# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mcg.c

## Purpose
`mcg.c` implements SR-IOV multicast group paravirtualization for SA MCMember records. The master PF tracks multicast groups per demux port, consolidates VF join/leave requests into real SA requests, rewrites Port_GID to the master's real GID on the wire, fans responses back to the requesting VF with the VF's Port_GID restored, exposes group state through sysfs, and cleans VF memberships on shutdown.

## Important APIs, types, and functions
- `struct ib_sa_mcmember_data` is the packed MCMember record payload used in SA MAD data.
- `struct mcast_group` stores the group record, RB-tree node, mgid0 relocation list entry, per-VF membership and pending queues, state machine, last wire TID, response MAD, sysfs attribute, refcount, timeout work, and cleanup list.
- `struct mcast_member` stores each VF's join state, membership state, pending count, and request list.
- `struct mcast_req` stores queued VF SA MADs plus group/function list links and a cleanup marker.
- `mlx4_ib_mcg_multiplex_handler()` handles VF-origin MCMember SET/DELETE requests.
- `mlx4_ib_mcg_demux_handler()` handles wire-origin MCMember GET_RESP/DELETE_RESP responses.
- `mlx4_ib_mcg_work_handler()` is the central group state-machine worker.
- `mlx4_ib_mcg_timeout_handler()` handles SA response timeouts.
- `mlx4_ib_mcg_port_init()`, `mlx4_ib_mcg_port_cleanup()`, `clean_vf_mcast()`, `mlx4_ib_mcg_init()`, and `mlx4_ib_mcg_destroy()` manage per-port and global workqueues/state.

## Control flow
On a VF MCMember SET or DELETE, `mlx4_ib_mcg_multiplex_handler()` rejects requests while flushing, allocates a `mcast_req`, acquires or creates a group under `ctx->mcg_table_lock`, checks the per-VF pending limit, increments counters/refcounts, queues the request on both the group and VF lists, and schedules `mlx4_ib_mcg_work_handler()`.

The worker first processes any waiting SA response (`MCAST_RESP_READY`), validates the TID, cancels timeout work, updates the group record on success, reports failure status to the waiting VF when needed, and returns the group to `MCAST_IDLE`. It then processes pending requests while idle. Leave requests are validated against the VF's current join bits, immediately acknowledged to the VF, and update local membership counters. Join requests either complete locally if the PF is already a member for all requested bits and the record matches, or send a real SA join using `send_join_to_wire()` and transition to `MCAST_JOIN_SENT`. After pending requests, if local membership counters show the PF no longer needs some join bits, it sends a real SA leave and transitions to `MCAST_LEAVE_SENT`.

Wire responses enter `mlx4_ib_mcg_demux_handler()`. For normal MGIDs it finds the group by RB-tree lookup. For MGID zero joins, where the SM may allocate the MGID, it uses `search_relocate_mgid0_group()` to match by TID, update the group MGID, move the group from the temporary list into the RB-tree, and add sysfs exposure. The response is copied into the group, state becomes `MCAST_RESP_READY`, and the worker is queued.

Timeouts remove or fail the outstanding request depending on `MCAST_JOIN_SENT` or `MCAST_LEAVE_SENT`, potentially clear membership bits, release groups, reset state to idle, and reschedule the worker. Cleanup calls `clean_vf_mcast()` for each VF, queues synthetic clean leave requests for joined groups, waits briefly for the RB-tree to drain, flushes the MCG workqueue, then force-frees any remaining groups.

## State and persistence behavior
All state is runtime memory. Each demux context has an RB-tree keyed by MGID, a special list for MGID zero groups, and an ordered workqueue. Group membership is tracked as three membership counters plus per-VF join-state bitmasks. `refcount` intentionally represents queued requests, worker invocations, and real SA membership; release logic deletes sysfs attributes and removes RB-tree/list entries when it reaches zero. `last_req_tid` correlates wire responses and timeouts. Sysfs group files are transient diagnostics under the per-port MCG sysfs parent.

## Dependencies and integration points
`mcg.c` depends on ib_mad, ib_sa, ib_cache, rbtrees, workqueues, and mlx4_ib demux state. It sends wire MADs through `mlx4_ib_send_to_wire()` and VF replies through `mlx4_ib_send_to_slave()`, uses `dev->sm_ah` from `mad.c` to address the subnet manager, reads `demux->guid_cache[0]` for the real port GID, uses sysfs helpers declared in `mlx4_ib.h`, and is initialized/cleaned by SR-IOV demux setup in `mad.c` and module init in `main.c`.

## Risks and edge cases
- The group state machine is concurrency-sensitive: `mcg_table_lock`, per-group `lock`, delayed timeout work, normal work, cleanup work, and refcount releases must stay ordered.
- MGID zero relocation races with existing groups; collision handling silently drops the new temporary request and releases the group.
- `MAX_PEND_REQS_PER_FUNC` limits VF pressure, but note the condition uses `> MAX_PEND_REQS_PER_FUNC`, allowing one more than the literal maximum before rejecting.
- Cleanup may force-free groups after timeout if refcounts do not drain; this is defensive but can hide a leaked reference or queued work bug.
- TID rewriting and validation are required to avoid applying an SA response to the wrong group.
- `send_mad_to_slave()` assumes `sm_ah` is valid for `rdma_query_ah()` after only checking the send agent; callers rely on port-active ordering.
- Membership counters cover three low join-state bits; if protocol semantics expand, counter logic would need review.

## Test signals
- SR-IOV multicast tests should include VF joins/leaves for full, non-member, send-only, and overlapping join-state bits across multiple VFs.
- Exercise MGID zero allocation, SM failure statuses, wrong-TID responses, timeouts, and duplicate MGID collision during relocation.
- Verify per-VF pending limit behavior and cleanup of pending requests on VF shutdown.
- Confirm sysfs group attributes appear/disappear for nonzero MGIDs and show expected members/refcount/state.
- Run teardown tests with pending joins/leaves, delayed timeout work active, and `ctx->flushing` set.
