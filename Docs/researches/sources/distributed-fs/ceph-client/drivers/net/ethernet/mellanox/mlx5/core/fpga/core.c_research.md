<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.c

## Purpose

This file owns mlx5 FPGA device discovery, startup, shutdown, health integration, and FPGA error event handling. It decides whether an FPGA is present, validates image load status, initializes connection resources for network-processing FPGA images, and tears down the device on FPGA error events.

## Important APIs, types, and functions

- `mlx5_fpga_init()` allocates `struct mlx5_fpga_device` when the general FPGA capability is present and attaches it to `mdev->fpga`.
- `mlx5_fpga_device_start()` reads FPGA capabilities, checks image load state, logs card/image/SBU identity, reserves GIDs, registers FPGA error EQ notifiers, initializes connection resources, and optionally performs sandbox bypass-reset-bypass.
- `mlx5_fpga_device_stop()` reverses startup for non-lookaside devices and turns sandbox bypass back on for user images.
- `mlx5_fpga_cleanup()` calls stop, frees the FPGA object, and clears `mdev->fpga`.
- `mlx5_fpga_event()` decodes FPGA and FPGA-QP error syndromes, changes behavior based on `fdev->state`, and triggers mlx5 health work on active-device errors.

## Control flow

Startup is capability gated. Lookaside FPGA projects skip QP connection setup because they do not participate in network processing. Non-lookaside startup requires a successful image load, nonzero `shell_caps.max_num_qps`, reserved GIDs, error notifier registration, device connection resource init, and optional reset/bypass sequence for user images. Errors unwind registered notifiers and GID reservations. Stop checks the software state under `state_lock`, marks it inactive, applies bypass if needed, cleans connection resources, unregisters notifiers, and unreserves GIDs.

## State and persistence

`struct mlx5_fpga_device` stores software state under `state_lock`, last admin/oper image values, EQ notifier blocks, and shared connection resources. No disk state exists. Firmware state changed by this file includes FPGA control operations and possibly sandbox bypass/reset state. Error events can trigger health recovery by calling `mlx5_trigger_health_work()`.

## Dependencies and integration points

This file depends on the command helpers in `cmd.c`, connection resource helpers in `conn.c`, mlx5 EQ notifier registration, mlx5 health recovery, and core GID reservation APIs. It is conditionally compiled behind `CONFIG_MLX5_FPGA` through `core.h`.

## Risks

State transitions must remain paired with resource ownership. `mlx5_fpga_device_stop()` returns early for lookaside devices and for failed/non-success states; cleanup relies on those branches matching what startup actually allocated. Error events during startup/teardown are rate-limited or health-triggering depending on `state`. `mlx5_fpga_name()` uses a static buffer for unknown IDs, which is fine for logging but not reentrant as a general API.

## Test signals

Tests should cover devices without FPGA capability, lookaside vs non-lookaside IDs, image load failure, zero-QP capability, connection init failure unwind, user-image bypass/reset operations, FPGA and FPGA-QP error EQEs, and stop/cleanup idempotence. Health recovery tests should confirm active FPGA errors trigger device recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.c -->
