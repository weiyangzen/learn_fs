# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qp.h

## Purpose
`qp.h` declares the mlx5 QP resource table and the core QP/DCT/SQ/RQ/XRCD helper interface shared by `qp.c`, `qpc.c`, UMR, and related mlx5 IB modules. It is the local contract between verbs-level queue-pair code and mlx5 command/resource tracking code.

## Important APIs, types, and functions
- `struct mlx5_qp_table` stores the mlx5 event notifier, DCT `xarray`, spinlock, and radix tree used for QP/SQ/RQ resource lookup.
- `mlx5_init_qp_table()` and `mlx5_cleanup_qp_table()` initialize and unregister the resource/event infrastructure.
- `mlx5_qpc_create_qp()`, `mlx5_core_qp_modify()`, `mlx5_core_destroy_qp()`, `mlx5_core_qp_query()`, `mlx5_core_create_dct()`, `mlx5_core_destroy_dct()`, and `mlx5_core_dct_query()` expose mlx5 command operations for transport QPs and DCTs.
- `mlx5_core_create_rq_tracked()`, `mlx5_core_destroy_rq_tracked()`, `mlx5_core_create_sq_tracked()`, and `mlx5_core_destroy_sq_tracked()` expose event-tracked raw RQ/SQ creation and destruction.
- `mlx5_core_res_hold()` and `mlx5_core_res_put()` provide refcounted lookup/release for event resources.
- `mlx5_core_set_delay_drop()` exposes the firmware command for delay-drop receive queues.
- `mlx5_core_xrcd_alloc()` and `mlx5_core_xrcd_dealloc()` manage XRCD numbers.
- `mlx5_ib_qp_set_counter()`, `mlx5_ib_qp_event_init()`, `mlx5_ib_qp_event_cleanup()`, and `mlx5r_ib_rate()` are exported helpers implemented in `qp.c`.

## Control flow
Other mlx5 IB files include this header when they need to create or destroy tracked QP-like resources, query or modify QPs, hold event resources during asynchronous callbacks, or allocate XRCDs. The table is initialized during device setup, used by resource creation paths to publish objects, and cleaned up on device teardown.

## State and persistence
The header itself stores no state, but it defines the structure that persists QP resource lookup state inside `struct mlx5_ib_dev`. The radix tree and DCT xarray back asynchronous event dispatch and protect resources with explicit refcounts and completions.

## Dependencies and integration points
It depends on `struct mlx5_ib_dev`, mlx5 core QP/DCT types, RDMA counter and QP types, xarray, radix tree, notifier blocks, and spinlocks. It is tightly coupled with `qpc.c` for implementation and with `qp.c` for verbs-level usage.

## Risks
- The resource table layout is consumed by asynchronous event code; changing it affects locking and lifetime rules.
- APIs mix QP, raw SQ/RQ, DCT, XRCD, and counter operations. Callers must choose the helper that matches the hardware object type.
- `mlx5_core_res_hold()`/`put()` require strict pairing because event handlers can otherwise race destroy paths.

## Test signals
- Compile coverage should ensure all prototypes remain consistent with `qp.c`, `qpc.c`, and UMR callers.
- Event-injection or fault tests should validate that QP/SQ/RQ/DCT resources can be looked up, refcounted, and released during destroy races.
- XRCD and delay-drop users should verify command wrappers still pass correct IDs and UID fields after signature changes.
