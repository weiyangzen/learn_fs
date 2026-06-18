# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/qp.c

## Purpose
`qp.c` is the central rdmavt queue-pair implementation shared by software verbs transports such as hfi1/qib-style providers. It owns QP number allocation, QP hash-table membership, QP create/modify/query/destroy verbs, send and receive posting, shared receive queue posting, RC retry/RNR timers, receive-WQE extraction, send completion advancement, SGE copy heuristics, and connected loopback for local RC/UC traffic.

## Important APIs, types, and functions
The exported surface includes `ib_rvt_state_ops`, `rvt_driver_qp_init()`, `rvt_qp_exit()`, `rvt_create_qp()`, `rvt_modify_qp()`, `rvt_destroy_qp()`, `rvt_query_qp()`, `rvt_post_recv()`, `rvt_post_send()`, `rvt_post_srq_recv()`, `rvt_get_rwqe()`, `rvt_comm_est()`, `rvt_rc_error()`, timer helpers, `rvt_qp_iter*()`, `rvt_send_complete()`, `rvt_copy_sge()`, and `rvt_ruc_loopback()`. Internal helpers manage QPN bitmap pages, driver-private QP allocation hooks, MR reference cleanup, UD address-handle attribute caching, and send queue reservation accounting. `struct rvt_qp`, `struct rvt_swqe`, `struct rvt_rq`, `struct rvt_krwq`, `struct rvt_rwq`, `struct rvt_sge_state`, and `struct rvt_wss` are the dominant state carriers.

## Control flow
Driver registration calls `rvt_driver_qp_init()` to allocate a QP hash table and initialize the QPN bitmap, including provider-reserved QPN ranges. `rvt_create_qp()` validates core capabilities, allocates send/receive queues, creates mmap metadata for user receive queues, initializes timers and locks, calls provider QP-private hooks, allocates a QPN, and returns mmap offsets to userspace when applicable. QPs enter the lookup table when transitioning from RESET to INIT in `rvt_modify_qp()`.

Send posting takes `s_hlock`, validates opcode support through `rdi->post_parms`, validates SGEs and lkeys, executes or queues local operations, computes PSN ranges, lets the provider finish WQE setup, updates queue head with a write barrier, and schedules or directly invokes the send engine. Receive posting writes RWQEs into a kernel or user-mapped ring. Receive consumption validates user-controlled head/tail values before using them, initializes SGEs, emits local protection errors for bad lkeys, and triggers SRQ limit events. Error/reset paths stop timers, notify providers, drain queues, drop MR refs, remove QPs from RCU lookup tables, and emit last-WQE events when needed.

## State and persistence
All persistent runtime state is in memory: QPN bitmaps, QP hash buckets, queue indices, MR references, timers, retry counters, PSNs/MSNs, pending mmap records, and port counters. User-mapped receive queues make ring indices user-visible, so the code repeatedly sanitizes head/tail values and uses RDMA UAPI atomic accessors. The working-set-size heuristic tracks destination pages atomically to choose cacheless copy behavior for large SGE copies. QPNs and object counts are released only after QP reset, RCU removal, and refcount drain.

## Dependencies and integration points
The file integrates with the RDMA core verbs ABI, rdmavt provider hooks in `rvt_dev_info.driver_f`, CQ/MR/AH/mmap/mcast helpers, RCU lookup, timers/hrtimers, tracepoints, OPA address validation, and user copy helpers. Providers supply send scheduling, PMTU translation, QP private allocation, reset/error notifications, and optional QPN allocation.

## Risks
The highest-risk areas are lock ordering across `r_lock`, `s_hlock`, and `s_lock`; user-writable queue indices; MR reference lifetime while deregistration races active QPs; reset/error paths that temporarily drop locks; and timer callbacks running while QPs are being destroyed. `rvt_ruc_loopback()` combines requester and responder state, remote-key validation, atomics, local invalidation, receive completions, RNR retry handling, and RC error transition in one path, making regression tests important. QPN bitmap allocation depends on provider QPN increments, reserved ranges, AIP prefixes, and QoS bit assumptions.

## Test signals
Useful signals include QP lifecycle tests for all supported QP types, QPN reuse and reserved ranges, post-send/post-recv validation, user mmap receive queues with corrupt head/tail values, MR deregistration while WQEs reference lkeys, RC timeout/RNR retry behavior, SRQ limit events, loopback SEND/RDMA/atomic/local-invalidate flows, SQ drain and last-WQE events, and build coverage with lockdep, KASAN, and tracepoint compilation enabled.
