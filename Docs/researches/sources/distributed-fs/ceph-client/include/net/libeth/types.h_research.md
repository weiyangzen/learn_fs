# sources/distributed-fs/ceph-client/include/net/libeth/types.h

Purpose: Defines common libeth hotpath stats and XDP queue helper structures shared by receive and transmit support code.

Important APIs/types/functions: `libeth_rq_napi_stats`, `libeth_sq_napi_stats`, and `libeth_xdpsq_napi_stats` are compact NAPI-loop counters with named fields and flexible-array raw aliases for bulk operations. `libeth_xdpsq_lock` represents a spinlock plus sharing flag for shared XDP send queues. `libeth_xdpsq_timer` stores queue pointer, lock pointer, and delayed work for lazy cleanup of non-interrupt XDP queues. `libeth_xdp_buff_stash` stores just the necessary `xdp_buff` fields to resume partially built frames: data pointer, headroom, len, frame size, and flags.

Control flow: Drivers embed these structs in queue state and pass them to libeth helpers. Stats are updated in NAPI poll/completion loops. Shared XDPSQs use the lock wrapper. Lazy cleanup timers schedule delayed work to free stale XDP buffers when queues do not interrupt.

State and persistence: All state is per-driver-queue runtime state. There are no globals. The stash is transient between NAPI polls.

Dependencies/integration: Depends on workqueue and spinlock primitives and is consumed by libeth RX/TX/XDP helpers.

Risks: The raw flexible-array aliases assume exact field layout for aggregation; timer cleanup must coordinate with queue locking; stashed XDP fields must be sufficient and kept in sync with XDP expectations. Test signals include stats aggregation by raw arrays, shared vs unshared XDPSQ locking, lazy cleanup delayed work, partial XDP buffer stash/restore, and structure size/alignment checks from libeth cache assertions.
