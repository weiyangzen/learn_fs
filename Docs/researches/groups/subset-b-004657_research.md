# subset-b-004657 research

Grouped research report for the Sun Ethernet driver files in `sources/distributed-fs/ceph-client/drivers/net/ethernet/`. Each file section preserves the source path and is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sungem.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sungem.h

## Purpose
`sungem.h` is the hardware and driver-state contract for the Sun GEM gigabit Ethernet driver. It does not implement executable logic; it defines the register map, bit fields, DMA descriptor formats, ring sizing rules, PHY/link state enumerations, and `struct gem` private state that the GEM implementation uses to program the ASIC and track runtime network state.

## Important APIs, Types, And Constants
- Global, TX DMA, RX DMA, WOL, MAC, MIF, PCS, and PROM register offsets are declared as `GREG_*`, `TXDMA_*`, `RXDMA_*`, `WOL_*`, `MAC_*`, `MIF_*`, `PCS_*`, and `PROM_*`.
- Interrupt and error masks include `GREG_STAT_ABNORMAL`, `GREG_STAT_NAPI`, MAC status/mask fields, PCI error fields, and PCS link-change fields.
- `struct gem_txd` and `struct gem_rxd` are 64-bit little-endian descriptor layouts. TX descriptors are read by hardware and not written back, while RX descriptors include status ownership and receive metadata.
- Descriptor control masks such as `TXDCTRL_*` and `RXDCTRL_*` describe checksum offload, SOF/EOF, interrupt request, buffer length, ownership, hash status, alternate MAC match, and CRC failure.
- Ring constants `TX_RING_SIZE`, `RX_RING_SIZE`, `TXDMA_CFG_BASE`, `RXDMA_CFG_BASE`, `NEXT_TX`, `NEXT_RX`, `TX_BUFFS_AVAIL`, `RX_BUF_ALLOC_SIZE`, and `RX_COPY_THRESHOLD` encode sizing and wraparound behavior.
- `struct gem_init_block` co-locates TX and RX descriptor rings in one DMA-visible block.
- `enum gem_phy_type` distinguishes MDIO0, MDIO1, serialink, and SERDES modes. `enum link_state` models link negotiation from down through autoneg, forced fallback, and up.
- `struct gem` is the main private state: MMIO base, TX/RX ring indexes, NAPI object, FIFO sizing, pause state, reset work, PHY state, DMA block, SKB arrays, PCI device, netdev, and optional Open Firmware node.
- `found_mii_phy(gp)` checks whether a usable MII PHY definition is present for MDIO PHY modes.

## Control Flow And State Behavior
This header encodes constraints that control the implementation flow. Global reset bits must be polled until clear before programming other GEM blocks. TX uses kick/completion registers instead of a descriptor ownership bit; the driver advances `tx_new` and hardware completion advances `tx_old`. RX buffers must be posted in aligned groups, with ownership set only after the buffer address is valid. The `struct gem` state persists only in kernel memory for the life of a probed device and is reinitialized on driver reset, suspend/resume, or module unload paths implemented elsewhere.

## Dependencies And Integration Points
The file depends on Linux networking, PCI, DMA, NAPI, timer, workqueue, PHY/MII, and platform/Open Firmware types included by the implementation. It integrates with the GEM C driver by defining the MMIO ABI and private state layout. The hardware contract also influences netdev feature support: checksum fields, pause registers, WOL fields, and link negotiation state all map to ethtool and netdev behavior in the implementation.

## Risks And Edge Cases
- Hardware ordering matters: descriptor address and status fields must be programmed in the order expected by the ASIC.
- TX and RX descriptor alignment is strict. Ring size constants must stay in the legal hardware set or compile-time `#error` guards fire.
- RX ring posting cannot wrap freely and has alignment/grouping constraints, so off-by-one ring accounting can starve receive buffers.
- Several register comments call out self-clearing or read-to-clear side effects. Incorrect reads can lose interrupt status.
- The 64-bit descriptor control masks require careful endian handling in implementation code.

## Test Signals
Useful signals include successful driver compile with the selected ring sizes, boot/probe on GEM hardware, NAPI RX/TX interrupt behavior, ethtool link reporting, RX checksum validation, TX checksum offload, WOL configuration, reset recovery, and stress tests around ring wrap and RX no-buffer interrupts. Static analysis should focus on descriptor endian conversions and ring index arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sungem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunhme.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunhme.c

## Purpose
`sunhme.c` implements the Sun Happy Meal Ethernet 10/100 driver for SBUS and PCI variants, including single-port HME and four-port Quattro/QFE cards. It owns device probing, MAC address discovery, register mapping, reset and initialization, PHY/MII access, autonegotiation and forced-link fallback, interrupt-driven RX/TX, multicast filters, ethtool operations, and module registration.

## Important APIs, Types, And Functions
- Module interface: `module_param_array(macaddr, ...)`, `happy_meal_probe()`, `happy_meal_exit()`, conditional SBUS and PCI driver registration, and PCI/OF match tables.
- Bus abstraction helpers: `sbus_hme_*`, `pci_hme_*`, `hme_write32`, `hme_read32`, `hme_write_rxd`, `hme_write_txd`, and `hme_read_desc32` handle endian and bus differences.
- PHY/MIF access: `happy_meal_bb_read()`, `happy_meal_bb_write()`, `happy_meal_tcvr_read()`, and `happy_meal_tcvr_write()` support bit-bang and frame-mode MII access.
- Link management: `happy_meal_begin_auto_negotiation()`, `happy_meal_timer()`, `try_next_permutation()`, `set_happy_link_modes()`, `display_link_mode()`, and `display_forced_link_mode()` implement autonegotiation, forced fallback, and BigMAC duplex updates.
- Hardware lifecycle: `happy_meal_stop()`, `happy_meal_tx_reset()`, `happy_meal_rx_reset()`, `happy_meal_tcvr_reset()`, `happy_meal_transceiver_check()`, `happy_meal_init_rings()`, `happy_meal_clean_rings()`, and `happy_meal_init()`.
- Data path: `happy_meal_interrupt()`, `happy_meal_tx()`, `happy_meal_rx()`, `happy_meal_start_xmit()`, `unmap_partial_tx_skb()`, `happy_meal_tx_timeout()`, `happy_meal_open()`, and `happy_meal_close()`.
- Netdev and ethtool integration: `hme_netdev_ops`, `hme_ethtool_ops`, `happy_meal_get_stats()`, `happy_meal_set_multicast()`, `hme_get_link_ksettings()`, `hme_set_link_ksettings()`, `hme_get_drvinfo()`, and `hme_get_link()`.
- Probe support: `happy_meal_addr_init()`, `happy_meal_common_probe()`, `happy_meal_sbus_probe_one()`, `happy_meal_pci_probe()`, `quattro_sbus_find()`, `quattro_pci_find()`, `is_quattro_p()`, and `find_eth_addr_in_vpd()`.

## Control Flow
Probe allocates an Ethernet netdev, resolves SBUS or PCI resources, maps global/TX/RX/BigMAC/MIF register windows, assigns MAC address, initializes locks and Quattro parent membership, allocates one coherent descriptor page, sets netdev operations/features, primes PHY advertisement, and registers the netdev. `ndo_open` requests the shared IRQ and calls `happy_meal_init()` under `happy_lock`. Initialization stops hardware, clears and refills rings, configures MIF access mode, detects internal/external transceiver, resets PHY and BigMAC, writes MAC and hash filters, programs DMA ring pointers and burst size, enables TX/RX DMA and BigMAC, and starts the link timer.

Interrupt handling reads `GREG_STAT` once, handles fatal errors through `happy_meal_is_not_so_happy()` and reset, reclaims TX on `TXALL`, and drains RX on `RXTOHOST`. TX maps the linear area and fragments into descriptors; fragment descriptors are written before the first descriptor to avoid hardware racing a partially populated packet. RX either passes the DMA SKB upward for large packets after replacing the ring buffer, or copies small packets into a fresh SKB and reuses the DMA buffer. Close stops hardware, frees RX/TX SKBs and DMA mappings, deletes the autoneg timer, and releases the IRQ.

## State And Persistence
All persistent runtime state lives in `struct happy_meal`: register bases, DMA coherent descriptor block, SKB rings, ring indexes, PHY software shadow registers, link timer state, flags, bus identity, and Quattro membership. There is no disk persistence. Module parameter `macaddr` is process-global module state and increments the last byte after assignment. Quattro parent lists are global in-memory lists and are freed at module exit. Device-managed allocations are used for many probe resources, while the Quattro membership array is manually cleared on probe failure.

## Dependencies And Integration Points
The driver depends on Linux netdev, ethtool, DMA mapping, SKB, CRC multicast hashing, timers, PCI, platform/OF, and SPARC SBUS support. It consumes definitions from `sunhme.h`. It integrates with Open Firmware names `SUNW,hme`, `SUNW,qfe`, and `qfe`, PCI ID `PCI_DEVICE_ID_SUN_HAPPYMEAL`, idprom MAC fallback on SPARC, PCI ROM VPD MAC lookup off-SPARC, and netdev features `NETIF_F_SG`, `NETIF_F_HW_CSUM`, and `NETIF_F_RXCSUM`.

## Risks And Edge Cases
- The hardware has documented write, parity, and reset quirks. The driver contains retries, rereads, and low-bit ring-pointer workarounds that must not be simplified without hardware validation.
- `unmap_partial_tx_skb()` advances neither `first_entry` inside its loop in the visible source, which is a high-risk area for DMA mapping failure handling if exercised.
- The driver is interrupt-driven, not NAPI, so high RX rates can spend a long time in IRQ context.
- Autonegotiation and forced fallback are timer-driven under `happy_lock`; reset paths must delete or restart the timer carefully.
- Descriptor ordering is critical: address writes must precede ownership flags and use `dma_wmb()`.
- Global `macaddr` assignment can generate sequential addresses and is not per-device isolated.
- Quattro parent tracking must stay synchronized with failed probes and module exit to avoid stale pointers.

## Test Signals
Important signals include SBUS and PCI probe/remove, QFE four-port detection, open/close cycles, IRQ sharing, TX with and without fragments, DMA mapping failure injection, RX small-copy and large-buffer replacement paths, multicast/promiscuous/allmulti changes, ethtool autoneg and forced speed/duplex settings, TX timeout reset, link-down forced-mode fallback, and module unload with Quattro lists populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunhme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunhme.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunhme.h

## Purpose
`sunhme.h` defines the register, descriptor, ring, transceiver, and private-state layout for the Happy Meal Ethernet driver implemented in `sunhme.c`. It is the ABI map for the HME global, external TX/RX, BigMAC, and transceiver register blocks and the software contract for descriptor rings and device state.

## Important APIs, Types, And Constants
- Register offsets and bit masks are grouped by global registers (`GREG_*`), TX DMA (`ETX_*`), RX DMA (`ERX_*`), BigMAC (`BMAC_*` and `BIGMAC_*`), transceiver MIF (`TCVR_*` and `TCV_*`), and DP83840 PHY-specific fields.
- Descriptor types `struct happy_meal_rxd` and `struct happy_meal_txd` use `hme32` fields and masks `RXFLAG_*` and `TXFLAG_*` for ownership, size, checksum, SOP/EOP, and checksum offload placement.
- Ring constants define 32-entry active TX/RX rings, 256-entry maximum descriptor arrays, wrap macros, TX availability, RX alignment offset, allocation size, and copy threshold.
- `struct hmeal_init_block` stores full RX/TX descriptor arrays in one DMA block and `hblock_offset()` computes hardware-visible offsets.
- `enum happy_transceiver` and `enum happy_timer_state` define PHY source and link timer states.
- `struct happy_meal` stores register bases, bus access function pointers when both SBUS and PCI are compiled, DMA device, lock, SKB rings, ring indexes, PHY shadows, timer state, netdev backpointer, and Quattro metadata.
- `struct quattro` tracks four child `net_device` instances and parent bus object for QFE cards.
- `happy_meal_alloc_skb()` wraps `alloc_skb()` to reserve enough headroom for 64-byte alignment.

## Control Flow And State Behavior
The macros in this header directly shape `sunhme.c` control flow. RX initialization allocates aligned SKBs, writes RX descriptor address before ownership, and reserves `RX_OFFSET` so the IP header is aligned. TX uses one descriptor per linear area or fragment and ring availability is calculated by `TX_BUFFS_AVAIL`. Timer states move from arbitration wait to link-up wait, forced-mode try wait, or asleep. `happy_flags` records hardware feature and runtime mode decisions such as frame-mode MIF, Lance mode, RX enable, autoneg/full duplex, PCI, and Quattro membership.

## Dependencies And Integration Points
The header includes `<linux/pci.h>` for PCI-visible private state. It also relies on netdev, timer, SKB, DMA, platform, and SPARC-specific types included by the C file. It integrates with Linux MII definitions, BigMAC register programming, SBUS/PCI bus accessors, and ethtool link settings through the fields cached in `struct happy_meal`.

## Risks And Edge Cases
- The descriptor write-order comment is a correctness requirement for DMA races.
- Ring constants have compile-time legal-value checks, but the 256-entry descriptor arrays are larger than the active 32-entry rings; code must consistently use the active size for wrap and availability.
- `happy_meal_alloc_skb()` alignment relies on extra allocation headroom and must be paired with the RX offset programming.
- `struct happy_meal` contains conditional function pointers only when both CONFIG_SBUS and CONFIG_PCI are enabled; code paths must match compilation mode.
- `happy_flags` is a bitfield-style integer with hardware revision quirks encoded by masks, so adding flags risks collisions.

## Test Signals
Validation should include building SBUS-only, PCI-only, and combined configurations; descriptor endian behavior on PCI; RX buffer alignment checks; Quattro slot assignment; and runtime assertions around ring indexes, timer states, and feature flags during open, reset, ethtool changes, and close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunhme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunqe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunqe.c

## Purpose
`sunqe.c` implements the Sun QuadEthernet 10baseT SBUS driver. One QEC controller owns shared global registers and interrupt delivery for up to four QE/MACE channels; each channel is exposed as a Linux Ethernet netdev with PIO/register initialization, coherent descriptor and packet buffers, interrupt-driven RX, lazy TX reclaim, multicast filter programming, ethtool link reporting, and platform-driver lifecycle.

## Important APIs, Types, And Functions
- Module and driver entry: `qec_init()`, `qec_exit()`, `qec_sbus_driver`, OF match table for `"qe"`, and global `root_qec_dev`.
- QEC lifecycle: `qec_global_reset()`, `qec_init_once()`, `qec_get_burst()`, and `get_qec()` allocate/map the shared controller, validate MACE mode, reset QEC, configure local memory partitioning and burst mode, request the shared IRQ, and publish the parent in platform data.
- Channel lifecycle: `qe_stop()`, `qe_init_rings()`, `qe_init()`, `qe_open()`, `qe_close()`, `qec_ether_init()`, and `qec_sbus_remove()`.
- Data path: `qec_interrupt()`, `qe_rx()`, `qe_tx_reclaim()`, `qe_start_xmit()`, and `qe_tx_timeout()`.
- Error handling: `qe_is_bolixed()` decodes QEC/MACE status bits, updates netdev stats, and resets the channel for lockup-prone conditions.
- Multicast and ethtool: `qe_set_multicast()`, `qe_get_drvinfo()`, `qe_get_link()`, `qe_ethtool_ops`, and `qec_ops`.

## Control Flow
Each `"qe"` platform child probes through `qec_ether_init()`. It allocates an Ethernet netdev, gets the `channel#`, obtains or creates the parent QEC via `get_qec()`, maps per-channel QEC and MACE registers, allocates coherent descriptor and packet-buffer memory, stops the channel, installs netdev and ethtool ops, and registers the netdev. The first child for a QEC maps global registers, confirms MACE mode, resets the controller, computes burst capabilities from OF properties, partitions local memory into channel RX/TX FIFO areas, and requests the shared IRQ.

`ndo_open` sets the base MACE config and calls `qe_init()`, which resets MACE and QEC channel, writes descriptor ring addresses, masks/unmasks RX/TX/error interrupts, positions local-memory FIFO pointers by channel, programs MACE PHY/TX/RX/FIFO/address registers, clears multicast filter state, initializes rings, waits briefly for link, clears missed counters, and calls `qe_set_multicast()` to enable TX/RX. The shared IRQ reads QEC global status nibble by nibble, services each active child, processes errors first, drains RX descriptors, and only reclaims TX/wakes the queue when TX interrupts were enabled because the queue had filled.

TX copies SKB data into coherent per-channel TX buffers, writes one descriptor, wakes the channel, updates stats, and frees the SKB immediately. RX copies from coherent RX buffers into newly allocated SKBs, reposts descriptors at the delayed mirror position, and updates stats.

## State And Persistence
`struct sunqec` persists per physical QEC while loaded: global MMIO, four child pointers, burst capabilities, OF platform device, and root list linkage. `struct sunqe` persists per channel: register bases, coherent descriptor block, coherent packet buffers, ring cursors, lock, parent pointer, MACE config, channel number, platform device, and netdev. There is no disk state. MAC address comes from SPARC `idprom`, so channels initially share that base address unless platform firmware or external mechanisms adjust it.

## Dependencies And Integration Points
The driver depends on SPARC SBUS helpers, Open Firmware properties/resources, DMA coherent allocation, Linux netdev/ethtool/SKB APIs, CRC multicast hashing, and idprom. It consumes the register and state definitions in `sunqe.h`. It integrates with one shared QEC IRQ and with child `"qe"` OF nodes under a parent QEC resource.

## Risks And Edge Cases
- The shared interrupt assumes `qecp->qes[channel]` exists for any status nibble; partial probe or unexpected hardware status could expose null child pointers.
- The TX path copies into fixed `PKT_BUF_SZ` buffers and does not visibly guard against oversized SKBs beyond normal Ethernet MTU assumptions.
- RX and TX are interrupt-driven without NAPI; high packet rates can increase IRQ load.
- `qe_set_multicast()` stops and wakes the queue without taking `qep->lock`, relying on netdev serialization and hardware behavior.
- Error paths reset the channel from IRQ context for several MACE lockup conditions.
- Parent QEC lifetime is global and freed at module exit, while child remove frees channel resources; ordering must remain platform-driver controlled.

## Test Signals
Test with SPARC/SBUS builds, OF probe with four channels, shared IRQ dispatch, open/close, link-state reporting from `MREGS_PHYCONFIG`, TX queue full and wake behavior, TX timeout reset, RX under allocation failure, multicast/allmulti/promiscuous transitions, and module unload after multiple QEC instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunqe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunqe.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunqe.h

## Purpose
`sunqe.h` is the hardware map and private-state definition header for the Sun QuadEthernet SBUS driver. It describes QEC global registers, per-channel QEC registers, AMD 79C940 MACE registers, descriptor layouts, fixed ring/buffer geometry, and the parent/child state objects used by `sunqe.c`.

## Important APIs, Types, And Constants
- QEC global register offsets and masks: `GLOB_*`, `GLOB_CTRL_*`, `GLOB_STAT_*`, packet/local-memory sizing fields, and `GLOB_STAT_PER_QE()`.
- Per-channel QEC fields: `CREG_*`, control bits, status/error masks, QEC error masks, MACE error masks, and inter-frame-gap controls.
- MACE register offsets and bit masks: `MREGS_*`, including TX/RX frame controls/status, interrupt masks, BIU/FIFO/MAC/PLS/PHY config, internal address config, filter, counters, and test bits.
- Descriptor types `struct qe_rxd` and `struct qe_txd` plus `RXD_*` and `TXD_*` ownership, update, SOP/EOP, and length masks.
- Ring and buffer geometry: active 16-entry rings in 256-entry descriptor arrays, `NEXT_*` and `PREV_*` wrap over max-size descriptors, `TX_BUFFS_AVAIL`, `PKT_BUF_SZ`, `RXD_PKT_SZ`, `struct qe_init_block`, and `struct sunqe_buffers`.
- State containers: `struct sunqec` for a global QEC and `struct sunqe` for one channel/netdev.

## Control Flow And State Behavior
This header encodes the two-level hardware model. `struct sunqec` represents the parent QEC and points to four `struct sunqe` channels. Each child has its own QEC channel registers, MACE registers, coherent descriptor block, coherent packet buffers, and RX/TX cursors. RX descriptors are preposted with `RXD_OWN`; TX descriptors are populated on demand and reclaimed lazily. The QEC local memory layout is computed in the C file from global memory-size registers and channel numbers.

## Dependencies And Integration Points
The header is consumed by `sunqe.c` and assumes SBUS-style register access and DMA-visible 32-bit addresses. It integrates with Linux netdev state through the `struct net_device *` member, with platform/OF through `struct platform_device *`, and with the parent QEC interrupt fan-out through the `qes[4]` array.

## Risks And Edge Cases
- `NEXT_RX()` and `NEXT_TX()` wrap over `*_RING_MAXSIZE` rather than active ring size; this supports delayed descriptor reposting but requires careful masking when indexing the fixed packet buffers.
- Packet buffers are fixed-size arrays; MTU assumptions must match `PKT_BUF_SZ` and `TXD_LENGTH`/`RXD_LENGTH` limits.
- Register masks are dense and hardware-specific; incorrect masks can disable interrupts or miss fatal DMA errors.
- Parent/child pointers have no reference counting in the structures themselves, relying on platform-driver and module ordering.

## Test Signals
Build coverage should compile the header with `sunqe.c` on SPARC. Runtime signals include correct QEC global mode detection, channel number assignment, ring cursor wrap through 256 descriptors, multicast hash programming, MACE link status reads, and per-channel stats updates under shared IRQ load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunqe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet.c

## Purpose
`sunvnet.c` is the Sun LDOM virtual network driver front end. It creates and manages Linux netdevs for virtual networks described by the SPARC machine description, probes `vnet-port` VIO devices, assigns ports to parent vnets by local MAC address, chooses transmit ports/queues, exposes ethtool information and statistics, and delegates packet protocol mechanics to `sunvnet_common.c`.

## Important APIs, Types, And Functions
- Module interface: `vnet_init()`, `vnet_exit()`, `vnet_port_driver`, VIO match table for `"vnet-port"`, and supported VIO versions 1.8, 1.7, 1.6, and 1.0.
- Netdev setup: `vnet_new()`, `vnet_find_or_create()`, `vnet_cleanup()`, `vnet_ops`, and `vnet_ethtool_ops`.
- TX routing: `__tx_port_find()`, `vnet_tx_port_find()`, `vnet_select_queue()`, and wrapper `vnet_start_xmit()`.
- RX/multicast/common wrappers: `vnet_set_rx_mode()` and optional `vnet_poll_controller()`.
- Machine-description lookup: `vnet_find_parent()` finds the containing `"network"` node and its `local-mac-address`.
- Port lifecycle: `vnet_port_probe()` and `vnet_port_remove()` allocate/free `struct vnet_port`, initialize VIO/LDC, add NAPI, link the port into parent lists/hash table, allocate a TX queue index, start VIO handshake, and tear everything down.
- Ettool statistics: `vnet_get_sset_count()`, `vnet_get_strings()`, and `vnet_get_ethtool_stats()` combine netdev stats with per-port stats.

## Control Flow
At module load the VIO driver is registered. Each `vnet-port` probe grabs the machine description, finds or creates a parent `struct vnet` based on the network node's local MAC, reads the port's remote MAC, allocates a `struct vnet_port`, initializes generic VIO state and an LDC channel, attaches NAPI to the parent netdev, marks switch-port capability from MD properties, inserts the port into the parent list and hash under `vp->lock`, assigns a least-used TX queue, stores driver data, creates the cleanup timer, enables NAPI, and calls `vio_port_up()` to begin handshake.

The parent vnet netdev is created once per local MAC with multiple TX queues, feature bits for TSO/GSO/checksum/scatter-gather, MTU range up to 65535, fixed MAC from MD, and source `vnet_ops`. TX queue selection hashes the destination MAC to a live direct port, falling back to the first live switch port. Remove disables VIO timers/NAPI, removes RCU list/hash entries, synchronizes readers, shuts down cleanup, returns the TX queue allocation, deletes NAPI, frees TX buffers and LDC resources, and frees the port. Module exit unregisters the VIO driver then frees parent netdevs after asserting their port lists are empty.

## State And Persistence
Global `vnet_list` tracks parent vnets by `local_mac` under `vnet_list_mutex`. Each `struct vnet` stores port list/hash state, queue usage, multicast list, netdev pointer, and local MAC. Each `struct vnet_port` stores remote MAC, switch/direct role, VIO state, per-port counters, NAPI, cleanup timer, negotiated offload values, and queue index. All state is volatile kernel memory; the authoritative topology comes from the machine description.

## Dependencies And Integration Points
The file depends on Linux netdev/ethtool/etherdevice/SKB APIs, mutex/RCU/list primitives, SPARC `asm/vio.h` and `asm/ldc.h`, machine-description APIs, and the common functions declared in `sunvnet_common.h`. It integrates with VIO control operations through `vnet_vio_ops`, with LDC events through `vnet_ldc_cfg`, and with ethtool through dynamic per-port string/stat generation.

## Risks And Edge Cases
- Ettool string count depends on `vp->nports`; concurrent port removal is protected by RCU during iteration, but userspace stats reads can still observe topology changes between count and fetch.
- `vnet_cleanup()` uses `BUG_ON(!list_empty(&vp->port_list))`, so module exit assumes VIO unregister has already removed every port.
- `__tx_port_find()` returns `NULL` when no live direct or switch port exists; common TX then drops.
- Queue selection and TX routing must stay aligned with `sunvnet_port_add_txq_common()` and per-port queue indexes.
- Machine-description properties are mandatory; missing local or remote MAC fails probe.

## Test Signals
Signals include module load/unload, vnet creation for shared local MACs, multiple port probes/removes, switch-port fallback routing, per-port queue distribution, ethtool stat names and counts with changing port counts, MTU boundary behavior, VIO handshake completion, and RCU-safe removal under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet_common.c

## Purpose
`sunvnet_common.c` is the shared protocol and data-path library for Sun virtual network ports. It negotiates VIO network attributes, manages exported/imported descriptor rings, handles LDC events through NAPI, receives packets from peer domains, maps and transmits SKBs through LDC cookies, handles ACK/STOPPED flow control, reshapes SKBs for hypervisor copy alignment, maintains multicast control messages, manages TX cleanup timers, and exports these common helpers to vnet/vsw-style drivers.

## Important APIs, Types, And Functions
- Exported handshake and control: `sunvnet_send_attr_common()`, `sunvnet_handle_attr_common()`, `sunvnet_handshake_complete_common()`, and `sunvnet_event_common()`.
- RX path: `vnet_rx_one()`, `get_rx_desc()`, `put_rx_desc()`, `vnet_walk_rx_one()`, `vnet_walk_rx()`, `vnet_rx()`, and `sunvnet_poll_common()`.
- TX ACK and trigger path: `vnet_ack()`, `vnet_nack()`, `vnet_send_ack()`, `__vnet_tx_trigger()`, `idx_is_pending()`, and `maybe_tx_wakeup()`.
- TX data path: `sunvnet_start_xmit_common()`, `vnet_skb_shape()`, `vnet_skb_map()`, `vnet_handle_offloads()`, `vnet_clean_tx_ring()`, `vnet_free_skbs()`, and `sunvnet_clean_timer_expire_common()`.
- Offload/checksum helpers: `vnet_fullcsum_ipv4()` and optional `vnet_fullcsum_ipv6()`.
- Netdev helpers: `sunvnet_open_common()`, `sunvnet_close_common()`, `sunvnet_tx_timeout_common()`, `sunvnet_set_rx_mode_common()`, and `sunvnet_set_mac_addr_common()`.
- Port resource helpers: `sunvnet_port_free_tx_bufs_common()`, `vnet_port_reset()`, `vnet_port_alloc_tx_ring()`, `sunvnet_port_is_up_common()`, `sunvnet_port_add_txq_common()`, and `sunvnet_port_rm_txq_common()`.
- Multicast helpers: `__vnet_mc_find()`, `__update_mc_list()`, `__send_mc_list()`, and `handle_mcast()`.

## Control Flow
During VIO handshake, `sunvnet_send_attr_common()` allocates the TX ring and sends supported transfer mode, MAC address, MTU, VIO_TX_DRING option, and LSO capabilities based on protocol version. `handle_attr_info()` validates peer attributes, negotiates MTU and TSO length, ACKs supported settings, or NACKs/reset on mismatch. Handshake completion initializes RX/TX ring sequence numbers.

LDC events are accumulated in `port->rx_event`, interrupts are disabled, and NAPI is scheduled. `vnet_event_napi()` handles RESET first by resetting VIO state, freeing TX rings, restarting handshake, and waking queues; handles UP by updating link state; otherwise it reads VIO messages, validates session IDs, dispatches data INFO to RX walking, data ACK to TX reclaim/wakeup, control multicast replies, or generic VIO control. RX walking imports peer descriptors with `ldc_get_dring_entry()`, copies packet data with `ldc_copy()`, marks descriptors done, and sends ACTIVE or STOPPED ACKs. If NAPI budget is exhausted, it records resume state and defers the STOPPED ACK.

TX chooses a port via a driver-supplied callback, handles GSO/TSO segmentation if needed, enforces remote MTU with ICMP packet-too-big feedback, shapes the SKB for the LDC alignment contract, computes full checksums when required, cleans old TX descriptors, maps the SKB into LDC cookies, fills a VIO net descriptor, optionally writes descriptor extension offload flags, publishes `VIO_DESC_READY` after `dma_wmb()`, sends exactly one start trigger while the peer is stopped, advances `dr->prod`, stops/wakes the netdev queue based on ring space, and starts the cleanup timer.

## State And Persistence
State is per `struct vnet_port` and per `struct vio_dring_state`: TX cookies/SKBs, negotiated remote MTU, TSO flag and max length, NAPI resume index, STOPPED ACK state, queue index, per-port stats, and cleanup timer. `struct vnet` holds the multicast subscription list and queue usage counters. There is no persistent storage; reset clears negotiated MTU/offload state and frees/reallocates TX rings.

## Dependencies And Integration Points
The file depends on Linux netdev, SKB, GSO, checksum, IPv4/IPv6 ICMP, timers, RCU/list state provided by the front-end driver, tracepoints from `trace/events/sunvnet.h`, and SPARC VIO/LDC primitives. It exports GPL symbols consumed by `sunvnet.c` and related virtual switch code. It integrates with VIO protocol versions 1.0 through 1.8, LDC descriptor ring APIs, hypervisor interrupt control via `vio_set_intr()`, and netdev multi-queue flow control.

## Risks And Edge Cases
- Attribute validation has a suspicious expression `!(xfer_mode | VIO_NEW_DRING_MODE)`, which uses bitwise OR where a capability test may have intended bitwise AND; this should be reviewed before protocol changes.
- `sunvnet_tx_timeout_common()` is a stub despite netdevs installing it.
- RX checksum code compares `skb->protocol == ETH_P_IP` in one branch while most checks use `htons(ETH_P_IP)`, making that path worth auditing.
- TX trigger/ACK state (`start_cons`, `stop_rx`, `dr->cons`, `dr->prod`) is subtle and races with queue locking; missed triggers are explicitly handled in `vnet_ack()`.
- LDC mapping and copying require 8-byte alignment and padded lengths; `vnet_skb_shape()` is critical for correctness.
- GSO handling recursively calls `sunvnet_start_xmit_common()` for each segment and must avoid queue/ring accounting regressions.
- Cleanup timer reclaims SKBs independent of ACK frequency; incorrect descriptor state transitions can leak mappings or free too early.

## Test Signals
High-value tests include VIO version negotiation across 1.0/1.3/1.6/1.7/1.8, MTU and TSO negotiation boundaries, LDC send `-EAGAIN` retry behavior, RX NAPI budget exhaustion/resume, STOPPED ACK flow control, TX ring full and queue wake paths, reset while TX descriptors are pending, SKB alignment and fragmented SKB mapping, GSO segmentation above `tsolen`, IPv4/IPv6 checksum correction, multicast add/delete propagation, and tracepoint-assisted packet flow verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet_common.h

## Purpose
`sunvnet_common.h` defines the shared constants, state structures, inline helpers, and exported function prototypes for Sun LDOM virtual network common code. It is the interface between front-end drivers such as `sunvnet.c` and the shared VIO/LDC packet implementation in `sunvnet_common.c`.

## Important APIs, Types, And Constants
- Packet/ring/offload constants: `VNET_CLEAN_TIMEOUT`, `VNET_MAXPACKET`, `VNET_TX_RING_SIZE`, `VNET_TX_WAKEUP_THRESH()`, `VNET_MINTSO`, `VNET_MAXTSO`, `VNET_MAX_MTU`, `VNET_PACKET_SKIP`, `VNET_MAXCOOKIES`, and `VNET_MAX_TXQS`.
- `struct vnet_tx_entry` stores one outstanding SKB, cookie count, and LDC cookies for a TX descriptor.
- `struct vnet_port_stats` defines fixed-width per-port counters and `NUM_VNET_PORT_STATS`.
- `struct vnet_port` embeds `struct vio_driver_state` and stores peer MAC, role flags, parent vnet/netdev pointers, TX buffer ring, list/hash nodes, flow-control booleans, cleanup timer, negotiated MTU/TSO, NAPI state, event mask, and queue index.
- `to_vnet_port()` maps a VIO state pointer back to `struct vnet_port`.
- `vnet_hashfn()` hashes MAC bytes into a 16-bucket port hash.
- `struct vnet_mcast_entry` tracks multicast addresses, whether they have been sent, and whether they remain present.
- `struct vnet` stores lock, netdev pointer, message level, TX queue usage, port list/hash, multicast list, parent-list node, local MAC, and port count.
- Public prototypes declare common netdev, VIO handshake, NAPI, TX, reset, poll-controller, and queue-allocation functions.

## Control Flow And State Behavior
The header fixes the common runtime model: a `vnet` owns many `vnet_port` instances, each port owns one VIO/LDC channel and a 512-entry TX descriptor ring, and the front-end selects a port per SKB before calling `sunvnet_start_xmit_common()`. `VNET_PACKET_SKIP` is part of the wire-buffer layout and is used by both TX shaping and RX pulling. Queue assignment is bounded by `VNET_MAX_TXQS`, while `q_used[]` spreads ports across netdev TX queues.

## Dependencies And Integration Points
The header includes `<linux/interrupt.h>` and relies on declarations from VIO/LDC, netdev, NAPI, timers, SKB, hlist/list, and Ethernet headers that are included by users. It integrates front-end drivers with common code through the exported function prototypes and the `VNET_PORT_TO_NET_DEVICE()` role distinction for vnet versus virtual-switch ports.

## Risks And Edge Cases
- Structure fields are shared by interrupt, NAPI, timer, and TX contexts; callers must respect the locking rules implemented in the C file.
- `VNET_MAXPACKET` allows jumbo MTUs up to 65535 plus Ethernet/VLAN headers, which drives cookie count and allocation sizes.
- Role flags `switch_port`, `tso`, and `vsw` alter routing, checksum behavior, and netdev selection.
- The multicast list is a manual singly linked list, so update/send code must handle allocation failure and removal carefully.
- `NUM_VNET_PORT_STATS` assumes every field in `struct vnet_port_stats` is `u32`.

## Test Signals
Compile users with vnet and virtual-switch configurations, validate queue index allocation up to and beyond 16 ports, check MAC hash collision behavior, verify per-port stat string counts match `NUM_VNET_PORT_STATS`, and stress reset/timer/NAPI/TX interactions over the fields exposed in `struct vnet_port`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/Kconfig

## Purpose
This Kconfig file declares the Sunplus Ethernet driver menu. It exposes a vendor gate `NET_VENDOR_SUNPLUS` and the `SP7021_EMAC` tristate option for Sunplus SP7021 dual 10/100 Ethernet hardware.

## Important APIs, Types, And Options
- `config NET_VENDOR_SUNPLUS` is a boolean menu gate named "Sunplus devices", defaults to `y`, and depends on `ARCH_SUNPLUS || COMPILE_TEST`.
- `if NET_VENDOR_SUNPLUS` scopes Sunplus device-specific options.
- `config SP7021_EMAC` is a tristate named "Sunplus Dual 10M/100M Ethernet devices", depends on `SOC_SP7021 || COMPILE_TEST`, selects `PHYLIB`, and documents that the driver creates two net-device interfaces and builds as module `sp7021_emac`.

## Control Flow And State Behavior
Kconfig controls build visibility and dependency resolution only. If `NET_VENDOR_SUNPLUS=n`, the SP7021 prompt is hidden and no Sunplus object is selected through this subtree. If `SP7021_EMAC=m` or `y`, the Makefile builds the composite `sp7021_emac` driver from its object list. No runtime state is stored here.

## Dependencies And Integration Points
The file integrates with the kernel networking vendor menu and the adjacent Makefile. `COMPILE_TEST` allows wider build coverage outside Sunplus architectures. `PHYLIB` selection ensures the selected driver has PHY framework support.

## Risks And Edge Cases
- `NET_VENDOR_SUNPLUS` defaults to `y`, so compile-test configurations may expose the submenu broadly.
- `SP7021_EMAC` selects `PHYLIB` but does not express MDIO/GPIO/clock/reset dependencies here; those may be handled in source or broader SoC configuration.
- The help text promises two net-device interfaces, which should stay consistent with the driver implementation.

## Test Signals
Run Kconfig build matrix checks for `ARCH_SUNPLUS`, non-Sunplus `COMPILE_TEST`, built-in, module, and disabled configurations. Confirm `sp7021_emac.ko` naming and PHYLIB dependency resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/Makefile

## Purpose
This Makefile wires the Sunplus SP7021 Ethernet driver into the kernel build. It maps `CONFIG_SP7021_EMAC` to the composite object `sp7021_emac.o` and lists the implementation objects that make up that module or built-in driver.

## Important APIs, Types, And Variables
- `obj-$(CONFIG_SP7021_EMAC) += sp7021_emac.o` includes the driver only when the Kconfig symbol is enabled.
- `sp7021_emac-objs := spl2sw_driver.o spl2sw_int.o spl2sw_desc.o spl2sw_mac.o spl2sw_mdio.o spl2sw_phy.o` declares the component objects for the composite target.

## Control Flow And State Behavior
The file has no runtime control flow. Build-time control is entirely driven by `CONFIG_SP7021_EMAC`. When enabled as `m`, the listed objects are linked into `sp7021_emac.ko`; when enabled as `y`, they are linked into the kernel image.

## Dependencies And Integration Points
It integrates with the Sunplus Kconfig file and the kernel kbuild composite-object convention. The object names indicate separate implementation areas for top-level driver logic, interrupts, descriptors, MAC programming, MDIO, and PHY handling.

## Risks And Edge Cases
- Any source rename or split must update `sp7021_emac-objs` or the build fails.
- The composite target name must remain aligned with the Kconfig help text's promised module name.
- Missing conditional objects may limit compile coverage if future features become optional.

## Test Signals
Build with `CONFIG_SP7021_EMAC=m` and `CONFIG_SP7021_EMAC=y`, verify the composite object links all six components, and run clean rebuilds after touching each component object dependency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/Makefile -->
