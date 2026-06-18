<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.h

## Purpose

This header declares the internal FPGA command ABI used by the mlx5 FPGA core and connection layers. It defines device/image/status enums, the query result structure, QP modify field selection, QP counter structure, and command helper prototypes.

## Important APIs, types, and functions

- `enum mlx5_fpga_id` names supported Innova FPGA card families: Newton, Edison, Morse, and MorseQ.
- `enum mlx5_fpga_image` distinguishes user and factory images.
- `enum mlx5_fpga_status` mirrors firmware load/control status values, including `SUCCESS`, `FAILURE`, `IN_PROGRESS`, and `NONE`.
- `struct mlx5_fpga_query` carries admin image, operational image, and status returned by `mlx5_fpga_query()`.
- `enum mlx5_fpga_qpc_field_select` currently exposes `MLX5_FPGA_QPC_STATE` for state-only QP modification.
- `struct mlx5_fpga_qp_counters` carries packet/drop counters decoded from firmware.
- Prototypes expose capability, query, control, register access, SBU capability, FPGA QP lifecycle, and FPGA QP counter helpers.

## Control flow

The header has no runtime control flow. It defines the contract that `cmd.c` implements and that `core.c`, `conn.c`, and `sdk.c` consume.

## State and persistence

The header describes firmware-visible state but stores none. The enums and structures must remain aligned with mlx5 firmware encodings because they gate image status interpretation and QP state transitions.

## Dependencies and integration points

It includes `linux/mlx5/driver.h` for mlx5 core types and kernel integer helpers. It is internal to the mlx5 FPGA feature and is included by `fpga/core.h`, `fpga/core.c`, `fpga/conn.c`, and `fpga/sdk.c` through direct or indirect paths.

## Risks

Incorrect enum values would misclassify hardware and image state. Adding QPC field bits without updating command handling could cause firmware modifications to use stale QPC data. The `MLX5_FPGA_STATUS_NONE = 0xFFFF` sentinel is used as software state as well as a status-like value, so consumers must not treat it as a firmware success code.

## Test signals

Build coverage with `CONFIG_MLX5_FPGA` is the main compile-time signal. Runtime tests should verify query status decoding, image name/status handling in `core.c`, and state-only QP modification in `conn.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.h -->
