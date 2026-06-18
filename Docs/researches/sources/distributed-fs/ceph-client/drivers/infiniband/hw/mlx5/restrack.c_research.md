# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/restrack.c

## Purpose
`restrack.c` registers mlx5-specific RDMA resource tracking callbacks. It enriches RDMA netlink resource dumps with raw mlx5 hardware resource data, ODP memory-region statistics, ODP mode labels, and mlx5 driver QP subtypes.

## Important APIs, types, and functions
- `mlx5_ib_restrack_init()` installs `restrack_ops` into the RDMA device.
- `dump_rsc()` drives mlx5 resource dump commands using `mlx5_rsc_dump_cmd_create()`, `mlx5_rsc_dump_next()`, and `mlx5_rsc_dump_cmd_destroy()`.
- `fill_res_raw()` allocates a bounded buffer, dumps raw mlx5 hardware resource data, and emits `RDMA_NLDEV_ATTR_RES_RAW`.
- `fill_stat_mr_entry()` emits ODP counters for page faults, handled faults, invalidations, handled invalidations, and prefetches.
- `fill_res_mr_entry()` labels ODP MRs as implicit or explicit under `RDMA_NLDEV_ATTR_DRIVER`.
- `fill_res_mr_entry_raw()`, `fill_res_cq_entry_raw()`, and `fill_res_qp_entry_raw()` dump raw MKEY, CQ, and QP PRM data.
- `fill_res_qp_entry()` exposes mlx5 driver QP subtypes `REG_UMR`, `DCT`, and `DCI` for `IB_QPT_DRIVER`-style resources.

## Control flow
Initialization calls `ib_set_device_ops()` with a static `ib_device_ops` containing only resource-tracking callbacks. When RDMA netlink requests resource data, RDMA core calls the relevant fill callback. Raw callbacks allocate up to `MAX_DUMP_SIZE`, ask mlx5 firmware to dump one object by type and index, copy each returned page chunk into the buffer, and append it as a netlink attribute. MR callbacks skip non-ODP resources and otherwise emit driver metadata or statistics.

## State and persistence
This file maintains no long-lived state beyond registered device ops. It reads live hardware resource state through mlx5 dump commands and reads live ODP atomic counters from `struct mlx5_ib_mr`. Temporary dump buffers and pages are freed after each request.

## Dependencies and integration points
It integrates with RDMA netlink resource tracking, mlx5 resource dump firmware APIs, ODP MR statistics, netlink attribute helpers, mlx5 CQ/QP/MKEY identifiers, and mlx5 private QP type definitions. It is initialized through the declaration in `restrack.h`.

## Risks
- `dump_rsc()` enforces `MAX_DUMP_SIZE` of 1024 bytes; larger firmware dumps fail instead of truncating, so new hardware dump formats may need a larger bound.
- Netlink attribute construction can fail with `-EMSGSIZE`; nested attributes must be cancelled on every error path.
- Raw dumps expose low-level hardware state and must use the correct segment type and object number to avoid misleading diagnostics.
- Only ODP MRs receive stats and driver labels; callers must not interpret missing attributes as an error for regular MRs.
- `fill_res_qp_entry()` only recognizes selected driver QP subtypes; newly added driver QP types need updates for useful netlink output.

## Test signals
- RDMA netlink resource dump tests should verify raw CQ/QP/MR attributes are present and bounded for mlx5 devices.
- ODP MR tests should create implicit and explicit ODP MRs and confirm mode labels and counter names/values are emitted.
- Driver QP tests should create REG_UMR, DCT, and DCI resources and check subtype and `IB_QPT_DRIVER` type reporting.
- Failure tests should force small netlink buffers, resource dump command errors, and allocation failures to validate cleanup and `-EMSGSIZE`/error propagation.
