# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_agent.c

## Purpose
This file manages HSM copytool agents registered with the MDT coordinator and sends selected HSM action batches to them. It tracks agent archive capabilities and load, converts active request lists into userspace kernel-comm HSM action lists, updates persistent llog records after dispatch, and provides a debugfs listing of registered agents.

## Important APIs, Types, And Functions
`mdt_hsm_agent_register()`, `mdt_hsm_agent_register_mask()`, and `mdt_hsm_agent_unregister()` maintain `coordinator::cdt_agents`. `mdt_hsm_agent_update_statistics()` adjusts per-agent request/success/failure counters. `mdt_hsm_find_best_agent()` chooses the least-loaded compatible agent for an archive. `mdt_hsm_agent_send()` validates a scan request, builds the outbound HAL, registers active in-memory requests, sends the request over the agent export reverse import, and modifies action llog records. `mdt_hsm_agent_modify_record()` persists status changes. `hsr_hal_size()` and `hsr_hal_copy()` size and fill the outbound `hsm_action_list`.

## Control Flow
Registration first obtains a coordinator reference, allocates a `hsm_agent`, copies archive ids, rejects duplicate UUIDs under `cdt_agent_lock`, links the agent, wakes the coordinator, and drops the reference. Agent selection scans registered agents under read lock, accepting archive-count zero as "all archives", and picks the lowest `ha_requests` count. Dispatch starts by choosing an agent; if no all-archive agent exists for archive zero remove requests, it can broadcast remove actions to all registered archive ids by adding fresh persistent records and marking the original records succeeded. Otherwise it revalidates each non-cancel request against current HSM state, removes invalid restore locks, builds a HAL excluding failed records, optionally registers active requests with `mdt_hsm_add_hsr()`, sends the packed kernelcomm message with `do_set_info_async()`, and finally updates/removes records and request counters.

## State And Persistence
Agent membership and counters are in-memory under `cdt_agent_lock`; persistent request state remains in the action llog and is changed through `mdt_hsm_agent_modify_record()`. Active requests are also registered in the coordinator request table by `mdt_hsm_add_hsr()` before dispatch. The outbound HAL is transient kernelcomm memory allocated by `kuc_alloc()`.

## Dependencies And Integration Points
The file integrates with coordinator reference management, request records from `mdt_hsm_cdt_requests.c`, HSM compatibility helpers from `mdt_coordinator.c`, llog modification, `obd_uuid_lookup()`, export lifecycle, and `LDLM_SET_INFO` reverse imports to clients running copytools. Its debugfs functions expose the registered-agent list and counters to operators.

## Risks
Agent selection is simple least-loaded scheduling and does not account for backend health beyond archive capability and export lookup. Dispatch has several race windows: objects can disappear between scan and send; agents can disconnect after selection; restore locks must be released for invalid restores; and llog status must remain consistent with in-memory request registration. Archive-zero remove broadcasting can produce duplicates after partial success because successfully reached archive ids are not persistently tracked. The archive mask path uses bit positions as archive ids plus one; very large archive ids are outside this mask representation.

## Test Signals
Look for HSM copytool registration/unregistration tests, duplicate UUID rejection, archive-mask registration, agent failover on disconnect or `-EPIPE`, request status transitions from waiting to started/succeeded/failed in debugfs, and remove-with-archive-zero behavior when only archive-specific agents are registered. Fault injection should cover reverse import failure, export eviction, incompatible HSM state, and `mdt_hsm_add_hsr()` failure.
