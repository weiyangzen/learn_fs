# sources/distributed-fs/lustre-release/lustre/ptlrpc/ptlrpcd.c

Purpose: implements PTLRPC daemon threads that own never-ending request sets for asynchronous RPCs, plus a dedicated recovery daemon so recovery can progress even if normal async threads are blocked.

Important APIs/types/functions: exported entry points are `ptlrpcd_wake()`, `ptlrpcd_add_req()`, `ptlrpcd_start()`, `ptlrpcd_stop()`, `ptlrpcd_free()`, `ptlrpcd_addref()`, and `ptlrpcd_decref()`. Internal state includes per-CPT `struct ptlrpcd`, per-thread `struct ptlrpcd_ctl`, global `ptlrpcds`, CPT index maps, recovery control `ptlrpcd_rcv`, and module parameters `max_ptlrpcds`, `ptlrpcd_bind_policy`, `ptlrpcd_per_cpt_max`, `ptlrpcd_partner_group_size`, and `ptlrpcd_cpts`.

Control flow: the first `ptlrpcd_addref()` initializes a recovery thread and per-CPT regular thread groups. Requests added through `ptlrpcd_add_req()` get job info packed into the request message, handle stale set membership, then route to the recovery thread if not in `LUSTRE_IMP_FULL` send state or to a round-robin CPT-local thread otherwise. Each daemon thread binds to its CPT, allocates a request set, initializes LU contexts, waits on the set waitqueue, moves new requests into active requests, runs `ptlrpc_check_set()`, frees completed requests, and can steal new work from partner threads in the same group. Stop marks flags, wakes the set, optionally aborts in-flight RPCs, drains, and frees set/partner state.

State/persistence: runtime-only thread, request-set, partner, CPT mapping, and user-reference state. `ptlrpcd_users` controls lazy startup/shutdown. No persistent storage exists.

Dependencies/integration: integrated with PTLRPC request sets, client resend/recovery, pinger async pings, events portal startup (`ptlrpcd_addref()`), LU context/session infrastructure, CPT binding/allocation, kernel kthreads, wait queues, and lprocfs-tuned module parameters.

Risks/test signals: daemon callbacks must not block on synchronous RPCs because they can deadlock recovery. Races around invalid request sets, stop/free ordering, partner stealing, and CPT subset parsing are high risk. Tests should cover addref/decref nesting, CPT pattern parsing, obsolete parameter translation, recovery-thread routing, normal round-robin routing, partner work stealing, forced stop aborts, request completion cleanup, and daemon behavior under timeout and LU environment refill failure.
