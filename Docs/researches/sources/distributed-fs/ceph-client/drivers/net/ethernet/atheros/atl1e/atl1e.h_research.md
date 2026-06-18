# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1e/atl1e.h

## Purpose
`atl1e.h` is the private header for the older Atheros L1E/L2E driver. It defines the driver-wide constants, descriptor formats, adapter/hardware state, RX page model, TX ring model, register access macros, and function prototypes shared by main, hardware, ethtool, and parameter code.

## Important APIs, types, and functions
The key hardware state type is `struct atl1e_hw`, containing MMIO base, memory range, PCI identity, NIC type, MAC addresses, frame thresholds, media/autoneg state, interrupt moderation timers, RSS/RRS type, DMA request sizing, and PHY flags. `struct atl1e_adapter` binds the netdev, pci_dev, NAPI object, MII info, hardware/stats, WoL/link state, locks, reset/link work, timers, DMA ring allocation, TX/RX rings, flags, PCI saved state, and config-space storage.

TX uses `struct atl1e_tpd_desc`, `struct atl1e_tx_ring`, and `struct atl1e_tx_buffer`. RX differs from ATL1C: it uses page-backed receive areas described by `struct atl1e_rx_page`, `struct atl1e_rx_page_desc`, and `struct atl1e_rx_ring`, with read/write offsets instead of a simple RFD/RRD descriptor pair per buffer. Receive status is `struct atl1e_recv_ret_status`.

Macros define TX checksum/segmentation fields, receive status flags/errors, VLAN tag transforms, DMA masks, timer constants, and MMIO accessors. Prototypes expose option checking, up/down/reinit, reset, and ethtool registration.

## Control flow and state behavior
The header has no executable flow, but its structures describe the driver lifecycle. Adapter flags track testing/reset/down state, work items perform reset/link handling, timers handle watchdog and PHY configuration, TX rings track producer/consumer indices, and RX pages track active page plus read/write offsets. Persistent hardware state includes EEPROM/VPD, PCI config, MAC address registers, PHY registers, and MMIO configuration.

## Dependencies and integration points
It depends on Linux PCI, netdevice, MII, ethtool, VLAN, SKB, workqueue, checksum, and DMA APIs, and on `atl1e_hw.h` for register constants. It integrates with `atl1e_hw.c` and `atl1e_ethtool.c`; the Makefile indicates `atl1e_main.c` and `atl1e_param.c` are additional consumers.

## Risks
The receive page model is more stateful than a descriptor-per-buffer model; offset synchronization with hardware is critical. `AT_TPD_TAG_TO_VLAN_TAG` references `_tdp` instead of `_tpd`, which would fail or miscompile if used. Several constants duplicate legacy advertisement names and must stay compatible with ethtool conversion code. Any mismatch in descriptor bit layout can corrupt TSO/checksum/VLAN behavior.

## Test signals
Compile coverage, RX under page wrap and jumbo settings, TX with SG/checksum/TSO, VLAN acceleration, ethtool link setting, suspend/resume, DMA API debug, and MII ioctl behavior are useful signals.
