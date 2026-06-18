<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.c

## Purpose

This file is the low-level command/register bridge for mlx5 Innova FPGA support. It encodes FPGA access, capability, control, query, FPGA QP, and FPGA QP counter commands into mlx5 firmware command/register layouts.

## Important APIs, types, and functions

- `mlx5_fpga_access_reg()` validates 4-byte alignment and maximum transfer size, then reads or writes `MLX5_REG_FPGA_ACCESS_REG`.
- `mlx5_fpga_caps()` reads `MLX5_REG_FPGA_CAP` into `dev->caps.fpga`.
- `mlx5_fpga_ctrl_op()` writes a control operation into `MLX5_REG_FPGA_CTRL`.
- `mlx5_fpga_sbu_caps()` reads the sandbox extended capability blob in chunks using `mlx5_fpga_access_reg()`.
- `mlx5_fpga_query()` reads status and selected admin/operational image from `MLX5_REG_FPGA_CTRL`.
- `mlx5_fpga_create_qp()`, `modify_qp()`, `query_qp()`, `destroy_qp()`, and `query_qp_counters()` wrap FPGA-specific firmware opcodes and copy QPC/counter fields to/from callers.

## Control flow

Most functions build a stack `in` buffer with `MLX5_SET` macros, call `mlx5_core_access_reg()` or `mlx5_cmd_exec*()`, then decode output fields. `mlx5_fpga_sbu_caps()` loops over the device-advertised capability length and advances the FPGA address and caller buffer pointer by each successful read.

## State and persistence

No state is stored in this file except the side effect of updating `dev->caps.fpga`. Firmware state affected by these calls includes FPGA control operation state, sandbox capability reads, and FPGA-owned QP objects/counters. Query-counter can optionally clear counters through the command `clear` bit.

## Dependencies and integration points

The code depends on generated mlx5 IFC layouts, command opcodes, `mlx5_core_access_reg()`, and `mlx5_cmd_exec*()`. It is consumed by `fpga/core.c` for startup/status/control, `fpga/conn.c` for remote FPGA QP lifecycle, and `fpga/sdk.c` for memory/capability API calls.

## Risks

Alignment and size validation protects the FPGA access register, but callers must still chunk unaligned logical operations themselves. `mlx5_fpga_sbu_caps()` uses a `void *` pointer increment, which relies on GNU C semantics used in the kernel. Buffer size must match `sandbox_extended_caps_len` or the function fails. QPC copies use fixed firmware field sizes, so layout drift would corrupt QP creation/modification.

## Test signals

Validation should cover aligned and unaligned FPGA access reads/writes, SBU capability reads larger than one register window, FPGA status query for success/failure/in-progress, QP create/modify/query/destroy, and counter query with and without clear. Fault injection on command failures should verify no caller-visible partial QP identity is trusted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.c -->
