<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.h

## Purpose

This header is the documented in-kernel API for Innova FPGA client drivers. It defines connection attributes, DMA buffer shapes, memory access types, and exported SBU/memory/capability functions.

## Important APIs, types, and functions

- `SBU_QP_QUEUE_SIZE` and `MLX5_FPGA_CMD_TIMEOUT_MSEC` provide queue and timeout constants for clients.
- `enum mlx5_fpga_access_type` currently maps both I2C and DONTCARE to value `0`.
- `struct mlx5_fpga_dma_entry` describes one virtual/DMA address segment.
- `struct mlx5_fpga_dma_buf` contains up to two SG entries, a DMA direction, an SQ backlog list node, and an optional TX completion callback.
- `struct mlx5_fpga_conn_attr` carries TX/RX queue sizes and receive callback context.
- Public APIs create/destroy/send over SBU connections, read/write FPGA memory, and fetch SBU capabilities.

## Control flow

The header has no executable control flow. Its comments define important callback timing: receive callbacks may run before connection create returns, receive buffers are reusable after callback return, and send buffers must remain stable until completion.

## State and persistence

The data structures describe runtime DMA and callback state only. `dma_addr` is private to the implementation after mapping. `list` is owned by the SQ backlog while a send is queued. No state is persisted outside the kernel runtime.

## Dependencies and integration points

It includes Linux type and DMA-direction headers and forward-declares `mlx5_fpga_conn` and `mlx5_fpga_device`. It is consumed by FPGA client drivers and by internal `conn.c`/`sdk.c`.

## Risks

The API contract around buffer lifetime is strict and easy for clients to violate. The comments claim memory read/write return `0` on success, but `sdk.c` returns the byte count. `MLX5_FPGA_ACCESS_TYPE_DONTCARE` is currently identical to I2C, so callers cannot request a different fast path. Receive callbacks may happen during creation, requiring callers to initialize callback context before invoking create.

## Test signals

Consumer tests should validate callback ordering, send completion status, two-entry SG sends, receive buffer reuse assumptions, memory API return-value interpretation, and behavior when queue sizes are small or saturated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.h -->
