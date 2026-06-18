# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/diag/sf_tracepoint.h

## Purpose

`sf/diag/sf_tracepoint.h` defines tracepoints for mlx5 SF devlink and hardware-table operations. It provides visibility into SF allocation, free, deferred free, activation, deactivation, and VHCA state updates.

## Important APIs and Control Flow

Events include `mlx5_sf_add`, `mlx5_sf_free`, `mlx5_sf_hwc_alloc`, `mlx5_sf_hwc_free`, `mlx5_sf_hwc_deferred_free`, `mlx5_sf_activate`, `mlx5_sf_deactivate`, and `mlx5_sf_update_state`. A shared event class is used for activate/deactivate style state events. Each event captures device name and relevant identifiers such as port index, controller, hardware function id, SF number, or state.

## State and Dependencies

The tracepoints are observational only. They depend on Linux tracepoint infrastructure, `struct mlx5_core_dev`, and the SF VHCA event type. The footer sets `TRACE_INCLUDE_PATH` to `sf/diag` and `TRACE_INCLUDE_FILE` to `sf_tracepoint`.

## Risks and Test Signals

Tracepoint field names must match the data passed by `sf/devlink.c` and `sf/hw_table.c`. Test by enabling mlx5 SF trace events while running devlink SF lifecycle commands and confirming hardware IDs and user SF numbers correlate with devlink output and firmware events.
