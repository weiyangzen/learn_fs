<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.c

## Purpose

This file implements the exported in-kernel Innova FPGA SDK functions. It adapts public SBU connection APIs to the internal connection implementation and exposes FPGA memory read/write plus SBU capability reads through the FPGA access register.

## Important APIs, types, and functions

- `mlx5_fpga_sbu_conn_create()`, `destroy()`, and `sendmsg()` are exported wrappers around `mlx5_fpga_conn_create/destroy/send()` using `MLX5_FPGA_QPC_QP_TYPE_SANDBOX_QP`.
- `mlx5_fpga_mem_read_i2c()` and `mlx5_fpga_mem_write_i2c()` chunk memory operations by `MLX5_FPGA_ACCESS_REG_SIZE_MAX` and call `mlx5_fpga_access_reg()`.
- `mlx5_fpga_mem_read()` and `mlx5_fpga_mem_write()` validate the requested access type and return the requested size on success.
- `mlx5_fpga_get_sbu_caps()` forwards to `mlx5_fpga_sbu_caps()`.

## Control flow

Connection APIs are direct pass-throughs. Memory read/write reject zero length, reject disconnected FPGA objects without `mdev`, then loop until all bytes have been processed or a command error occurs. Only `MLX5_FPGA_ACCESS_TYPE_I2C` is accepted; `DONTCARE` currently aliases the same enum value, so it also selects I2C.

## State and persistence

The SDK functions do not store state. Connection calls create/destroy state in `conn.c`; memory calls read/write FPGA address space through firmware. Successful read/write functions return `size`, not `0`, so callers should treat positive values as byte counts.

## Dependencies and integration points

The file depends on `fpga/core.h`, `fpga/conn.h`, `fpga/sdk.h`, and the command access helpers in `cmd.c`. The `EXPORT_SYMBOL` declarations make this API available to other in-kernel FPGA client drivers.

## Risks

The header comments describe `0` as success for memory read/write, but the implementation returns the byte count. That mismatch can break callers that only test `ret == 0`. Partial progress is not returned on command error; the first error aborts and returns the error code. Access-type expansion must update both the enum and switch statements.

## Test signals

Tests should cover SBU connection creation/send/destruction, zero-length memory operations, disconnected device handling, reads/writes spanning multiple access-register chunks, command failures mid-transfer, and consumer handling of positive success returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.c -->
