# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/atl1c/atl1c.h

## Purpose
`atl1c.h` is the private driver header for the Atheros L1C/L2C/L1D family. It collects Linux networking includes, descriptor layouts, ring state, adapter state, offload bit definitions, register access macros, constants for MTU/DMA/timers, and prototypes shared between `atl1c_main.c`, `atl1c_hw.c`, and `atl1c_ethtool.c`.

## Important APIs, types, and functions
The central data type is `struct atl1c_adapter`, which binds `struct net_device`, `struct pci_dev`, `struct atl1c_hw`, hardware stats, MII plumbing, WoL configuration, link state, locks, work/timers, descriptor rings, and queue counts. `struct atl1c_hw` stores MMIO base, PCI identity, NIC type, DMA ordering, link capabilities, PHY state, MAC addresses, interrupt mask, ASPM/control flags, and PHY tuning flags.

DMA state is split into `struct atl1c_ring_header`, `struct atl1c_tpd_ring`, `struct atl1c_rfd_ring`, and `struct atl1c_rrd_ring`. Per-buffer state lives in `struct atl1c_buffer`, with flags recording free/busy state, DMA mapping type, and direction. On-wire/hardware descriptors are `struct atl1c_tpd_desc`, `struct atl1c_tpd_ext_desc`, `struct atl1c_rx_free_desc`, and `struct atl1c_recv_ret_status`.

Important macros include `ATL1C_TPD_DESC`, `ATL1C_RFD_DESC`, `ATL1C_RRD_DESC`, field masks for TX checksum/TSO/VLAN offload, RRS receive status bits, VLAN byte-swap helpers, and `AT_READ_REG`/`AT_WRITE_REG` accessors. The accessors include a hibernate double-read workaround for some register reads.

## Control flow and state behavior
The header does not execute control flow, but it defines the state machine used by the driver. `adapter->flags` tracks testing, resetting, and down state; `adapter->work_event` tracks reset and link-change work; `adapter->irq_sem` gates interrupt enable/disable; ring producer/consumer indices track DMA ownership. Hardware state persists in MMIO registers and descriptors; software state persists in the adapter while the netdev is registered and is rebuilt across open/close or suspend/resume.

## Dependencies and integration points
It depends on Linux PCI, netdevice, ethtool, MII, VLAN, SKB, NAPI, workqueue, checksum, and DMA APIs. `atl1c_main.c` owns most consumers of ring and adapter fields, `atl1c_hw.c` consumes `struct atl1c_hw` and register macros for PHY and EEPROM work, and `atl1c_ethtool.c` exposes selected state to userspace.

## Risks
The descriptor structures and bit masks must match hardware layout exactly. Any mismatch can corrupt DMA, break offload, or misreport RX status. `ATL1C_SET_BUFFER_STATE` and `ATL1C_SET_PCIMAP_TYPE` are macro-based state transitions; callers must set them consistently or cleanup can unmap with the wrong direction/type. `struct atl1c_hw_stats` assumes hardware MIB order matches `atl1c_update_hw_stats()`. The hibernate read workaround makes register access semantics differ from normal readl paths.

## Test signals
Compile coverage is essential because this header is shared widely. Runtime signals include successful RX/TX with SG, checksum, TSO, VLAN acceleration, queue cleanup without DMA API warnings, correct ethtool link/register reporting, and stable reset/suspend paths.
