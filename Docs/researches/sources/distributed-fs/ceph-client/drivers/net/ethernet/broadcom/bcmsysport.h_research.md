# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcmsysport.h

Purpose: Defines the hardware contract and driver-private state for the SYSTEMPORT Ethernet MAC implementation. It is the central map of descriptor formats, register offsets, interrupt bits, DMA ring fields, statistics layout, and `struct bcm_sysport_priv`.

Important APIs/types: `struct bcm_tsb` describes the transmit status block used for checksum/VLAN metadata. `struct bcm_rsb` describes the receive status block prepended by hardware. Register groups cover TOPCTRL, INTRL2, RXCHK, RBUF, TBUF, UMAC, Lite-only GIB, RDMA, and TDMA. `struct bcm_sysport_mib`, `struct bcm_sysport_stats`, and related macros define ethtool statistic mapping. `struct bcm_sysport_cb` tracks SKB and DMA address for RX/TX descriptors. `struct bcm_sysport_tx_ring` models per-queue TDMA state. `struct bcm_sysport_priv` aggregates platform resources, RX/TX rings, PHY state, coalescing/DIM, WoL, filters, stats, and DSA queue map. `BCM_SYSPORT_IO_MACRO()` creates typed MMIO accessors.

Control flow support: The header encodes all offsets and bit masks that `bcmsysport.c` uses to build descriptors, program DMA rings, mask interrupts, detect RX/TX completion, configure checksum parsing, and handle Lite-specific GIB/RDMA/TDMA differences. The statistics macros make array order match the memory layout of both hardware MIB blocks and software fields.

State/persistence: The persistent runtime state is explicitly centralized in `struct bcm_sysport_priv`. RX descriptor backing is MMIO-based, while software `bcm_sysport_cb` arrays remember DMA mappings. TX ring state records descriptor availability and clean/current indices. WoL filters are stored as a bitmap plus location array. `u64_stats_sync` allows lockless stats reads on 32-bit systems.

Dependencies/integration: Includes kernel bitmap, ethtool, VLAN, DIM, and local `unimac.h`; consumers depend on netdevice, phylib, DMA, DSA and platform APIs in the C file. Constants assume Broadcom register layout and 40-bit descriptor addressing.

Risks/test signals: Header changes are risky because structure offsets are used by ethtool stat descriptors and register offsets feed raw MMIO. Validate with compile coverage across big/little endian, 32/64-bit DMA address builds, SYSTEMPORT vs Lite devices, ethtool stats ordering, and packet offload behavior.
