<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.h

## Purpose

This internal header defines the full FPGA connection object and declares the connection/device lifecycle functions implemented by `conn.c`.

## Important APIs, types, and functions

- `struct mlx5_fpga_conn` combines client callback state, remote FPGA QPC/QPN, CQ state, host QP state, SQ/RQ rings, posted buffer arrays, and SQ backlog.
- The CQ substructure owns `mlx5_cqwq`, `mlx5_wq_ctrl`, `mlx5_core_cq`, and tasklet.
- The QP substructure tracks `active`, SGID index, host `mlx5_wq_qp`, QPN, SQ spinlock/producers/consumers/size/buffers/backlog, and RQ producers/consumers/size/buffers.
- Declared functions are `mlx5_fpga_conn_device_init()`, `mlx5_fpga_conn_device_cleanup()`, `mlx5_fpga_conn_create()`, `mlx5_fpga_conn_destroy()`, and `mlx5_fpga_conn_send()`.

## Control flow

The header has no executable control flow, but it documents ownership boundaries: device-level init/cleanup wraps shared resources, create/destroy wraps one connection, and send queues a DMA buffer through that connection.

## State and persistence

All fields are runtime-only. The SQ spinlock protects SQ producer/consumer counters, the posted-SQ buffer array, and backlog ordering. RQ state is manipulated by connection setup and CQ receive completion handling. Client callbacks are stored in the connection and invoked from completion context paths.

## Dependencies and integration points

The header includes mlx5 CQ/QP definitions, `fpga/core.h`, public `fpga/sdk.h` buffer/attribute definitions, and mlx5 work queue helpers. It is used by `conn.c` and by `sdk.c` as the internal implementation layer for public SBU APIs.

## Risks

Because the full struct is visible within the FPGA core, future users could bypass locking/ownership assumptions. The header exposes raw buffer arrays and counters rather than opaque accessors, so changes to posting/completion invariants must be coordinated with all users.

## Test signals

Compile coverage with `CONFIG_MLX5_FPGA` catches structure dependency drift. Runtime signals come from `conn.c`: queue size power-of-two behavior, SQ lock coverage, CQ teardown synchronization, and callback invocation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.h -->
