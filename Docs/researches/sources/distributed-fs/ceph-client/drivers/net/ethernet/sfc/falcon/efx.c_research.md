# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/efx.c

## Purpose
`efx.c` is the core of the legacy Falcon `sfc-falcon` network driver. It owns module parameters, PCI probe/remove, netdev registration, interrupt/channel setup, datapath start/stop, port lifecycle, filter table setup, reset and PCI error recovery, power management, NAPI polling, workqueues, and global Falcon loopback/reset name tables.

## Important APIs, Types, and Functions
Externally visible driver APIs include `ef4_net_open()`, `ef4_net_stop()`, `ef4_realloc_channels()`, `ef4_reconfigure_port()`, `ef4_mac_reconfigure()`, `ef4_schedule_reset()`, `ef4_reset()`, `ef4_reset_down()`, `ef4_reset_up()`, `ef4_try_recovery()`, interrupt moderation helpers, link-state helpers, dummy PHY ops, and `ef4_update_sw_stats()`. Static integration objects include `ef4_netdev_ops`, `ef4_pci_driver`, `ef4_pm_ops`, `ef4_err_handlers`, `ef4_pci_table`, and the global `reset_workqueue`.

## Control Flow
Probe allocates a multiqueue netdev, initializes `struct ef4_nic`, maps PCI BARs, probes NIC/port/filter/channel resources, initializes NAPI, initializes hardware/port/interrupts, sets netdev features, registers the netdev, and optionally probes MTD. Open checks disabled/special states, publishes current link state, starts the port and datapath, queues monitoring, and starts async self-test. Stop quiesces stats, monitor/self-test/MAC work, TX queues, DMA queues, RX refill, and datapath resources.

NAPI polling calls `ef4_process_channel()`, which processes event queues, flushes RX packets, refills RX descriptors, and completes BQL accounting. Channel probing allocates event queues, TX queues, and RX queues; reallocation detaches the device, stops traffic, soft-disables interrupts, clones copyable channels, swaps queue sizes, probes replacement channels, and rolls back on failure. Reset work chooses the highest pending reset bit, optionally tries EEH recovery, then runs `ef4_reset()` under RTNL. Reset down stops datapath/interrupts and tears down PHY/NIC state under `mac_lock`; reset up reinitializes hardware, PHY, interrupts, filters, unlocks, and restarts if allowed.

## State and Persistence
Persistent runtime state lives in `struct ef4_nic`: `state`, `reset_pending`, `port_enabled`, `port_initialized`, queue sizes, channel arrays, RSS indirection/key, interrupt mode, IRQ moderation, filters, MAC/PHY state, workqueues, VPD serial, and PCI BAR mappings. Global association lists track primary/secondary functions by VPD serial. Module parameters persist for module lifetime and affect channel split, RSS CPUs, interrupt mode, IRQ moderation thresholds, debug mask, and PHY flash mode.

## Dependencies and Integration Points
The file integrates with PCI, netdevice, NAPI, ethtool via `ef4_ethtool_ops`, MDIO ioctls, MSI/MSI-X, workqueues, PM callbacks, PCI AER/EEH recovery, MTD optional hooks, self-tests, Falcon NIC-type operation tables, TX/RX queue code, filter code, and PHY implementations. Type-specific callbacks in `efx->type` provide hardware behavior for probe/init/reset/stats/filter/interrupt/MAC operations.

## Risks
State transitions depend on RTNL, `mac_lock`, `stats_lock`, filter semaphores, IRQ synchronization, and workqueue cancellation being used in the intended order. Channel reallocation has rollback complexity and must not lose non-copyable channel buffer-table allocations. Reset masking assumes reset methods are ordered by scope. Probe/remove and PM paths must leave no live work item, IRQ, NAPI instance, or mapped BAR behind. The file uses legacy ethtool advertising bits and older MSI APIs, so kernel API changes can break backports.

## Test Signals
Important tests include PCI probe/remove, module unload, interface open/close, MTU and MAC address changes, TX watchdog reset, manual ethtool reset, suspend/resume/freeze/thaw, PCI error injection, MSI-X/MSI/legacy fallback, channel/ring resizing via ethtool, RSS CPU/module parameter variations, link change logging, async self-test execution, and netdev rename updating MTD/channel names. Lockdep, KASAN, interrupt storm checks, and repeated reset/remove cycles are high-value signals.
