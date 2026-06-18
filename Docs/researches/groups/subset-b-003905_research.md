# Research: subset-b-003905

Grouped research for InfiniBand core agent, cache, cgroup, connection manager, CM message helper, and CM trace files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/agent.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/agent.c

## Purpose

`agent.c` implements the lightweight MAD agent support used by the InfiniBand core to send management responses on SMI and GSI QPs. It maintains a global list of per-device/per-port agent registrations and exposes helpers to open/close those registrations and to transmit response MADs back to the requester.

## Important APIs, Types, And Functions

- `struct ib_agent_port_private` stores list linkage and two optional MAD agents: `agent[0]` for `IB_QPT_SMI` and `agent[1]` for `IB_QPT_GSI`.
- `ib_agent_port_open()` allocates the private object and conditionally registers send-only MAD agents based on `rdma_cap_ib_smi()` and `rdma_cap_ib_cm()`.
- `ib_agent_port_close()` removes a port from the global list, unregisters any registered agents, and frees the private object.
- `agent_send_response()` locates the right registered agent, creates an AH from the receive WC/GRH, creates a send MAD, copies the supplied response header/body, and posts it.
- `agent_send_handler()` is the send-completion callback; it destroys the AH and frees the send MAD.

## Control Flow

Open flow: allocate `port_priv`, register SMI agent if supported, register GSI agent if supported, then append the object to `ib_agent_port_list` under `ib_agent_port_list_lock`. Error paths unwind GSI then SMI registration before freeing the object.

Send flow: `agent_send_response()` resolves the port entry by device and either real port or port 0 for switch devices. It selects the agent by `qpn`, creates an AH from the incoming WC, adjusts OPA response length for non-OPA base versions, creates a send MAD with the incoming source QP and P_Key index, copies the response payload, records the AH, fixes the internal send WR port for switch devices, and posts through `ib_post_send_mad()`. Failed post or allocation frees the send buffer and AH.

Close flow: remove the port entry from the global list while holding the spinlock, then unregister agents outside the lock and free memory.

## State And Persistence

All state is in kernel memory. The global list `ib_agent_port_list` is protected by `ib_agent_port_list_lock`. Each send allocates a transient `ib_mad_send_buf` and AH; ownership transfers to the MAD layer on successful post and returns via `agent_send_handler()`. There is no on-disk persistence or user-visible configuration.

## Dependencies And Integration Points

This file depends on the RDMA MAD layer (`ib_register_mad_agent()`, `ib_create_send_mad()`, `ib_post_send_mad()`), AH helpers (`ib_create_ah_from_wc()`, `rdma_destroy_ah()`), and capability helpers (`rdma_cap_ib_switch()`, `rdma_cap_ib_smi()`, `rdma_cap_ib_cm()`). It is integrated with SMI/GSI management paths that need to synthesize replies, including OPA-aware response sizing.

## Risks

- `qpn` is used as an index into a two-element array; callers must pass only 0 or 1.
- The lookup returns a port object after dropping the global spinlock. Correctness depends on lifecycle ordering that prevents concurrent close from freeing an entry while a sender still uses it.
- Switch devices use port 0 for registration lookup but later override the send WR port; regressions here can route responses out the wrong port.
- OPA response length normalization must preserve legacy MAD length expectations for non-OPA management base versions.

## Test Signals

Useful signals include MAD response success for SMI and GSI, correct AH teardown on send completion and post failure, error logs for missing port agents or AH/send allocation failures, and switch-device tests that validate response port override. Kernel tests or fault injection should cover partial registration failure and close-after-open cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/agent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/agent.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/agent.h

## Purpose

`agent.h` is the small internal interface for the InfiniBand core MAD response agent implemented in `agent.c`. It declares lifecycle entry points for per-port agent registration and the response send helper.

## Important APIs, Types, And Functions

- `ib_agent_port_open(struct ib_device *device, int port_num)` registers per-port send-only MAD agents where supported.
- `ib_agent_port_close(struct ib_device *device, int port_num)` tears down the previously opened agents.
- `agent_send_response(...)` sends a prepared MAD response using receive-side routing information, device/port identity, QP selector, response length, and OPA mode.

## Control Flow

The header has no executable control flow. It defines an include guard, imports `<linux/err.h>` and `<rdma/ib_mad.h>`, and exposes function prototypes consumed by other InfiniBand core modules.

## State And Persistence

No state is defined here. State is owned by `agent.c` and the RDMA MAD subsystem.

## Dependencies And Integration Points

The prototypes bind this module to `struct ib_device`, `struct ib_mad_hdr`, `struct ib_grh`, and `struct ib_wc`. Callers must already understand MAD header formats, receive completions, and whether the response is OPA-specific.

## Risks

- The `qpn` parameter in `agent_send_response()` is not type-safe; the implementation expects an SMI/GSI array index.
- The header exposes raw pointers and lengths, so callers must ensure `resp_mad_len` matches the payload actually available at `mad_hdr`.

## Test Signals

Build coverage is the primary signal for this header. Runtime coverage comes from callers successfully opening/closing agent ports and sending responses through both SMI and GSI paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/agent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cache.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cache.c

## Purpose

`cache.c` maintains RDMA core caches for port attributes, P_Keys, subnet prefixes, port state, and GID table entries. It supports InfiniBand, RoCE, and iWARP behavior, handles default RoCE GIDs tied to net devices, exports lookup/query APIs to other RDMA components, and synchronizes cache updates before dispatching asynchronous events to clients.

## Important APIs, Types, And Functions

- `struct ib_pkey_cache` stores a cached P_Key table.
- `struct ib_gid_table` owns per-port GID entries, a mutex for writers, an IRQ-safe rwlock for table readers, and a bitmap of reserved default GID indices.
- `struct ib_gid_table_entry` wraps `struct ib_gid_attr`, refcounting, delete work, provider context, entry state, and a retained netdevice pointer for RCU-safe release.
- GID mutation APIs: `ib_cache_gid_add()`, `ib_cache_gid_del()`, `ib_cache_gid_del_all_netdev_gids()`, `ib_cache_gid_set_default_gid()`.
- GID lookup/query APIs: `rdma_find_gid_by_port()`, `rdma_find_gid_by_filter()`, `rdma_find_gid()`, `rdma_query_gid()`, `rdma_get_gid_attr()`, `rdma_query_gid_table()`, `rdma_put_gid_attr()`, `rdma_hold_gid_attr()`, `rdma_read_gid_hw_context()`, `rdma_read_gid_attr_ndev_rcu()`, `rdma_read_gid_l2_fields()`.
- P_Key and port cache APIs: `ib_get_cached_pkey()`, `ib_find_cached_pkey()`, `ib_get_cached_lmc()`, `ib_get_cached_port_state()`, `ib_get_cached_subnet_prefix()`.
- Lifecycle/event APIs: `ib_cache_setup_one()`, `ib_cache_cleanup_one()`, `ib_cache_release_one()`, and `ib_dispatch_event()`.

## Control Flow

GID setup allocates one `ib_gid_table` per port, reserves leading entries for supported RoCE default GID types, enables GID updates, and triggers a RoCE rescan. Initial cache setup then calls `ib_cache_update()` per port to query port attributes, load non-RoCE GIDs from the provider, and refresh P_Key tables.

GID add flow rejects zero GIDs, locks the table mutex, uses `find_gid()` to detect duplicates and locate an empty slot that matches default/non-default policy, fills device/index/port/gid fields in the attribute, and calls `add_modify_gid()`. For RoCE, `add_modify_gid()` calls provider `ops.add_gid()` before storing the entry. Successful changes dispatch `IB_EVENT_GID_CHANGE`.

GID delete flow locks the table mutex, finds a matching valid entry, marks it `PENDING_DEL`, clears the slot immediately for non-RoCE, calls provider `ops.del_gid()` if applicable, detaches any netdev pointer through RCU, drops the entry reference, and dispatches a GID change event.

Lookup flow uses the table rwlock. Functions that return `struct ib_gid_attr *` increment the entry kref under the read lock and require `rdma_put_gid_attr()` by the caller. Table scans skip invalid and pending-delete entries.

Event flow uses `ib_dispatch_event()` to allocate `ib_update_work` in atomic context and queue it to `ib_wq`. Cache-affecting events run `ib_cache_event_task()`, which refreshes the software cache before redispatching non-GID events to clients. Generic events are simply forwarded.

Cleanup flow disables GID updates, flushes the shared workqueue, deletes valid GID entries, flushes again for delayed GID free work, and later frees P_Key and GID table storage during release.

## State And Persistence

All state is in `ib_device->port_data[port].cache` and per-port GID table allocations. P_Key cache replacement is protected by `device->cache_lock`; old P_Key tables are freed after the write-side swap. GID entries use `kref` plus workqueue-delayed freeing so returned attributes can outlive deletion from the table. Netdevice references are held with `dev_hold()` and released using `call_rcu()` to protect readers of `attr.ndev`.

There is no durable persistence. The cache is reconstructed from provider queries, netdev/RoCE rescans, and asynchronous events.

## Dependencies And Integration Points

The file integrates with provider operations `query_gid`, `add_gid`, `del_gid`, `ib_query_port()`, and `ib_query_pkey()`. It relies on RDMA core capability helpers, RoCE netdev/GID helpers, Linux netdevice/VLAN APIs, RCU, workqueues, and RDMA security hooks (`ib_security_cache_change()`). Exported symbols are used by CM, CMA, verbs, uverbs, and providers needing source GID/P_Key/port-state information.

## Risks

- GID lifetime is subtle: readers must balance every returned `ib_gid_attr` with `rdma_put_gid_attr()`, and release paths warn on leaked refs.
- Writers require a sleepable context because provider `add_gid`/`del_gid` may sleep; using the mutation API from atomic context would be unsafe.
- RoCE GID deletion leaves slots pending until references drain, unlike non-RoCE immediate slot reuse. Incorrect assumptions can cause duplicate or stale entries.
- Netdevice pointers require RCU discipline. Callers of `rdma_read_gid_attr_ndev_rcu()` must hold an RCU read lock and handle `ERR_PTR`.
- `rdma_query_gid_table()` returns `-EINVAL` if `max_entries` is too small, so uverbs callers need a correct sizing/retry strategy.
- Cache update failures during initial setup trigger GID cleanup but leave correctness dependent on lifecycle ordering during device registration/removal.

## Test Signals

Useful signals include add/delete/find GID round trips for default and non-default RoCE GIDs, refcount leak warnings at release, correct `IB_EVENT_GID_CHANGE` dispatch, P_Key preference for full membership over partial membership, VLAN/source-MAC extraction for upper/lower netdev topologies, provider add/delete failure injection, and teardown tests that flush workqueue paths without use-after-free. Event tests should verify that cache state is updated before clients receive non-GID cache events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cgroup.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cgroup.c

## Purpose

`cgroup.c` connects RDMA devices and RDMA resource objects to the kernel RDMA cgroup controller. It provides device registration/unregistration and exported charge/uncharge helpers for RDMA resource accounting.

## Important APIs, Types, And Functions

- `ib_device_register_rdmacg()` sets `device->cg_device.name` and registers the RDMA cgroup device.
- `ib_device_unregister_rdmacg()` unregisters the RDMA cgroup device.
- `ib_rdmacg_try_charge()` charges a resource of type `enum rdmacg_resource_type` to an `ib_rdmacg_object` and device cgroup object.
- `ib_rdmacg_uncharge()` releases a prior charge.

## Control Flow

Device registration is expected before exposing the RDMA device to user space, so user allocations cannot bypass accounting. Unregistration is expected after user-triggered allocations are impossible and resources are deallocated. Per-object charge/uncharge calls delegate directly to `rdmacg_try_charge()` and `rdmacg_uncharge()`.

## State And Persistence

The file stores no private state. It writes the RDMA cgroup device name into `device->cg_device` and relies on the cgroup core for accounting state. Accounting is runtime-only and tied to device/resource lifetimes.

## Dependencies And Integration Points

The file includes `core_priv.h` for RDMA core internals and depends on the kernel RDMA cgroup API. The charge helpers are exported for consumers that allocate/deallocate RDMA resources and need cgroup enforcement.

## Risks

- Registering too late can allow unaccounted allocations; unregistering too early can strand accounting state or allow post-unregister allocation paths.
- Callers must pair successful charges with uncharges using the same device and resource index.
- `ib_rdmacg_try_charge()` can fail, and allocation paths must propagate or unwind that failure.

## Test Signals

Signals include cgroup limit enforcement for RDMA resources, no accounting leaks after resource teardown, correct failures when limits are exceeded, and lifecycle tests confirming registration precedes user exposure and unregistration follows resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cm.c

## Purpose

`cm.c` implements the InfiniBand Connection Manager. It creates/listens/destroys CM IDs, sends and receives CM MADs, drives the connection state machine for REQ/REP/RTU/DREQ/DREP/REJ/MRA/LAP/APR/SIDR messages, assists QP state transitions, tracks duplicate/stale connections through timewait tables, registers MAD agents per CM-capable port, and exposes per-port CM counters in sysfs.

## Important APIs, Types, And Functions

- Public lifecycle and connection APIs: `ib_create_cm_id()`, `ib_destroy_cm_id()`, `ib_cm_listen()`, `ib_cm_insert_listen()`, `ib_send_cm_req()`, `ib_send_cm_rep()`, `ib_send_cm_rtu()`, `ib_send_cm_dreq()`, `ib_send_cm_drep()`, `ib_send_cm_rej()`, `ib_prepare_cm_mra()`, `ib_send_cm_sidr_req()`, `ib_send_cm_sidr_rep()`, `ib_cm_notify()`, `ib_cm_init_qp_attr()`, and `ibcm_reject_msg()`.
- Global `struct ib_cm cm` owns locks, device list, listener tree, remote ID/QP/SIDR trees, local ID xarray, random ID operand, timewait list, and CM workqueue.
- `struct cm_id_private` extends `struct ib_cm_id` with locks, refcount/completion, message pointer, AVs, private data, QP parameters, timeout/retry fields, queued work, timewait state, and ECE data.
- `struct cm_device` and `struct cm_port` represent a registered IB device and per-port MAD agents/counters.
- `struct cm_work` carries received MAD work, local/remote IDs, event payload, and optional path records.
- `struct cm_timewait_info` indexes remote IDs/QPNs and later becomes a delayed work item for timewait exit.

## Control Flow

Module init initializes global locks/trees/xarray, randomizes the local ID operand, creates `cm.wq`, and registers `cm_client`. `cm_add_one()` attaches to each CM-capable port, registers sysfs counter groups, creates a receive-capable GSI MAD agent and a send-only reply agent, sets the port CM capability bit, and links the `cm_device` into the global device list. Remove marks the device `going_down`, flushes queued work, nulls MAD agents under `mad_agent_lock`, unregisters agents/counters, and drops the device reference.

ID creation allocates `cm_id_private`, initializes state as `IB_CM_IDLE`, allocates a cyclic 32-bit local ID from the xarray, XORs it with `cm.random_id_operand`, and finalizes it into `cm.local_id_table` unless it is a shared listener created by `ib_cm_insert_listen()`. ID destruction is state-aware: listeners are removed from the listener tree, pending sends are cancelled, active connections may send REJ or DREQ, established IDs enter timewait when appropriate, SIDR requests may be rejected, queued work is drained, AVs/private data are destroyed, and final free uses RCU after the refcount completion.

Outbound active connection flow starts in `ib_send_cm_req()`: validate request parameters, create timewait info, build primary and optional alternate AVs from SA path records, fill local state and timeouts, allocate a tracked MAD send buffer, format a REQ, post it, and move to `IB_CM_REQ_SENT`. REP receipt validates state, inserts remote ID and remote QPN into duplicate/stale detection tables, fills remote QP and responder parameters, cancels the REQ send, moves to `IB_CM_REP_RCVD`, and queues a callback. `ib_send_cm_rtu()` then sends RTU and moves to `IB_CM_ESTABLISHED`.

Passive connection flow starts in `cm_req_handler()`: allocate a new CM ID for the incoming REQ, initialize response AV from the receive WC/GRH, create timewait info, set `IB_CM_REQ_RCVD`, use remote ID/QPN trees to reject duplicates/stale connections, find a matching listener, parse primary/alternate paths, rebuild AVs by path, finalize the new ID into the xarray, and deliver `IB_CM_REQ_RECEIVED` to the listener's handler. `ib_send_cm_rep()` replies and moves to `IB_CM_REP_SENT`; incoming RTU moves to `IB_CM_ESTABLISHED`.

Disconnect flow uses `ib_send_cm_dreq()` to send tracked DREQ from established state and move to `IB_CM_DREQ_SENT`; incoming DREQ cancels applicable outstanding messages, moves to `IB_CM_DREQ_RCVD`, and queues a callback. `ib_send_cm_drep()` enters timewait and sends DREP. Incoming DREP for a DREQ moves to timewait and cancels the outstanding send. Duplicate DREQs may elicit direct DREP responses.

MRA/REJ flow adjusts timeouts or terminates state. `ib_prepare_cm_mra()` moves pending received REQ/REP/LAP work into MRA-sent states. `cm_mra_handler()` extends tracked MAD timeouts and queues MRA events. `cm_send_rej_locked()` resets to idle or enters timewait depending on state; `cm_rej_handler()` mirrors that for received rejects and delivers an event.

SIDR flow uses `ib_send_cm_sidr_req()` for service ID resolution without normal connection timewait/xarray receive state. Incoming SIDR requests create a temporary CM ID indexed by remote request ID and SLID to suppress duplicates, find a listener, call its handler directly, and expect `ib_send_cm_sidr_rep()` to send the response and erase the SIDR tree entry. SIDR replies cancel the tracked request and deliver an event.

LAP/APR alternate path flow is unsupported on RoCE. Incoming LAP parses alternate path information, updates AV state, and queues a LAP event if the connection is established and LAP state allows it. APR replies reset LAP state to idle and cancel outstanding LAP sends.

MAD receive flow maps CM MAD attribute IDs to `ib_cm_event_type`, allocates `cm_work` with enough path records, increments receive counters, and queues the work unless the device is going down. Send completions update transmit/retry counters and call `cm_process_send_error()` for tracked sends. User callbacks are serialized per CM ID by `work_count` and `work_list` in `cm_queue_work_unlock()`/`cm_process_work()`.

`ib_cm_init_qp_attr()` synthesizes QP attributes for INIT/RTR/RTS from CM state: P_Key index, port, access flags, AH/path MTU/destination QPN/PSN, responder/initiator depths, retry/RNR settings, timeout, and alternate path migration fields.

## State And Persistence

All state is in memory. The global CM state uses `cm.lock` for listener and remote/timewait structures, `cm.device_lock` for the device list, `cm.local_id_table` for local ID lookup under RCU, and `cm.wq` for serialized asynchronous handling. Each CM ID has its own spinlock and refcount; tracked send MADs hold an extra CM ID reference until completion or cancellation. Timewait state persists only until the delayed work fires or the device/ID is destroyed.

Private data is copied for RTU/DREP or reused for duplicate replies. AVs hold references to `cm_device` through their `cm_port`; `cm_destroy_av()` releases those references. Sysfs counters are atomic per port and grouped as transmitted messages, transmit retries, received messages, and received duplicates.

## Dependencies And Integration Points

`cm.c` depends on the RDMA MAD layer, AH/path record helpers, GID/P_Key cache APIs from `cache.c`, CM message field accessors from `cm_msgs.h` and IBTA field definitions, tracepoints from `cm_trace.h`, RDMA device client registration, sysfs port attribute groups, workqueues, xarray, rbtree, RCU, and low-level port modification. It is consumed by upper-layer RDMA protocols that use `struct ib_cm_id` callbacks and QP initialization helpers.

## Risks

- The state machine is broad and lock-sensitive. Regressions can cause invalid transitions, duplicate callbacks, missed cancellations, or leaked references.
- Listener sharing only works for matching handlers with no context; misuse returns existing IDs or errors in subtle ways.
- Remote duplicate/stale detection depends on correct insertion/removal of remote ID and remote QPN timewait nodes.
- Destroy paths can send protocol messages and wait for references; incorrect timeout or refcount handling can lead to hangs, warnings, or use-after-free.
- Direct retry response messages use special context and are freed differently from tracked private messages.
- Device removal races are mitigated by `going_down`, workqueue flushes, and `mad_agent_lock`; any new queueing path must honor those gates.
- Path handling includes IB, RoCE, OPA extended LIDs, permissive LIDs, SGID attributes, and alternate paths. Small field conversion mistakes can break interoperability.
- QP attribute helpers expose live AH objects by value; callers must use them only in states accepted by CM and avoid assuming alternate path support on RoCE.

## Test Signals

High-value signals include full active/passive RC connection handshakes, rejection paths for invalid service IDs/GIDs/alternate paths, duplicate REQ/REP/DREQ/MRA behavior, stale connection timewait behavior, SIDR request/reply success and duplicate suppression, LAP/APR behavior on IB and rejection on RoCE, send-completion error events for REQ/REP/DREQ/SIDR, CM sysfs counter increments, QP INIT/RTR/RTS attribute generation, listener sharing semantics, and device removal while work and MAD sends are outstanding. Tracepoints in `cm_trace.h` provide detailed observability for these cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_msgs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_msgs.h

## Purpose

`cm_msgs.h` provides small inline helpers and constants for interpreting and formatting InfiniBand CM MAD fields. It centralizes QP type encoding/decoding and REP QPN extraction over the packed IBTA message structures.

## Important APIs, Types, And Functions

- `IB_CM_CLASS_VERSION` defines CM class version 2, matching IB specification 1.2 behavior used by `cm.c`.
- `cm_req_get_qp_type()` decodes the REQ transport service type and extended transport type into `IB_QPT_RC`, `IB_QPT_UC`, or `IB_QPT_XRC_TGT`.
- `cm_req_set_qp_type()` writes REQ transport fields for UC, XRC initiator, or default RC.
- `enum cm_msg_response` identifies whether a MRA or REJ is responding to REQ, REP, or another message class.
- `cm_rep_get_qpn()` returns the local QPN field for normal QPs or the local EE context number for XRC initiator flows.

## Control Flow

The helpers are inline switch/field-access routines. They use `IBA_GET()` and `IBA_SET()` macros from the IBTA field definitions and keep values in the network-byte-order conventions expected by CM message structs.

## State And Persistence

No state is stored. The header only transforms fields in caller-owned CM message buffers.

## Dependencies And Integration Points

The header depends on `<rdma/ibta_vol1_c12.h>`, `<rdma/ib_mad.h>`, and `<rdma/ib_cm.h>`. `cm.c` uses it to format REQs, decode incoming REQs, decide QP behavior, and parse REP QPN/EECN fields.

## Risks

- Unsupported or malformed transport encodings return 0, so callers must treat that as invalid.
- XRC initiator/target naming is direction-sensitive: REQ encoding for `IB_QPT_XRC_INI` is later decoded on the peer as `IB_QPT_XRC_TGT`.
- REP QPN extraction must match QP type or XRC connections can use the wrong endpoint identifier.

## Test Signals

Signals include unit-style validation of REQ transport field encodings for RC, UC, and XRC; malformed transport type rejection by CM request handling; and REP parsing tests for normal QP versus XRC EECN fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_msgs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_trace.c

## Purpose

`cm_trace.c` is the tracepoint instantiation unit for the InfiniBand/RDMA Connection Manager trace events declared in `cm_trace.h`.

## Important APIs, Types, And Functions

- Defines `CREATE_TRACE_POINTS` before including `cm_trace.h`, causing the tracepoint definitions to be emitted exactly once.
- Includes `<rdma/rdma_cm.h>` and `"cma_priv.h"` before the trace header so trace helper types and formatting helpers are visible.

## Control Flow

There is no runtime logic beyond compilation of tracepoint definitions. The file participates in the kernel tracepoint build pattern: declarations live in the header, and one C file defines `CREATE_TRACE_POINTS`.

## State And Persistence

No private state is stored. Tracepoint enablement and buffers are managed by the kernel tracing subsystem.

## Dependencies And Integration Points

This file integrates `cm_trace.h` with ftrace/perf/eBPF tracing infrastructure. It is required so `trace_icm_*` calls in `cm.c` link to real tracepoint objects.

## Risks

- If this file is omitted from the build or `CREATE_TRACE_POINTS` is duplicated elsewhere, tracepoint linkage will fail.
- Include ordering must continue to satisfy helper dependencies used by the trace header.

## Test Signals

Build/link success is the primary signal. Runtime signals include the presence of `ib_cma` trace events under tracing infrastructure and successful capture of CM events emitted by `cm.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_trace.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_trace.h

## Purpose

`cm_trace.h` declares tracepoints for the InfiniBand Connection Manager. The events expose CM ID state, LAP state, reject reasons, send/receive anomalies, MAD send failures, and QP initialization errors for debugging and observability.

## Important APIs, Types, And Functions

- `TRACE_SYSTEM ib_cma` names the trace event subsystem.
- `IB_CM_STATE_LIST`, `IB_CM_LAP_STATE_LIST`, and `IB_CM_REJ_REASON_LIST` define enum-to-string mappings using `TRACE_DEFINE_ENUM()` and `__print_symbolic()`.
- `DECLARE_EVENT_CLASS(icm_id_class)` captures CM ID pointer, local ID, remote ID, CM state, and LAP state.
- `DEFINE_CM_SEND_EVENT()` emits send events for REQ, REP, duplicate REQ/REP, RTU, MRA, SIDR, DREQ, and DREP.
- `TRACE_EVENT(icm_send_rej)` records reject sends with a symbolic reject reason.
- Error event classes cover establish, no-listener, DREQ unknown, MRA unknown, QP INIT/RTR/RTS errors, stale connection, missing private state, unknown handlers, and MAD send completion failures.
- The footer sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` for the kernel trace header generator.

## Control Flow

The header uses standard Linux tracepoint macros. At compile time, it defines enum mappings and event structures. At runtime, `trace_icm_*()` callsites in `cm.c` populate fixed event fields and print symbolic state/reason/status strings when tracing is enabled.

## State And Persistence

The header declares trace event schemas, not durable state. Event records are transient in kernel tracing buffers. It intentionally stores pointer values for eBPF correlation plus integer IDs/states for stable decoding.

## Dependencies And Integration Points

It includes `<linux/tracepoint.h>`, `<rdma/ib_cm.h>`, and `<trace/misc/rdma.h>`. `cm.c` depends on the generated `trace_icm_*` helpers. Tracing tools consume the `ib_cma` event namespace to diagnose CM state transitions and failures.

## Risks

- Enum lists must stay synchronized with public RDMA CM enums; missing values degrade trace readability.
- Trace payloads must avoid dereferencing freed CM IDs. Current callsites pass live IDs while holding appropriate references or locks.
- The relative `TRACE_INCLUDE_PATH` must match the source tree layout for trace generation.
- Event fields are part of observability contracts for scripts; renaming events or fields can break external tooling.

## Test Signals

Signals include successful trace header generation, visible `ib_cma:*` events, symbolic rendering of CM states/LAP states/reject reasons/WC statuses, and trace output during CM handshakes, duplicate handling, REJ/MRA paths, send errors, and QP attribute failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/cm_trace.h -->
