# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/efx.c

## Purpose
Main Siena module, PCI, netdev, and top-level lifecycle implementation. It probes supported Solarflare PCI IDs, allocates/registers netdevs, wires netdev operations, configures NIC/port/channel resources, handles XDP/PTP/VLAN/SR-IOV hooks, and implements PM/remove paths.

## Important APIs and functions
Exports module parameters for interrupt mode, RSS CPU count, separate TX channels, PHY flash mode, and debug mask. `efx_pci_driver` binds PCI probe/remove/shutdown/PM/error handling. `efx_netdev_ops` wires open/stop/transmit/stats/ioctl/MTU/MAC/RX-mode/features/VLAN/hwtstamp/SR-IOV/port/TC/RFS/XDP operations. Core functions include `efx_pci_probe()`, `efx_pci_probe_main()`, `efx_pci_probe_post_io()`, `efx_probe_all()`, `efx_remove_all()`, `efx_register_netdev()`, `efx_unregister_netdev()`, `efx_net_open()`, `efx_net_stop()`, and PM helpers.

## Control flow
Probe allocates the netdev and `efx_nic`, initializes common state, maps PCI BAR/DMA, probes NIC/port/filters/channels/NAPI/hardware/interrupts, publishes features, registers the netdev, creates optional MTDs, and pushes UDP tunnel ports. Open checks disabled/special state, handles MC reboot reset, starts all runtime work, and starts async self-test. Remove closes and unregisters the netdev, disables interrupts, removes optional interfaces, tears down hardware/software resources, unmaps I/O, and frees memory.

## State and persistence behavior
Maintains global primary/secondary association lists by VPD serial number. Per-NIC state includes netdev features, `STATE_*`, XDP program pointer, channel names, IRQ moderation, VPD serial, sysfs `phy_type`, and optional MCDI logging setup. No on-disk persistence.

## Dependencies
Integrates PCI, netdev, ethtool, BPF/XDP, PTP, VLAN, RFS, SR-IOV, MTD, MCDI, and hardware-specific `efx_nic_type` callbacks.

## Risks
Probe/remove failure ordering is high risk because interrupts, NAPI, filters, SR-IOV, MTD, and netdev registration have strict lifetimes. XDP attach relies on RTNL/RCU and MTU bounds. PM paths must not restart disabled devices. Probe retries must clear `reset_pending` carefully.

## Test signals
Module load/unload, PCI bind/unbind, ifup/ifdown traffic, XDP attach/xmit, PTP timestamp config, SR-IOV when enabled, MTD creation when enabled, suspend/resume, hot-remove, and probe failure injection.
