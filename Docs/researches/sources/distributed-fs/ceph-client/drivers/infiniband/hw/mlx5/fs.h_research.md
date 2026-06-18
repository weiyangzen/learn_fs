<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.h

## Purpose
Declares mlx5 flow-steering initialization and cleanup helpers and documents the special lifetime rule for user-visible steering anchor flow tables.

## Important APIs, Types, And Functions
- `mlx5_ib_fs_init()` initializes the mlx5 IB flow database and registers flow provider ops.
- `mlx5_ib_fs_cleanup_anchor()` destroys retained steering-anchor resources.
- `mlx5_ib_fs_cleanup()` is an inline full cleanup helper that destroys anchors, frees RDMA transport RX/TX per-priority arrays, and frees `dev->flow_db`.

## Control Flow
The inline cleanup first calls `mlx5_ib_fs_cleanup_anchor(dev)`, then frees every allocated RDMA transport TX and RX priority array up to `MLX5_RDMA_TRANSPORT_BYPASS_PRIO`, and finally frees the `flow_db` container. The comment explains that anchor flow tables may outlive individual user anchor destruction because users can reference the table; they are destroyed only when the RDMA device is destroyed.

## State And Persistence
The header itself stores no state. It defines cleanup for `dev->flow_db`, which owns flow table priority arrays and retained steering-anchor resources allocated by `fs.c`.

## Dependencies And Integration Points
The header includes `mlx5_ib.h` and is used by mlx5 IB device lifecycle code to initialize and tear down flow steering. It pairs with `fs.c`, which allocates the flow database and implements anchor cleanup.

## Risks And Edge Cases
Cleanup assumes `dev->flow_db` was allocated and that RDMA transport arrays are either valid allocations or NULL. Anchor cleanup must precede freeing flow-db memory because anchor state is embedded in the priority arrays. The intentionally delayed anchor table destruction can look like a leak unless the device-level cleanup path is understood and tested.

## Test Signals
Build and unload/reload the mlx5 IB driver with flow steering enabled. Exercise steering anchor create/destroy followed by device teardown and verify retained anchor tables are released only at cleanup. Fault-injection tests for partial `mlx5_ib_fs_init()` allocation should verify cleanup of already allocated transport arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/fs.h -->
