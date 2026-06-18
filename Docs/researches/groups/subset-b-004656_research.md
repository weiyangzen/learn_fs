# subset-b-004656

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/niu.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/niu.h

## Purpose
`niu.h` is the hardware contract and private state model for the Sun/Oracle Neptune NIU Ethernet driver. It defines the register map for PIO, MAC, IPP, FFLP, ZCP, DMA, TXC, PROM, MIF/MDIO, SerDes, PCS/XPCS, and interrupt units; packet descriptor formats; classifier and hash table formats; PHY constants; and the main software structs consumed by the NIU implementation.

## Important APIs, Types, And Functions
The file is mostly definitions. Important register families include logical device and interrupt controls (`LDSV*`, `LDG_IMGMT`, `LD_IM*`, `LDG_NUM`, `SID`), MAC/PCS/XPCS controls (`XMAC_CONFIG`, `BMAC_CONFIG`, PCS/XPCS status and advertisement registers), classifier resources (`ENET_VLAN_TBL`, `L2_CLS`, `L3_CLS`, `TCAM_*`, `FLOW_KEY`, FCRAM hash formats), receive DMA (`RXDMA_CFIG*`, `RBR_*`, `RCR*`, `RX_DMA_CTL_STAT*`), transmit DMA (`TX_RNG_CFIG`, `TX_RING_HDL`, `TX_RING_KICK`, `TX_CS`, `TX_ENT_MSK`), and error/ECC telemetry in IPP, ZCP, TXC, and RDMC blocks.

Key packet and ring types are `struct rx_pkt_hdr0`, `struct rx_pkt_hdr1`, `struct tx_pkt_hdr`, `struct tx_buff_info`, `struct txdma_mailbox`, `struct tx_ring_info`, `struct rxdma_mailbox`, and `struct rx_ring_info`. `niu_tx_avail()` computes transmit-ring availability from producer/consumer positions and the configured pending descriptor count. `NEXT_TX()`, `PREVIOUS_TX()`, `NEXT_RCR()`, and `NEXT_RBR()` wrap ring indexes.

The top-level runtime model is `struct niu`, which binds MMIO bases, `net_device`, PCI/platform device pointers, parent sharing state, DMA ops, MAC statistics, RX/TX rings, logical device groups, PHY ops, link configuration, classifier state, VPD, reset work, and per-port flags. Shared-chip state lives in `struct niu_parent`; classifier state uses `struct niu_classifier`, `struct niu_tcam_entry`, and `struct niu_rdc_tables`; PHY/link behavior is abstracted through `struct niu_phy_ops` and `struct niu_link_config`; DMA is abstracted through `struct niu_ops`.

## Control Flow
This header does not execute control flow by itself, but it encodes the driver control flow used by the implementation. Initialization code programs PIO/LDG mappings, parent classifier tables, MAC mode, PCS/XPCS or MII/MDIO PHY mode, RX/TX descriptor rings, logical pages, and interrupt masks using these offsets and masks. Runtime RX flow is RBR buffer publication, RCR completion consumption, packet-header parsing through `rx_pkt_hdr0/1`, and error classification through `RCR_ENTRY_*` and `RX_DMA_CTL_STAT_*`. Runtime TX flow is `tx_pkt_hdr` setup, one or more `TX_DESC_*` descriptors, producer kick via `TX_RING_KICK`, and completion/error observation through mailbox and `TX_CS` fields. Link flow branches between 1G/10G, copper/fiber, MII/PCS/XPCS, and vendor PHY constants such as BCM8704/8706, BCM5464R, and MRVL88X2011.

## State, Persistence, And Dependencies
Persistent driver state is in memory owned by `struct niu` and `struct niu_parent`, not on disk. Hardware-visible state is held in MMIO registers, descriptor rings, DMA mailboxes, FCRAM hash entries, TCAM entries, VLAN/RDC tables, VPD EEPROM fields, and logical page mappings. The state is volatile across reset except VPD/EEPROM content and board/PHY identity. The file depends on kernel networking types (`net_device`, `sk_buff`, NAPI), DMA mapping semantics, PCI/platform devices, `device_node`, timers/workqueues, endian-specific bitfields, and Ethernet constants.

## Integration Points
`niu.h` integrates the NIU driver with the Linux netdev stack through `struct net_device`, NAPI in `struct niu_ldg`, per-ring packet counters, and `sk_buff` ownership. It integrates with the kernel DMA API through the `niu_ops` abstraction, allowing physical or virtualized DMA backends. It integrates with PCI/Open Firmware platform discovery through `struct niu_parent`, VPD strings, platform type constants, and port/PHY mappings. The classifier definitions align VLAN, alternate MAC, TCAM, flow hash, and RDC steering hardware with receive queue selection. Interrupt definitions map logical devices to logical device groups and hardware vectors.

## Risks
The biggest risk is bitfield/register drift: incorrect masks, shifts, endian layout, or address offsets can corrupt hardware state. Ring availability assumes power-of-two maximum sizing and consistent `pending`, `prod`, and `cons` handling; misuse can underflow or overrun descriptor rings. RX/TX DMA descriptors embed physical address limits and alignment requirements, so wrong shifts or block sizes can cause DMA to wrong memory. Shared `niu_parent` classifier and TCAM state must be coordinated across ports. Error masks distinguish fatal, port fatal, and write-clear conditions; treating a fatal bit as recoverable can leave DMA wedged, while over-resetting can flap links. Vendor PHY constants are board-specific and fragile around hotplug and 1G/10G copper/fiber detection.

## Test Signals
Useful signals include successful probe across PCI and platform NIU variants, correct MAC mode selection, expected VPD model/board parsing, stable link negotiation for MII/PCS/XPCS PHYs, RX/TX packet counters advancing under traffic, no descriptor leaks under ring wrap, correct multicast/VLAN/RDC steering, correct MSI-X/LDG interrupt routing, and recovery from injected or observed DMA/MAC/IPP/ZCP/TXC error bits. Static checks should focus on mask/shift consistency, endian bitfield layout, descriptor alignment, and ring availability arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/niu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunbmac.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunbmac.c

## Purpose
`sunbmac.c` is the Linux SBUS/platform driver for Sun BigMAC 100baseT Ethernet adapters attached through QEC. It maps QEC global/channel registers, BigMAC core registers, and transceiver registers; allocates DVMA descriptor rings; registers a netdev; services transmit, receive, interrupt, multicast, ethtool-link, and timeout paths; and drives a simple PHY speed fallback timer.

## Important APIs, Types, And Functions
Probe/removal entry points are `bigmac_sbus_probe()`, `bigmac_ether_init()`, and `bigmac_sbus_remove()`, registered by `module_platform_driver()`. Netdev operations are `bigmac_open()`, `bigmac_close()`, `bigmac_start_xmit()`, `bigmac_get_stats()`, `bigmac_set_multicast()`, `bigmac_tx_timeout()`, `eth_mac_addr`, and `eth_validate_addr`. Ethtool exposes `bigmac_get_drvinfo()` and `bigmac_get_link()`.

Hardware setup is split across `qec_global_reset()`, `qec_init()`, `bigmac_tx_reset()`, `bigmac_rx_reset()`, `bigmac_stop()`, `bigmac_init_rings()`, `bigmac_tcvr_init()`, and `bigmac_init_hw()`. PHY management uses bit-banged MDIO helpers `idle_transceiver()`, `write_tcvr_bit()`, `read_tcvr_bit()`, `read_tcvr_bit2()`, `put_tcvr_byte()`, `bigmac_tcvr_read()`, `bigmac_tcvr_write()`, `bigmac_begin_auto_negotiation()`, `try_next_permutation()`, and `bigmac_timer()`. Runtime data paths are `bigmac_interrupt()`, `bigmac_tx()`, `bigmac_rx()`, and `bigmac_is_medium_rare()`.

## Control Flow
Probe allocates an Ethernet device, maps QEC/global/channel/MAC/transceiver registers, verifies QEC BigMAC mode, resets QEC, chooses SBUS burst size, initializes QEC memory partitioning, stops the MAC, allocates one coherent descriptor block, sets timer/netdev operations, registers the netdev, and stores driver data. Open requests the shared IRQ, initializes the timer, and calls `bigmac_init_hw()`. Hardware initialization latches counters, resets QEC, initializes rings, detects internal/external transceiver, stops RX/TX, writes the station address and multicast hash baseline, programs TX/RX config, points QEC at descriptor rings, configures FIFO pointers and interrupt masks, enables TX/RX, and starts link fallback.

Transmit maps the skb, fills one TX descriptor with update, address, ownership, SOP/EOP, and length bits under `bp->lock`, advances `tx_new`, stops the queue if full, and kicks QEC. TX completion walks from `tx_old` until it sees an owned descriptor, unmaps DMA, accounts bytes/packets, frees skbs, advances `tx_old`, and wakes the queue if space returned. Receive walks descriptors until owned by hardware, validates length, either swaps in a new DMA skb for large packets or copies small packets into a fresh skb, returns the ring descriptor to hardware, calls `eth_type_trans()` and `netif_rx()`, and updates stats. Interrupt handling reads QEC and channel status, resets on error bits, then dispatches TX and RX completions.

The link timer first forces 100baseT, polls BMSR/BMCR every 1.2 seconds, reports link up, or after several ticks resets the PHY and falls back to 10baseT. If both modes fail, it reinitializes the adapter and reports a cable/link problem.

## State, Persistence, And Dependencies
Driver state lives in `struct bigmac`: mapped register pointers, descriptor block and DVMA address, spinlock, RX/TX skb arrays, ring indexes, board revision, transceiver type, burst mode, software copies of BMSR/BMCR, timer state/ticks, platform device backpointers, and netdev pointer. Persistent state is limited to netdev configuration and MAC address; hardware and ring state are rebuilt on open, reset, timeout, and error interrupts. Dependencies include SBUS read/write accessors, Open Firmware resource mapping, platform devices, DMA coherent/single mapping APIs, Linux MII constants, timers, IRQs, CRC multicast hashing, and the shared QEC hardware described in `sunbmac.h`.

## Integration Points
The driver integrates with Linux netdev through `alloc_etherdev()`, netdev ops, `register_netdev()`, IRQ sharing, watchdog timeouts, stats, multicast callbacks, and ethtool. It uses the SPARC/Open Firmware environment for resources, IRQs, `idprom` MAC address, and QEC parent discovery. Its descriptor and register definitions come from `sunbmac.h`. RX hands packets up through `netif_rx()` rather than NAPI, which reflects the driver age. The hardware path is tightly coupled to QEC local memory partitioning: QEC owns the descriptor-ring DMA addresses and FIFO offsets while BigMAC owns MAC filtering and PHY-facing behavior.

## Risks
The driver does not check DMA mapping failures for per-packet maps, so DMA API failures could lead to invalid descriptors. `bigmac_init_rings()` can leave RX descriptors empty when skb allocation fails, reducing receive capacity without failing initialization. `bigmac_set_multicast()` disables RX and busy-waits without a timeout, so hardware that never clears enable can hang the caller. Error recovery calls full hardware initialization from interrupt context with `non_blocking=true`; this path must avoid blocking allocations but still touches many registers. The link logic is a forced 100/10 fallback rather than full autonegotiation. RX has no checksum offload and uses legacy `netif_rx()`. Correctness depends on SBUS/QEC register ordering and descriptor ownership bits being visible in the expected order.

## Test Signals
Signals include successful platform probe for OF node name `be`, clean register mapping/unmapping on failure and removal, QEC reset completion, IRQ request/free symmetry, stable open/close cycles, TX queue stopping and waking under ring pressure, RX delivery for small and large frames, multicast hash programming for normal/allmulti/promisc cases, watchdog reset recovery, link timer reporting 100baseT or 10baseT, and stats increments for MAC counters and RX/TX traffic. Fault-injection signals include allocation failure during RX refill, QEC/BigMAC error bits triggering reset, and timeout paths not leaking skbs or DMA mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunbmac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunbmac.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunbmac.h

## Purpose
`sunbmac.h` defines the hardware register offsets, bit masks, descriptor layouts, ring sizing, helper macros, enums, and private state for the Sun BigMAC 100baseT driver. It is the static ABI layer used by `sunbmac.c` to program QEC global/channel resources, BigMAC MAC registers, the transceiver PAL/MDIO interface, and RX/TX descriptor rings.

## Important APIs, Types, And Functions
Register groups include QEC global registers (`GLOB_*`), QEC BigMAC channel registers (`CREG_*`), BigMAC core registers (`BMAC_*`), XIF/TX/RX config and status masks (`BIGMAC_*`), and transceiver PAL/MGMT registers (`TCVR_*`, `MGMT_PAL_*`). Descriptor types are `struct be_rxd` and `struct be_txd` with `RXD_*` and `TXD_*` ownership, update, SOP/EOP, and length bits. Ring constants fix both RX and TX rings at 256 entries, with `NEXT_RX()`, `NEXT_TX()`, `PREV_RX()`, `PREV_TX()`, and `TX_BUFFS_AVAIL()` providing wrap and flow-control arithmetic.

`struct bmac_init_block` stores the coherent RX and TX descriptor arrays. `bib_offset()` computes descriptor offsets inside that block for QEC descriptor base registers. `enum bigmac_transceiver` selects external, internal, or unknown transceiver mode; `enum bigmac_timer_state` defines the link timer state machine. `struct bigmac` is the driver's private state. The inline `big_mac_alloc_skb()` allocates 64-byte-aligned receive skbs using `ALIGNED_RX_SKB_ADDR()`.

## Control Flow
The header shapes `sunbmac.c` control flow: probe maps register ranges sized by `*_REG_SIZE`, initialization writes QEC burst/memory controls, TX/RX reset loops poll `BIGMAC_*CFG` bits, descriptor setup fills `be_rxd`/`be_txd` entries, open starts the timer in `ltrywait`, RX/TX paths advance ring indexes with the macros, and multicast setup writes BMAC hash-table registers. Transceiver MDIO operations use the PAL bit definitions to drive internal or external MDIO pins.

## State, Persistence, And Dependencies
`struct bigmac` stores volatile per-device state: MMIO pointers, coherent descriptor block and DVMA address, lock, skb arrays, ring indexes, board revision, transceiver selection, burst capabilities, PHY software registers, timer, platform device links, and the netdev pointer. There is no filesystem persistence. Hardware state persists only while the device is powered and is reprogrammed on initialization or reset. The header depends on Linux kernel types (`u32`, `dma_addr_t`, `spinlock_t`, `sk_buff`, `timer_list`, `platform_device`, `net_device`) and Ethernet constants.

## Integration Points
This header is included directly by `sunbmac.c` and forms the interface between the Linux netdev driver and the QEC/BigMAC hardware. Descriptor structs are shared with DMA hardware. The `TX_BUFFS_AVAIL()` macro controls when the netdev TX queue is stopped or woken. `big_mac_alloc_skb()` provides the alignment assumptions used by RX DMA setup. The register masks align driver error handling with QEC and BigMAC interrupt status bits.

## Risks
The descriptor length masks are 11 bits, so callers must keep RX/TX buffer sizes within the hardware's encoded limits. Ring macros assume 256-entry power-of-two rings. `TX_BUFFS_AVAIL()` relies on `tx_old` and `tx_new` being updated under the same synchronization expected by the driver. `big_mac_alloc_skb()` assumes the extra 64 bytes are sufficient for DMA alignment and that callers reserve subsequent protocol offsets correctly. Incorrect QEC memory sizes or FIFO pointer programming can cause RX/TX overlap in local memory. Status registers such as `BMAC_STATUS` are clear-on-read, so consumers must avoid accidental reads.

## Test Signals
Good signals are successful compilation against current kernel type definitions, correct descriptor block offsets, RX skb data alignment, ring wrap behavior under 256-entry pressure, queue stop/wake thresholds, and multicast hash register programming. Hardware tests should watch QEC `CREG_STAT_ERRORS`, BigMAC status bits, and collision/error counters while sending traffic, changing multicast modes, opening/closing the interface, and triggering link fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunbmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sungem.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sungem.c

## Purpose
`sungem.c` is the PCI driver for Sun GEM/RIO GEM and Apple GMAC Ethernet controllers. It supports 10/100/1000 operation depending on hardware/PHY, NAPI receive polling, scatter/gather TX, hardware checksum offload, multicast filtering, PHY/PCS link management, reset recovery, suspend/resume, Wake-on-LAN on Apple parts, ethtool configuration, and fallback MAC address discovery.

## Important APIs, Types, And Functions
PCI integration uses `gem_pci_tbl`, `gem_init_one()`, `gem_remove_one()`, `gem_driver`, and `module_pci_driver()`. Netdev ops are `gem_open()`, `gem_close()`, `gem_start_xmit()`, `gem_get_stats()`, `gem_set_multicast()`, `gem_ioctl()`, `gem_tx_timeout()`, `gem_change_mtu()`, `gem_set_mac_address()`, and `eth_validate_addr`. Ettool support includes driver info, link settings get/set, autoneg restart, message level, and WoL through `gem_ethtool_ops`.

MDIO access is handled by `__sungem_phy_read()`, `__sungem_phy_write()`, and wrappers connected to `sungem_phy`. Interrupt and NAPI paths include `gem_interrupt()`, `gem_poll()`, `gem_tx()`, `gem_rx()`, `gem_abnormal_irq()`, and specialized handlers for PCS, TX MAC, RX MAC, MAC pause, MIF, and PCI errors. Initialization and recovery use `gem_reset()`, `gem_reinit_chip()`, `gem_init_rings()`, `gem_init_dma()`, `gem_init_mac()`, `gem_init_pause_thresholds()`, `gem_init_phy()`, `gem_check_invariants()`, `gem_set_link_modes()`, `gem_link_timer()`, `gem_schedule_reset()`, and `gem_reset_task()`. Power management is `gem_suspend()`, `gem_resume()`, `gem_do_start()`, `gem_do_stop()`, `gem_get_cell()`, `gem_put_cell()`, and `gem_stop_phy()`.

## Control Flow
Probe enables the PCI device, chooses a 64-bit DMA mask only for Sun GEM when possible and otherwise uses 32-bit DMA, allocates a netdev, requests PCI regions, maps MMIO, records the OF node when available, enables Apple WoL capability, powers the cell, resets hardware, wires `sungem_phy` MDIO callbacks, detects FIFO/PHY invariants, allocates a coherent init block, obtains a MAC address from OF/idprom/PCI ROM/random fallback, configures netdev/NAPI/ethtool features, registers the netdev, and powers the cell back down until open.

Open powers the cell, enables PCI, and calls `gem_do_start()`. Start reinitializes chip state, requests the IRQ, attaches the netdev, enables NAPI/queue, initializes PHY/PCS, and starts link negotiation. Link establishment is timer-driven: `gem_link_timer()` polls MII or PCS/SerDes, handles autoneg fallback to forced 100 then 10 half-duplex when needed, and calls `gem_set_link_modes()` when link is up. `gem_set_link_modes()` programs duplex, speed, carrier extension, XIF, pause, slot time, and then starts DMA/MAC units.

Interrupts schedule NAPI after saving `GREG_STAT` and masking interrupts. `gem_poll()` handles abnormal status first, runs TX completions, then RX work until budget or status exhaustion; it reenables interrupts after completing NAPI. TX maps the skb head and fragments into descriptors, supports `CHECKSUM_PARTIAL`, writes the first descriptor last for multi-fragment packets, stops the queue when free descriptors are low, and kicks TX DMA. TX completion walks to the hardware-reported completion index, waits for all fragments of an skb to complete, unmaps DMA, updates stats, frees skbs, and wakes the queue with memory barriers. RX consumes descriptors not owned by hardware, avoids a descriptor writeback race by checking `RXDMA_DONE`, validates length/error bits, swaps large buffers or copies small packets, applies RX checksum when enabled, passes packets through GRO, reposts descriptors in groups of four, and updates counters.

Close and suspend stop NAPI/queue, mask interrupts, delete the link timer, clear pending reset state, stop DMA, reset when appropriate, clean rings, free IRQ, and stop or prepare the PHY for WoL. Reset work runs under RTNL, skips closed/suspended devices, stops the link timer/NAPI, reinitializes chip/rings, restarts link or DMA according to link state, and clears `reset_task_pending`.

## State, Persistence, And Dependencies
The private `struct gem` is defined in `sungem.h` and carries PCI/netdev pointers, MMIO base, coherent init block, RX/TX rings, NAPI, timers, reset work, PHY state, link state, FIFO sizes, pause thresholds, feature flags, message level, WoL state, and cell power reference count. Runtime state is volatile and rebuilt on open, reset, MTU change, and resume. Persistent configuration comes from PCI IDs, Open Firmware properties, idprom, PCI ROM VPD, user-set ethtool link/WoL settings, and netdev MAC/MTU/multicast flags. Dependencies include PCI, DMA mapping, NAPI/GRO, MII/ethtool, `sungem_phy`, Open Firmware on SPARC/PPC, PMAC feature calls on Apple hardware, timers/workqueues, and register definitions in `sungem.h`.

## Integration Points
The driver integrates with Linux networking through netdev ops, NAPI, GRO, checksum offload (`NETIF_F_HW_CSUM`, `NETIF_F_RXCSUM`), scatter/gather, MTU bounds, watchdog timeouts, multicast mode changes, MII ioctls, ethtool link settings, and WoL. It integrates with the PCI core for device IDs, regions, DMA masks, PM callbacks, config-space error reporting, and driver data. On Apple PowerMac systems it integrates with platform feature calls for GMAC cell and PHY reset/power control. On SPARC/PPC it uses OF properties for MAC address and PHY mode. It delegates PHY-specific details to the generic `sungem_phy` helper definitions.

## Risks
Several DMA mapping calls do not explicitly check mapping errors before publishing descriptors. Reset and power-management paths are complex and rely on RTNL, NAPI disable, IRQ masking, timer deletion, and `reset_task_pending` ordering to avoid races. TX completion must handle fragmented skbs atomically; a wrong completion limit can free a partially transmitted skb. RX descriptor reuse depends on the `RXDMA_DONE` readback guard to avoid racing hardware writeback. `gem_set_multicast()` waits for RX disable with a finite loop but continues if timeout expires. Jumbo MTU support is disabled because jumbo frames are noted as broken. MAC address fallback outside SPARC/PPC may generate a random Sun-prefixed address if VPD is missing. WoL and cell reference counting are Apple-specific and can become unbalanced if suspend/resume/open/close paths diverge.

## Test Signals
Strong signals include successful probe across Sun GEM, Sun RIO GEM, and Apple GMAC PCI IDs; correct 32-bit/64-bit DMA mask selection; open/close and suspend/resume cycles without cell reference leaks; stable NAPI interrupt masking/unmasking; TX with linear and fragmented skbs including checksum offload; RX GRO delivery with checksum-complete status; queue stop/wake under ring pressure; reset-task recovery after TX timeout, PCI error, RX tag error, and RX FIFO overflow; ethtool autoneg/forced-speed changes; multicast/allmulti/promisc programming; WoL magic-packet suspend behavior on Apple parts; and clean removal with reset work canceled and coherent memory unmapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sungem.c -->
