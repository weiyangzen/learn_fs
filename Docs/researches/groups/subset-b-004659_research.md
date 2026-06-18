# Research: subset-b-004659

Grouped research report for Tehuti, Synopsys XLGMAC, and TI AM65 CPSW ethernet driver files. Each section is source-tree aligned and bounded for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac.h

## Purpose
This header is the shared internal contract for the Synopsys DesignWare XLGMAC ethernet driver. It centralizes driver identity, descriptor sizing, DMA channel limits, interrupt categories, coalescing defaults, flow control/RSS limits, descriptor helper macros, all major private state structures, hardware operation tables, descriptor operation tables, and cross-file entry points used by the PCI, netdev, hardware, descriptor, ethtool, and common support files.

## Important APIs, Types, and Functions
Important exported declarations include `xlgmac_init_desc_ops`, `xlgmac_init_hw_ops`, `xlgmac_get_netdev_ops`, `xlgmac_get_ethtool_ops`, descriptor dump helpers, hardware feature discovery helpers, `xlgmac_drv_probe`, and `xlgmac_drv_remove`. Core types include `struct xlgmac_pdata`, `struct xlgmac_channel`, `struct xlgmac_ring`, `struct xlgmac_desc_data`, `struct xlgmac_pkt_info`, `struct xlgmac_hw_ops`, `struct xlgmac_desc_ops`, `struct xlgmac_hw_features`, and `struct xlgmac_stats`. The register bit helpers `XLGMAC_GET_REG_BITS`, `XLGMAC_GET_REG_BITS_LE`, `XLGMAC_SET_REG_BITS`, and `XLGMAC_SET_REG_BITS_LE` are used to manipulate hardware descriptor/register fields consistently, including little-endian descriptor values.

## Control Flow and State
The file itself does not execute control flow, but it defines the state transitions used elsewhere. `xlgmac_pdata` is the root per-device state: netdev/device pointers, operation tables, hardware features, channel/ring counts, coalescing settings, FIFO/PBL thresholds, flow-control settings, interrupt routing, VLAN filter bitmap, RSS key/table/options, clock rate, and PHY speed. `xlgmac_channel` binds queue index, DMA register base, NAPI context, timer state, and optional per-channel IRQ to TX/RX rings. `xlgmac_ring` tracks DMA descriptor arrays, per-descriptor software data, current/dirty indices, RX page allocation caches, and TX queue state. Receive continuation state is persisted in `xlgmac_desc_data.state` for incomplete packets across NAPI budget boundaries.

## Dependencies and Integration Points
The header depends on Linux networking, DMA, workqueue, PHY, VLAN, bitops, and timecounter facilities. It integrates with netdev ops via `xlgmac_get_netdev_ops`, ethtool via `xlgmac_get_ethtool_ops`, platform/PCI probe via `xlgmac_drv_probe`, and the hardware/descriptor implementation files through `xlgmac_hw_ops` and `xlgmac_desc_ops`. Feature fields mirror hardware registers and drive conditional enablement for RSS, checksum offload, timestamping, VLAN filtering, TSO, split headers, and flow control.

## Risks and Test Signals
Descriptor count and buffer-size constants are high-risk because TX split/GSO and RX allocation depend on them matching hardware constraints. Ring indices assume descriptor counts are power-of-two because `XLGMAC_GET_DESC_DATA` masks with `count - 1`. Endianness helpers need coverage on descriptor field generation and parsing. Useful tests include build coverage for all XLGMAC objects, probe/remove on PCI hardware or emulation, TX GSO and VLAN traffic, RX checksum/VLAN/RSS paths, interrupt coalescing changes via ethtool, and suspend/remove paths that validate DMA resources and NAPI/channel state are released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/Kconfig

## Purpose
This Kconfig fragment gates Tehuti ethernet driver visibility and build selection. It defines the vendor menu `NET_VENDOR_TEHUTI`, the legacy `TEHUTI` 10G driver, and the newer `TEHUTI_TN40` TN40xx driver.

## Important APIs, Types, and Functions
The relevant configuration symbols are `NET_VENDOR_TEHUTI`, `TEHUTI`, and `TEHUTI_TN40`. `NET_VENDOR_TEHUTI` is a boolean vendor menu depending on `PCI`. `TEHUTI` is a tristate for the older `tehuti.o` PCI driver. `TEHUTI_TN40` is a tristate for the `tn40xx` module and selects `PAGE_POOL`, `FW_LOADER`, and `PHYLINK`.

## Control Flow and State
There is no runtime control flow. Build-time state determines whether Tehuti-specific questions appear and whether the legacy or TN40 module objects are compiled. The selected helper subsystems are important runtime prerequisites: TN40 RX uses page_pool, firmware loading uses `request_firmware`, and link management uses phylink.

## Dependencies and Integration Points
Both drivers depend on PCI. `TEHUTI_TN40` integrates with `tn40.c`, `tn40_mdio.c`, and `tn40_phy.c` through the Makefile module definition. The help text documents currently supported TN40xx/AQR105-based adapters and the resulting module name `tn40xx`.

## Risks and Test Signals
The main risk is stale dependency modeling: if TN40 code starts using additional subsystems, missing `select` or `depends on` entries will surface as build failures in sparse randconfig coverage. Test signals are `oldconfig/menuconfig` visibility, `m` and `y` builds for both drivers, and randconfig combinations with PCI enabled but optional firmware/phylink/page_pool settings varied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/Makefile

## Purpose
This Makefile maps Tehuti Kconfig symbols to kernel objects. It builds the legacy single-file driver and the newer multi-object TN40xx module.

## Important APIs, Types, and Functions
`obj-$(CONFIG_TEHUTI) += tehuti.o` builds the legacy driver. `tn40xx-y := tn40.o tn40_mdio.o tn40_phy.o` defines the composite module contents, and `obj-$(CONFIG_TEHUTI_TN40) += tn40xx.o` enables that module when selected.

## Control Flow and State
There is no runtime behavior. Build state controls linkage boundaries: `tn40.c` owns PCI/netdev/data path, `tn40_mdio.c` owns MDIO bus and software-node setup, and `tn40_phy.c` owns phylink callbacks and PHY registration. Those objects share `tn40.h` declarations and are linked into one module.

## Dependencies and Integration Points
The file depends on symbols from `Kconfig` and on the kernel kbuild convention for composite `*-y` objects. It integrates with module firmware annotations from `tn40.c` and `tn40_mdio.c`; both object files must be linked for all firmware declarations and exported intra-module functions to resolve.

## Risks and Test Signals
The highest risk is object list drift: removing `tn40_mdio.o` or `tn40_phy.o` would leave unresolved `tn40_mdiobus_init`, `tn40_swnodes_cleanup`, `tn40_phy_register`, or `tn40_phy_unregister`. Test signals are module builds for `CONFIG_TEHUTI_TN40=m`, built-in builds, and `modinfo tn40xx` showing expected firmware references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tehuti.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tehuti.c

## Purpose
This is the legacy Tehuti 10G PCI ethernet driver for devices `0x3009`, `0x3010`, and `0x3014`. It implements PCI probe/remove, netdev open/stop/transmit, NAPI interrupt handling, firmware loading through the TX descriptor FIFO, RX/TX FIFO allocation, VLAN/multicast/MAC programming, private register ioctl access, and ethtool support for link, coalescing, ring sizing, and hardware statistics.

## Important APIs, Types, and Functions
The driver registers `bdx_pci_driver` with `bdx_probe` and `bdx_remove`; module init calls `init_txd_sizes` before `pci_register_driver`. Netdev operations are `bdx_open`, `bdx_close`, `bdx_tx_transmit`, `bdx_setmulti`, `bdx_change_mtu`, `bdx_set_mac`, VLAN add/kill, and `bdx_siocdevprivate`. NAPI/IRQ flow is handled by `bdx_isr_napi`, `bdx_poll`, `bdx_rx_receive`, and `bdx_tx_cleanup`. Resource helpers include `bdx_fifo_init/free`, `bdx_tx_init/free`, `bdx_rx_init/free`, `bdx_fw_load`, reset helpers, and TX/RX database functions. Ettool is installed by `bdx_set_ethtool_ops`.

## Control Flow and State
Probe enables PCI, sets a 64-bit DMA mask, maps BAR0, detects one or two ports, allocates one netdev per port, initializes `struct bdx_priv`, reads the MAC address, registers netdev, and leaves carrier/queue stopped. Open resets hardware, creates TX/RX FIFOs and databases, loads firmware `tehuti/bdx.bin`, primes RX buffers, requests the IRQ, enables interrupts, then enables NAPI. Interrupts read `regISR`, schedule NAPI for RX descriptors/TX frees, and process link/error conditions immediately. Poll reclaims TX descriptors, receives packets up to budget, completes NAPI, and reenables interrupts. Close disables NAPI, resets/stops hardware, frees IRQ, and tears down RX/TX DMA resources.

## State and Persistence Behavior
Persistent runtime state is in `struct bdx_priv`: mapped registers, NAPI object, RXD/RXF and TXD/TXF FIFOs, RX skb database, TX DMA/skb circular database, cached FIFO sizes, coalescing register values, stats, port number, and NIC-wide pointer. TX ownership is tracked by `txdb` entries followed by a negative descriptor-size sentinel and skb pointer. RX ownership is tracked by `rxdb` stack entries holding skb DMA mappings. Hardware-visible state is in DMA-coherent FIFO memory and MMIO read/write pointers. Firmware initialization uses `regINIT_SEMAPHORE` so only one function loads firmware for multi-port hardware.

## Dependencies and Integration Points
The file depends on `tehuti.h` register definitions, Linux PCI, netdevice, NAPI, DMA mapping, firmware loader, ethtool, VLAN, and user-copy APIs. It integrates with the network stack through `net_device_ops`, ethtool, `netif_receive_skb`, checksum/VLAN offload flags, and carrier/queue APIs. It exposes a privileged private ioctl path for raw register reads/writes guarded by `CAP_SYS_RAWIO`.

## Risks and Test Signals
High-risk areas include DMA mapping error handling gaps in TX/RX, private register ioctl safety, FIFO wrap copying, descriptor length parsing, reset ordering, IRQ/NAPI races, firmware load timeouts, and multi-port cleanup on partial probe failures. `BDX_ASSERT` is `BUG_ON`, so invariant failures are fatal. Test signals include PCI probe/remove, ifup/ifdown loops, firmware missing/failing paths, high-rate RX/TX with VLAN/TSO/checksum offloads, multicast/promiscuous transitions, ethtool coalesce/ring updates while up, private ioctl permission checks, and two-port adapter cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tehuti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tehuti.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tehuti.h

## Purpose
This header defines the private ABI for the legacy Tehuti driver. It provides compile-time feature switches, driver metadata, FIFO geometry, endian/DMA helpers, register offsets, interrupt/filter bit definitions, descriptor layouts, statistics layout, private driver structures, and debug/assertion macros used by `tehuti.c`.

## Important APIs, Types, and Functions
Key structures are `struct pci_nic`, `struct bdx_priv`, `struct fifo`, `struct rxdb`, `struct txdb`, `struct rxf_desc`, `struct rxd_desc`, `struct pbl`, `struct txd_desc`, and `struct bdx_stats`. Important macros include `READ_REG`, `WRITE_REG`, `CPU_CHIP_SWAP16/32`, `GET_BITS_SHIFT`, interrupt/coalescing helpers, RXD field accessors, `TXD_W1_VAL`, and hardware register constants such as `regISR`, `regIMR`, FIFO config/read/write pointer registers, MAC/VLAN/multicast registers, reset registers, and link status fields.

## Control Flow and State
The header has no direct control flow but encodes the state model used by the C file. `struct bdx_priv` persists all per-port software state, including NAPI, RX/TX FIFOs, descriptor databases, TX flow-control level, coalescing registers, stats, and PCI/netdev back-pointers. FIFO state combines DMA addresses, virtual memory, cached read/write pointers, register offsets, and packet size. Descriptor field macros define how hardware completion data drives RX length, checksum, error, VLAN, and packet-id decisions.

## Dependencies and Integration Points
The header includes Linux module, netdevice, PCI, ethtool, firmware, DMA, VLAN, interrupt, vmalloc, and networking protocol headers. It is tightly coupled to `tehuti.c` and to the specific Bordeaux/Luxor register map. Compile-time switches enable TSO, LLTX, delayed TX write-pointer updates, and optionally MSI when `CONFIG_PCI_MSI` is available.

## Risks and Test Signals
The comment on `struct tx_map` appears inverted relative to driver usage, so maintainers should trust the implementation flow rather than the prose. `BDX_ASSERT` maps to `BUG_ON`, which raises severity of bad descriptor or ring invariants. Register constants and bit masks are brittle; any hardware generation change needs direct validation. Test signals include endian builds, 32-bit and 64-bit DMA builds, descriptor format inspection, interrupt mask behavior, VLAN/multicast programming, and stats name/count agreement with `struct bdx_stats`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tehuti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40.c

## Purpose
This is the modern TN40xx Tehuti PCI ethernet driver. It reuses the FIFO-based hardware model of the legacy Tehuti driver while updating integration to devm allocation, MSI vectors, page_pool RX buffers, phylink link management, MDIO setup, queue statistics, and newer netdev features. It supports TN40xx/TN9510-based adapters and loads `tehuti/bdx.bin`.

## Important APIs, Types, and Functions
Top-level PCI entry points are `tn40_probe`, `tn40_remove`, and `module_pci_driver`. Netdev operations are `tn40_open`, `tn40_close`, `tn40_start_xmit`, `tn40_setmulti`, `tn40_get_stats`, `tn40_set_mac`, and VLAN add/kill. Data-path helpers include `tn40_create_rx_ring`, `tn40_rx_alloc_buffers`, `tn40_rx_receive`, `tn40_create_tx_ring`, `tn40_tx_map_skb`, `tn40_tx_cleanup`, and ring destroy/free helpers. Link and hardware control functions include `tn40_set_link_speed`, `tn40_hw_start`, `tn40_hw_reset`, `tn40_sw_reset`, `tn40_fw_load`, `tn40_restore_mac`, and `tn40_mac_init`. External integration calls `tn40_mdiobus_init`, `tn40_phy_register`, and `tn40_swnodes_cleanup`.

## Control Flow and State
Probe enables PCI, sets 64-bit DMA, requests regions, maps BAR0, allocates netdev, adds NAPI, initializes FIFO sizes/coalescing, resets hardware, allocates MSI vectors, registers MDIO, reads MAC, registers phylink, loads firmware through a temporary TX ring, and registers netdev. Open connects the PHY, software-resets hardware, creates TX/RX rings, fills RX page_pool buffers, requests IRQ, starts hardware, enables NAPI/phylink, and starts the queue. IRQ handling reads masked ISR status, handles link/timer conditions, schedules NAPI for RX/TX, and reenables interrupts when needed. NAPI reclaims TX, receives packets, completes, and reenables interrupts. Close stops phylink, disables/deletes NAPI, disables interrupts, frees IRQ, resets hardware, and destroys rings.

## State and Persistence Behavior
`struct tn40_priv` stores MMIO base, netdev/PCI pointers, NAPI, RX/TX FIFOs, RX database, page_pool, TX database, TX level/write pointer batching state, stats with `u64_stats_sync`, coalescing values, ISR mask, short-packet padding buffer, MDIO bus, PHY device, and phylink. RX pages are allocated from page_pool and handed to the stack through `napi_build_skb`; consumed pages clear the RX database entry, while errored/allocation-failed packets recycle the buffer. TX DMA mappings are stored in `tn40_txdb` and released when TXF acknowledgements arrive.

## Dependencies and Integration Points
The file depends on PCI, netdevice, DMA mapping, firmware loader, phylink, page_pool, NAPI/GRO, VLAN, ethtool link settings, and `netdev_stat_ops`. It includes `tn40.h`, which brings in register definitions and declarations from `tn40_mdio.c` and `tn40_phy.c`. Phylink drives `tn40_set_link_speed`, and MDIO/software-node setup is required before PHY registration.

## Risks and Test Signals
Risk concentrates in TX DMA mapping unwind, page_pool lifetime, FIFO wrap handling, delayed TX write-pointer updates, IRQ/NAPI sequencing, link-speed magic register programming, firmware load serialization, and open/close NAPI lifecycle. `tn40_close` deletes NAPI while probe only adds it once, so repeated open/close behavior is an important regression signal. Tests should cover module probe/remove, firmware missing and valid paths, PHY discovery failure, ifup/ifdown cycles, link speed changes, high-rate RX/TX with TSO/VLAN/checksum/GRO, short packets, multicast/promiscuous filters, and queue stats under concurrent traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40.h

## Purpose
This header defines the shared private interface for the TN40xx driver objects. It provides driver constants, FIFO and descriptor structures, TX/RX bookkeeping structures, software-node metadata containers, `struct tn40_priv`, register access helpers, and declarations shared by `tn40.c`, `tn40_mdio.c`, and `tn40_phy.c`.

## Important APIs, Types, and Functions
Key types include `struct tn40_fifo`, `struct tn40_rxdb`, `struct tn40_txdb`, `struct tn40_nodes`, `struct tn40_priv`, RX/TX descriptor structs, and `union tn40_tx_dma_addr`. Important macros are `TN40_INT_REG_VAL`, `TN40_GET_RXD_*`, `TN40_TXD_W1_VAL`, FIFO constants, descriptor sizes, and `NODE_PROP`/`NODE_PAR_PROP` for software-node construction. Inline APIs are `tn40_read_reg` and `tn40_write_reg`. Cross-file declarations are `tn40_set_link_speed`, `tn40_swnodes_cleanup`, `tn40_mdiobus_init`, `tn40_phy_register`, and `tn40_phy_unregister`.

## Control Flow and State
The header does not execute code beyond simple MMIO accessors, but it defines how state is shared. `tn40_priv` is the central per-device state container for netdev, PCI, software nodes, NAPI, RX/TX FIFOs, page_pool, databases, stats, coalescing, interrupt mask, short-packet buffer, MDIO, PHY, and phylink configuration. Descriptor structures define hardware-visible layout for RX free, RX data, TX data, and TX free entries.

## Dependencies and Integration Points
The file includes Linux software-node property support and `tn40_regs.h`. It integrates the main data path with MDIO and phylink code through declarations and shared `tn40_priv`. It also couples netdev feature behavior to descriptor fields: VLAN, checksum, large-send, and packet buffer list encoding all use macros defined here.

## Risks and Test Signals
Register accessors are thin wrappers around `readl/writel`, so ordering depends on callers adding barriers where needed. `TN40_REG_CTRLST_BASE` in `tn40_regs.h` references `REG_CTRLST_PRM_ENA`, a suspicious unprefixed macro, though this particular macro may be unused. Test signals include compile coverage for all TN40 objects, descriptor layout checks, 32/64-bit DMA builds, VLAN tag encoding, phylink/MDIO interaction, and page_pool RX lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_mdio.c

## Purpose
This file implements the TN40xx clause 45 MDIO bus backend and software-node registration for AQR105-based cards. It gives phylib/phylink a normal `mii_bus` interface even though the PHY is reached through TN40 MMIO MDIO registers, and it advertises AQR105 PHY firmware `tehuti/aqr105-tn40xx.cld`.

## Important APIs, Types, and Functions
Public functions are `tn40_mdiobus_init` and `tn40_swnodes_cleanup`. Internal helpers include `tn40_mdio_set_speed`, `tn40_mdio_wait_nobusy`, `tn40_mdio_read`, `tn40_mdio_write`, `tn40_mdio_read_c45`, `tn40_mdio_write_c45`, and `tn40_swnodes_register`. MDIO command encoding uses `TN40_MDIO_CMD_VAL`, `TN40_MDIO_CMD_READ`, device/address masks, and busy/error field helpers from `tn40_regs.h`.

## Control Flow and State
`tn40_mdiobus_init` allocates a devm MDIO bus, assigns clause 45 read/write callbacks, stores it in `priv->mdio`, conditionally registers software nodes for TN9510/AQR105 cards, configures MDIO speed to 6 MHz, and registers the bus. Reads wait for non-busy, write device/port and register address, issue a read command, wait again, and return low 16 bits of `TN40_REG_MDIO_DATA`. Writes perform the same address setup, write data, wait for completion, and fail if the MDIO read-error bit is set. Cleanup removes firmware-node references only for cards that installed software nodes.

## Dependencies and Integration Points
The file depends on `tn40.h`, Linux PCI, netdevice, phylink, software-node, and MDIO APIs. The software node describes a child `ethernet-phy@1` with compatible `ethernet-phy-id03a1.b4a3`, `reg = 1`, and firmware name, enabling phylib to discover and configure the PHY without firmware/DT/ACPI platform description.

## Risks and Test Signals
Risks include atomic polling timeouts, cleanup ordering for software nodes, hard-coded PHY address/compatible, AQR105-only assumptions tied to PCI device ID, and MDIO error reporting only after writes. Tests should cover MDIO read/write timeouts, successful PHY discovery, firmware-name propagation, probe failure after software-node registration, remove cleanup, and TN9510 versus non-TN9510 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_phy.c

## Purpose
This file binds TN40xx MAC control to the Linux phylink framework. It discovers the first PHY on the MDIO bus, creates a phylink instance for an XAUI netdev MAC, and maps link-up/link-down callbacks to TN40 MAC speed programming and netdev queue state.

## Important APIs, Types, and Functions
Public functions are `tn40_phy_register` and `tn40_phy_unregister`. Internal callbacks are `tn40_link_up`, `tn40_link_down`, `tn40_mac_config`, and `tn40_config_to_priv`. `tn40_mac_ops` supplies those callbacks to `phylink_create`.

## Control Flow and State
Registration calls `phy_find_first` on `priv->mdio`, initializes `priv->phylink_config` with `PHYLINK_NETDEV`, `MAC_10000FD`, and XAUI support, creates phylink, and stores `phydev`/`phylink` in `tn40_priv`. On link up, phylink calls `tn40_set_link_speed` with the negotiated speed and wakes the queue. On link down, it stops the queue and programs speed 0. Unregister destroys the phylink object.

## Dependencies and Integration Points
The file depends on `tn40.h`, Linux PCI/netdevice, phylink, and phylib. It integrates with `tn40_open`/`tn40_close`, which connect/disconnect and start/stop phylink, and with `tn40_set_link_speed` in `tn40.c`, which applies low-level PCS/MAC register sequences.

## Risks and Test Signals
Only `MAC_10000FD` is advertised even though `tn40_set_link_speed` has register sequences for 100M, 1G, 2.5G, 5G, and 10G, so capability modeling may be narrower than hardware. `tn40_mac_config` is empty, so interface changes rely entirely on link-up programming. Tests should cover missing PHY, XAUI mode negotiation, link up/down queue transitions, speed changes, and phylink destroy on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_regs.h

## Purpose
This header names the TN40xx MMIO register map and bit fields used by the TN40 driver. It covers FIFO configuration/read/write pointers, interrupt registers, firmware initialization registers, MAC/VLAN/multicast registers, MDIO registers, reset controls, RX filter bits, frame-size fields, and PLL lock/reset bits.

## Important APIs, Types, and Functions
The file exports constants only. Important groups are `TN40_REG_TXD_*`, `TN40_REG_RXF_*`, `TN40_REG_RXD_*`, `TN40_REG_TXF_*`, `TN40_REG_ISR/IMR/ISR_MSK0`, `TN40_REG_INIT_SEMAPHORE`, `TN40_REG_INIT_STATUS`, `TN40_REG_MDIO_*`, `TN40_REG_CTRLST`, `TN40_REG_RST_*`, `TN40_REG_DIS_*`, interrupt bits such as `TN40_IR_RX_DESC_0` and `TN40_IR_TX_FREE_0`, RX filter bits such as `TN40_GMAC_RX_FILTER_*`, and helpers `TN40_GET_MDIO_BUSY`/`TN40_GET_MDIO_RD_ERR`.

## Control Flow and State
There is no direct control flow. The constants define how `tn40.c` persists hardware state: FIFO base addresses, cached software pointers, hardware pointer registers, interrupt masks/status, MAC filters, VLAN tables, reset state, MDIO transactions, and PLL lock detection. The combined `TN40_IR_EXTRA` mask controls which non-data-path interrupts receive extra handling.

## Dependencies and Integration Points
This file is included by `tn40.h`, making its constants available to all TN40 module objects. It depends on bitfield macros from Linux headers included before use. It is coupled to magic register programming in `tn40_set_link_speed`, `tn40_hw_start`, and `tn40_sw_reset`, some of which uses raw offsets not named here.

## Risks and Test Signals
Register-map mistakes are severe because they can corrupt hardware state. `TN40_REG_CTRLST_BASE` references `REG_CTRLST_PRM_ENA` instead of `TN40_REG_CTRLST_PRM_ENA`, which is a latent compile risk if the macro is used. Tests should include allmodconfig/randconfig compile coverage, MDIO transaction checks, interrupt mask behavior, reset sequencing, VLAN/multicast programming, and hardware smoke tests for link and traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/tehuti/tn40_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/Kconfig

## Purpose
This Kconfig fragment defines the Texas Instruments ethernet driver menu and build options for DaVinci EMAC/MDIO, CPSW, K3 AM65 CPSW NUSS, CPTS timestamping, QoS offload, Keystone NETCP, ThunderLAN, ICSSG, ICSS IEP, and PRU Ethernet drivers.

## Important APIs, Types, and Functions
Important symbols include `NET_VENDOR_TI`, `TI_DAVINCI_EMAC`, `TI_DAVINCI_MDIO`, `TI_CPSW`, `TI_CPSW_SWITCHDEV`, `TI_CPTS`, `TI_K3_CPPI_DESC_POOL`, `TI_K3_AM65_CPSW_NUSS`, `TI_K3_AM65_CPSW_SWITCHDEV`, `TI_K3_AM65_CPTS`, `TI_AM65_CPSW_QOS`, `TI_KEYSTONE_NETCP`, `TI_KEYSTONE_NETCP_ETHSS`, `TLAN`, `TI_ICSSG_PRUETH`, `TI_ICSSG_PRUETH_SR1`, `TI_ICSS_IEP`, and `TI_PRUETH`.

## Control Flow and State
There is no runtime control flow. Build-time state determines which driver objects compile and which helper subsystems are selected. For the researched `am65-cpsw-ethtool.c`, the critical parent is `TI_K3_AM65_CPSW_NUSS`, which selects `NET_DEVLINK`, `TI_DAVINCI_MDIO`, `PHYLINK`, `PAGE_POOL`, and `TI_K3_CPPI_DESC_POOL`; optional timestamping and QoS behavior are controlled by `TI_K3_AM65_CPTS` and `TI_AM65_CPSW_QOS`.

## Dependencies and Integration Points
The file models architecture and subsystem requirements for many TI ethernet families. AM65 CPSW depends on `ARCH_K3`, OF, and TI UDMA glue, and conditionally integrates CPTS and QoS features. ICSSG/PRU options depend on remoteproc, switchdev, PTP optional support, and firmware-running PRU cores.

## Risks and Test Signals
Kconfig risk is dependency skew: missing `select`/`depends on` entries can break randconfig or expose unusable options. Optional QoS and CPTS dependencies affect ethtool code paths for timestamping and MAC Merge/IET. Tests should include randconfig, `COMPILE_TEST` where applicable, AM65 CPSW builds with and without CPTS/QoS/switchdev, and module/built-in combinations for shared objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/Makefile

## Purpose
This Makefile maps TI ethernet Kconfig symbols to objects and composite modules. It defines shared CPSW components, K3 AM65 CPSW module composition, Keystone NETCP modules, ICSSG/ICSSM components, and standalone legacy drivers.

## Important APIs, Types, and Functions
Important build variables include `ti-cpsw-common-y`, `ti-cpsw-priv-y`, `ti-cpsw-ale-y`, `ti-cpsw-sl-y`, `ti_cpsw-y`, `ti_cpsw_new-y`, `keystone_netcp-y`, `keystone_netcp_ethss-y`, `ti-am65-cpsw-nuss-y`, `icssg-prueth-y`, `icssg-prueth-sr1-y`, and `icssg-y`. The researched `am65-cpsw-ethtool.c` is linked through `ti-am65-cpsw-nuss-y := am65-cpsw-nuss.o am65-cpsw-ethtool.o`.

## Control Flow and State
There is no runtime state. Build composition determines which translation units share module scope. `ti-am65-cpsw-nuss-$(CONFIG_TI_AM65_CPSW_QOS)` conditionally includes `am65-cpsw-qos.o`, and `ti-am65-cpsw-nuss-$(CONFIG_TI_K3_AM65_CPSW_SWITCHDEV)` conditionally includes switchdev support. The base AM65 module always includes the ethtool implementation.

## Dependencies and Integration Points
The Makefile integrates Kconfig selections with shared support code such as ALE, CPDMA, CPTS, CPTS for AM65, K3 CPPI descriptor pools, ICSSG classifiers/stats/config, and switchdev objects. It is the linkage point ensuring ethtool ops can reference AM65 NUSS headers and optional QoS symbols guarded by Kconfig checks.

## Risks and Test Signals
Object-list drift can produce unresolved references or missing feature registration. Conditional AM65 QoS/switchdev object inclusion should match Kconfig feature guards in code. Test signals include `CONFIG_TI_K3_AM65_CPSW_NUSS=m/y` builds with `CONFIG_TI_AM65_CPSW_QOS` on/off, switchdev on/off, and build checks for shared objects not being duplicated across incompatible modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-ethtool.c

## Purpose
This file implements ethtool operations for the TI K3 AM65 CPSW NUSS ethernet driver. It exposes driver identity, message level, channel counts, ring parameters, pause/WOL/link/EEE through phylink, register dumps, statistics, timestamping capabilities, private flags, interrupt coalescing, and MAC Merge/IET frame preemption controls.

## Important APIs, Types, and Functions
The exported object is `am65_cpsw_ethtool_ops_slave`. Important internal types are `struct am65_cpsw_regdump_hdr`, `struct am65_cpsw_regdump_item`, `struct am65_cpsw_stats_regs`, and `struct am65_cpsw_ethtool_stat`. Key functions include runtime PM wrappers `am65_cpsw_ethtool_op_begin/complete`, stats string/count/data helpers, `am65_cpsw_get_regs_len`, `am65_cpsw_get_regs`, phylink forwarding helpers, `am65_cpsw_get_ethtool_ts_info`, private flag get/set, MAC Merge helpers `am65_cpsw_get_mm`, `am65_cpsw_set_mm`, `am65_cpsw_get_mm_stats`, and queue coalescing get/set routines.

## Control Flow and State
Ettool calls begin by runtime-resuming the device and complete by putting PM runtime. Driver/link settings are read from `am65_cpsw_common`, `am65_cpsw_ndev_priv`, slave data, host port, and active port structures. Register dump length is computed from static ranges plus dynamic ALE table size; dump output serializes module ID, length, register offset/value pairs, and ALE table contents. Stats use static offset tables into host and slave stat MMIO. Channel changes are rejected while `common->usage_count` indicates active interfaces. Coalescing stores microsecond values as nanosecond pacing timeouts per TX channel/RX flow. Private flag changes are rejected while active and when round-robin RX packet-type mode conflicts with QoS EST.

## State and Persistence Behavior
The file mutates `priv->msg_enable`, `common->tx_ch_num`, `common->rx_ch_num_flows` via `am65_cpsw_nuss_update_tx_rx_chns`, `common->pf_p0_rx_ptype_rrobin`, per-channel pacing timeouts, and MAC Merge state in port IET registers and `port->qos.iet`. `am65_cpsw_set_mm` also saves/restores original FIFO `MAX_BLKS`, toggles PMAC/TX preemption bits, updates verification mode/time, and commits preemptible traffic classes. Statistics and register dumps are read-only snapshots of hardware state.

## Dependencies and Integration Points
The file depends on `am65-cpsw-nuss.h`, `am65-cpsw-qos.h`, `cpsw_ale.h`, `am65-cpts.h`, phylink, runtime PM, platform device, and timestamping headers. It integrates with phylink for pause, WOL, link settings, EEE, and nway reset; with CPTS for PHC/timestamp reporting; with ALE for table dumps; and with QoS/IET helpers for frame preemption. `IS_ENABLED` guards keep timestamping/QoS behavior optional at compile time.

## Risks and Test Signals
Risks include register dump length/index accounting, runtime PM imbalance, channel changes racing active traffic, private flag/QoS conflicts, coalescing unit conversion and minimum validation, MM/IET register sequencing, and optional config combinations. In `am65_cpsw_get_regs`, the ALE-table branch advances `pos` by a byte length even though `reg` is a `u32 *`, which deserves scrutiny. Tests should cover `ethtool -i`, `-S`, `-d`, `-l/-L`, `-c/-C` including per-queue, phylink settings, timestamping with/without CPTS, private flag toggles while down/up, MM get/set/stats with QoS on/off, and runtime PM failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/am65-cpsw-ethtool.c -->
