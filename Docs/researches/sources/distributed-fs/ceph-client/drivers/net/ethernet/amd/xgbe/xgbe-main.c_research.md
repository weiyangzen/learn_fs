# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-main.c

## Purpose
`xgbe-main.c` is the top-level module and netdev configuration file. It allocates `struct xgbe_prv_data`, initializes function-pointer tables, derives channel/queue counts, configures the net_device feature set, registers/unregisters the netdev and PTP clock, and registers both platform and PCI bus drivers at module load.

## Important APIs, Types, And Functions
- Module metadata and the `debug` module parameter establish driver identity and default message logging.
- `xgbe_default_config` seeds DMA, FIFO threshold, flow-control, PHY speed, and power defaults.
- `xgbe_init_all_fptrs` wires hardware, generic PHY, I2C, descriptor, and version-specific PHY implementation callbacks.
- `xgbe_alloc_pdata`/`xgbe_free_pdata` allocate and free an `alloc_etherdev_mq` netdev with private data.
- `xgbe_set_counts` reads hardware features and determines initial TX/RX rings and queues.
- `xgbe_config_netdev` performs reset, default configuration, DMA mask setup, PHY init, netdev ops/features setup, coalescing init, registration, PTP registration, and debugfs init.
- `xgbe_deconfig_netdev` reverses debugfs, PTP, netdev, and PHY registration.
- `xgbe_netdev_event` handles rename events for debugfs.
- `xgbe_mod_init`/`xgbe_mod_exit` register/unregister the notifier plus platform and PCI drivers.

## Control Flow
Bus-specific probe code allocates `pdata`, fills resources and version data, calls `xgbe_set_counts`, then calls `xgbe_config_netdev`. That routine resets hardware through `hw_if.exit`, applies defaults, configures DMA capabilities and descriptor counts, constrains channels by IRQ availability, initializes RSS, runs PHY init, assigns ops, sets netdev offload features, initializes coalescing, registers the netdev, registers PTP if available, and initializes debugfs. Module init registers platform first, then PCI; failures unwind in reverse.

## State And Persistence
`pdata` owns all runtime state: locks, completions, feature flags, rings, counts, PHY state, timestamping, work items, and resources. Defaults are in-memory only. `msg_enable` persists for the lifetime of the device and can be modified through ethtool. The netdev registration makes this runtime state visible to the networking stack.

## Dependencies And Integration Points
This file integrates all driver subsystems: hardware operations, descriptors, PHY/MDIO, I2C, ethtool, netdev ops, optional DCB, PTP, debugfs, platform probing, and PCI probing. It depends on bus-specific code to populate MMIO addresses, clocks, IRQs, MAC address, version data, and device property registers before `xgbe_config_netdev` runs.

## Risks
The order of initialization matters: function pointers and hardware features must be valid before count calculation and netdev setup. A failure after partial registration must unwind cleanly; this file delegates much of that to bus-specific devm/pcim cleanup and `xgbe_deconfig_netdev`. Feature flags must match hardware capabilities or the stack can hand unsupported traffic to the driver. Channel count logic depends on CPU count, hardware limits, and IRQ count.

## Test Signals
Module load/unload, PCI and platform probe/remove, netdev rename, PTP registration, debugfs creation, and feature advertisement through `ethtool -k/-i` are primary signals. Regression tests should include probe failure injection around PHY init and netdev registration, plus suspend/resume through the bus-specific files.
