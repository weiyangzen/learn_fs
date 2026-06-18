<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/events.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/events.c

## Purpose

This file owns the general mlx5 core event dispatcher. It registers low-level EQ notifiers for firmware events, handles a small set of core diagnostics locally, forwards selected firmware events to mlx5 consumers, and provides a separate blocking notifier chain for driver-generated software events.

## Important APIs, types, and functions

- `struct mlx5_events` is attached at `dev->priv.events`. It owns the workqueue, registered EQ notifier wrappers, firmware atomic notifier chain, software blocking notifier chain, port-module statistics, and PCIe power work item.
- `events_nbs_ref[]` is the registration template for core handlers and forwarded event classes.
- `any_notifier()` logs all events at debug level; `temp_warn()` emits rate-limited high-temperature warnings and optional hwmon sensor names; `port_module()` updates port-module status/error counters and logs cable/module state; `pcie_core()` queues PCI power-status work for general PCI power-change events.
- `forward_event()` calls `atomic_notifier_call_chain(&events->fw_nh, event, data)` for mlx5e/mlx5_ib and other consumers.
- Public entry points include `mlx5_events_init/cleanup/start/stop`, `mlx5_notifier_register/unregister/call_chain`, `mlx5_blocking_notifier_register/unregister/call_chain`, and `mlx5_get_pme_stats()`.

## Control flow

Initialization allocates `struct mlx5_events`, initializes notifier heads, creates a single-thread workqueue, and stores it in `dev->priv.events`. Start copies each template notifier, stores the events context, and registers it with the EQ layer. Event callbacks either log/update local state or forward to consumer chains. Stop unregisters in reverse order and flushes the workqueue so queued PCIe work finishes before cleanup. Cleanup destroys the workqueue and frees the events object.

## State and persistence

Persistent runtime state is limited to notifier registration, `pme_stats`, and queued PCIe work. `pme_stats.status_counters[]` and `error_counters[]` accumulate until device cleanup. There is no disk persistence. PCIe power work reads `MLX5_REG_MPEIN` only when `pci_status_and_power` is supported.

## Dependencies and integration points

The file depends on `lib/eq.h` notifier registration, Linux notifier chains, optional `CONFIG_HWMON`, mlx5 register access, and device capability macros. It is the public event registration surface for mlx5 Ethernet and RDMA consumers. FPGA-specific, e-switch-specific, clock, tracer, and other feature events are intentionally handled elsewhere.

## Risks

Event ordering depends on start/stop registration order. Forwarded `GENERAL_EVENT` also has a local `pcie_core` handler, so consumers must tolerate seeing the same firmware event class through the atomic chain. `mlx5_get_pme_stats()` returns a non-atomic structure copy without explicit locking; counters are simple diagnostics. Workqueue creation failure must leave `dev->priv.events` either unused or cleaned by caller paths.

## Test signals

Tests should exercise event registration/unregistration during device start/stop, module plug/unplug/error EQEs, temperature warning EQEs with and without hwmon, PCI power-change general events, and consumer notifier delivery. Race tests should include unregister while events are in flight and cleanup after queued PCIe work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/events.c -->
