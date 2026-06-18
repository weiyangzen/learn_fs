# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/qp.c

## Purpose
`qp.c` manages mlx4 queue pair numbering, ICM allocation, lookup, state transitions, special QPs, QP update commands, and RoCE entropy calculation. It is shared by Ethernet, InfiniBand, RoCE, and SR-IOV code that needs to reserve QPNs, map QP context memory, drive firmware QP state machines, and dispatch asynchronous QP events.

## Important APIs, types, and functions
- Lifetime and events: `mlx4_qp_alloc()`, `mlx4_qp_remove()`, `mlx4_qp_free()`, `mlx4_qp_lookup()`, `mlx4_qp_event()`, and `mlx4_put_qp()`.
- State transitions: private `__mlx4_qp_modify()` and exported `mlx4_qp_modify()` plus convenience `mlx4_qp_to_ready()`.
- QPN reservation: `__mlx4_qp_reserve_range()`, `mlx4_qp_reserve_range()`, `__mlx4_qp_release_range()`, and `mlx4_qp_release_range()`.
- ICM mapping: `__mlx4_qp_alloc_icm()`, `mlx4_qp_alloc_icm()`, `__mlx4_qp_free_icm()`, and `mlx4_qp_free_icm()`.
- Table setup: `mlx4_create_zones()`, `mlx4_init_qp_table()`, `mlx4_cleanup_qp_table()`, `mlx4_CONF_SPECIAL_QP()`, and `mlx4_cleanup_qp_zones()`.
- Runtime mutation and query: `mlx4_update_qp()`, `mlx4_qp_query()`, and `mlx4_qp_roce_entropy()`.

## Control flow and integration
QP allocation starts with a QPN reserved from a zone or master resource command, maps all required ICM tables for that QPN, inserts the `struct mlx4_qp` into `dev->qp_table_tree`, and initializes reference/completion state. Async events look up the QP under `qp_table->lock`, take a reference, and call the QP's event callback, which is responsible for dropping the reference.

`__mlx4_qp_modify()` maps current/new state pairs to firmware commands. Reset-to-init also fills MTT base address and page size fields. RTR-to-RTS may compute RoCE v1/v2 entropy by querying the destination QPN. The command mailbox carries the optpar and context, and master devices also update internal QP0 active/proxy state when real or proxy QP0 moves to RTR, ERR, or RST.

QP reservation uses a zone allocator with separate general, RSS, and RAW_ETH/A0 steering areas. BlueFlame-capable Ethernet QPs avoid QPN bits 6 and 7 through `MLX4_BF_QP_SKIP_MASK`. Multi-function callers use wrapped `RES_QP` commands for reserve and ICM mapping. Initialization reserves special QPs, lays out proxy/tunnel SQPs for SR-IOV, creates zones, and configures the firmware special-QP base.

## State and persistence behavior
Runtime state includes `mlx4_priv(dev)->qp_table` locks, zone allocator, bitmaps, ICM tables, RDMARC base/shift from the profile, `dev->qp_table_tree`, special QP bases, and per-port proxy/tunnel QP values. Each `struct mlx4_qp` carries `qpn`, refcount, completion, and callback. Hardware-visible state is QP context, auxiliary/alternate/RDMARC/CMPT mappings, and firmware QP state. QPN reservations persist until explicitly released.

## Dependencies
The file depends on mlx4 command mailboxes, ICM table APIs, zone allocator and bitmap helpers, radix tree APIs, refcount/completion primitives, mlx4 capability fields, RoCE helpers such as `folded_qp()`, and SR-IOV physical capability state.

## Risks
- QP events and free rely on balanced refcounts; callbacks must call `mlx4_put_qp()` or `mlx4_qp_free()` can wait forever.
- State-transition command selection is table-driven; unsupported transitions correctly fail, but caller state tracking must stay synchronized with firmware.
- Zone layout for RSS/RAW_ETH/BlueFlame QPs is bit-mask sensitive. Off-by-one errors can allocate QPNs with forbidden bits or overlap reserved regions.
- Multi-function allocation masks unsupported flags before calling firmware; callers may believe a stronger allocation constraint was honored than hardware actually supports.
- Special QP and proxy/tunnel offsets affect port bring-up and SR-IOV management traffic.

## Test signals
Test QPN reserve/release with alignment, A0 steering, RSS, RAW_ETH, and BlueFlame flags; allocation/free with radix lookup and event dispatch; all valid QP state transitions plus invalid transition rejection; QP0/proxy QP0 state changes on master; `mlx4_update_qp()` capability gating for source-check, VLAN strip, rate limit, and QoS vport; and teardown leak checks for zones and ICM mappings.
