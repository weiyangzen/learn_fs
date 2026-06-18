# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/restrack.h

## Purpose
`restrack.h` is the local header for mlx5 RDMA resource tracking integration. It exposes the initialization hook that installs mlx5 resource dump callbacks into the RDMA device.

## Important APIs, types, and functions
- Includes `mlx5_ib.h` for `struct mlx5_ib_dev`.
- Declares `mlx5_ib_restrack_init(struct mlx5_ib_dev *dev)`.

## Control flow
Device initialization code includes this header and calls `mlx5_ib_restrack_init()` once the `mlx5_ib_dev` is ready to receive RDMA device ops. The implementation in `restrack.c` registers the static callback table.

## State and persistence
The header stores no state. The only persistent effect of its API is that the RDMA device receives mlx5-specific resource tracking callbacks.

## Dependencies and integration points
It depends on mlx5 IB device definitions and integrates with RDMA core device-ops registration through `restrack.c`.

## Risks
- The header is intentionally small; the main risk is signature drift between initialization callers and `restrack.c`.
- If initialization ordering changes, callers must still ensure resource-tracking ops are installed before userspace netlink queries are expected.

## Test signals
- Compile coverage catches prototype mismatches.
- Device initialization tests should verify mlx5 resource tracking callbacks are available through RDMA netlink after device registration.
