# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/vhca_event.h

## Purpose

`sf/vhca_event.h` declares the VHCA state event interface used by mlx5 SF manager components and provides no-op stubs when `CONFIG_MLX5_SF` is disabled.

## Important APIs and Types

`struct mlx5_vhca_state_event` carries hardware function id, software function id, and new VHCA state. The enabled API includes support detection, capability setup, notifier init, event init/cleanup/start/stop, notifier registration, software id modification, event arming, state query, work enqueue, and workqueue flush.

Disabled builds stub capability setup, notifier init, init/cleanup/start/stop to no-ops or success. Not all helper prototypes have stubs, so callers of query/arm/register functions must remain in SF-enabled code.

## State and Dependencies

The header itself has no storage. Enabled implementations mutate firmware VHCA state/event arm bits and `dev->priv.vhca_events`/notifier chains. It depends on `struct mlx5_core_dev`, `struct notifier_block`, and `struct work_struct` through included driver headers.

## Risks and Test Signals

Kconfig boundaries are the main risk. Compile SF and non-SF builds and validate that SF manager files do not call missing non-SF stubs. Runtime tests should confirm `mlx5_vhca_event_supported()` matches firmware capability before lifecycle functions allocate resources.
