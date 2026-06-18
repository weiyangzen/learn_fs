<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm.c -->
# sources/distributed-fs/ceph-client/net/mptcp/pm.c

## Purpose
Provides common MPTCP path-manager infrastructure shared by kernel and userspace PM implementations: address comparison/extraction helpers, ADD_ADDR retransmission state, PM event scheduling, subflow acceptance limits, RM_ADDR/subflow teardown, MP_PRIO/MP_FAIL handling, stale subflow detection, PM data initialization/reset, and path-manager registration.

## Important APIs, Types, and Functions
Address helpers include `mptcp_pm_addr_families_match()`, `mptcp_addresses_equal()`, `mptcp_local_address()`, and `mptcp_remote_address()`. Announcement state uses `struct mptcp_pm_add_entry`, `mptcp_pm_alloc_anno_list()`, `mptcp_pm_del_add_timer()`, and `mptcp_pm_add_timer()`. Event APIs include `mptcp_pm_new_connection()`, `mptcp_pm_fully_established()`, `mptcp_pm_subflow_established()`, `mptcp_pm_add_addr_received()`, `mptcp_pm_rm_addr_received()`, and `mptcp_pm_worker()`. Command helpers include `mptcp_pm_announce_addr()`, `mptcp_pm_remove_addr()`, `mptcp_pm_mp_prio_send_ack()`, `mptcp_pm_rm_subflow()`, and `mptcp_pm_mp_fail_received()`. Registration uses `mptcp_pm_register()`, `mptcp_pm_unregister()`, and `mptcp_pm_get_available()`.

## Control Flow
PM events set bits in `msk->pm.status` and schedule the MPTCP worker. The worker handles pending ADD_ADDR ACKs, RM_ADDR receives, and delegates kernel-specific work to `__mptcp_pm_kernel_worker()`. ADD_ADDR announcements are placed in an annotation list with retransmission timers; timer expiry re-announces with exponential delay up to `ADD_ADDR_RETRANS_MAX`, then triggers PM work to try further subflows. Incoming ADD_ADDR is either echoed, dropped, or queued for PM processing based on userspace/kernel mode, id0 validation, accept limits, and special C-flag handling. RM_ADDR and RM_SUBFLOW walk live subflows and close matching sockets. Stale detection marks subflows idle after repeated loss with no receive timestamp progress and reinjects pending data when alternatives exist.

## State and Persistence
State is per MPTCP socket in `msk->pm`: locks, status bits, announcement list, local/remote pending addresses, RM lists, counters, id bitmap, PM type, accept flags, work pending flag, and remote join-id0 denial. Global PM registry state is an RCU list protected by `mptcp_pm_list_lock`. Timers hold socket references and entries are freed by RCU.

## Dependencies and Integration Points
Depends on MPTCP protocol/socket internals, PM kernel/userspace backends, TCP sockets, timers, MIB counters, MPTCP events, and scheduler/work machinery. It integrates directly with `options.c` for option signaling and with `pm_kernel.c` for endpoint-driven behavior.

## Risks
Locking is subtle: many helpers require `msk->pm.lock`, while ACK sending temporarily drops it to lock subflow sockets. Timer cancellation/removal uses RCU to avoid freeing entries under concurrent callbacks. Counters for accepted addresses, extra subflows, and used local addresses must remain balanced across failures and removals. Userspace and kernel PM modes have different acceptance semantics. MP_FAIL disables new subflows and enters infinite-map fallback; mishandling can corrupt recovery behavior.

## Test Signals
Signals include ADD_ADDR retransmission/echo/drop counters, timer cancellation on echo/removal/destroy, userspace versus kernel PM behavior, subflow accept limits, RM_ADDR and RM_SUBFLOW close behavior, MP_PRIO send/receive events, MP_FAIL fallback handshake, stale subflow marking and recovery counters, PM registry sysctl available list, and lockdep/KASAN under concurrent PM events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm.c -->
