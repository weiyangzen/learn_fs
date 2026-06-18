# subset-b-004522 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/skge.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/skge.h

## Purpose
`skge.h` is the hardware contract header for the Marvell Yukon/SysKonnect `skge` Ethernet driver. It defines PCI configuration bits, MMIO register offsets, descriptor formats, queue/ring structures, per-device/per-port driver state, PHY/MAC bitfields, Wake-on-LAN controls, statistics counter offsets, and small MMIO helper functions used by the companion driver implementation. The file is intentionally dense: most of it maps named constants onto the Genesis/Yukon register layout so executable code can avoid magic offsets when programming BMU queues, RAM buffers, XMAC/GMAC blocks, PHYs, LEDs, timers, interrupts, and WOL units.

## Important APIs, Types, and Functions
The main hardware register namespaces are `enum csr_regs` for control/status blocks, queue/RAM/FIFO offsets such as `Q_ADDR()` and `RB_ADDR()`, XMAC/GMAC base mappings via `SK_XMAC_REG()` and `SK_GMAC_REG()`, and register groups for PHY, MAC, WOL, MIB, interrupt, BMU, RAM buffer, and FIFO control. Device identity constants include `CHIP_ID_GENESIS`, `CHIP_ID_YUKON`, `CHIP_ID_YUKON_LITE`, `CHIP_ID_YUKON_LP`, `CHIP_ID_YUKON_XL`, `CHIP_ID_YUKON_EC`, and `CHIP_ID_YUKON_FE`, plus revision IDs and PHY type IDs.

The core data structures are `struct skge_rx_desc`, `struct skge_tx_desc`, `struct skge_element`, `struct skge_ring`, `struct skge_hw`, and `struct skge_port`. `struct skge_hw` represents shared adapter state: mapped registers, PCI device, hardware lock, interrupt mask, up to two `net_device` instances, chip/PHY metadata, RAM sizing, PHY lock, PHY tasklet, and IRQ name storage. `struct skge_port` represents per-port netdev state: NAPI, TX/RX rings, RX buffer sizing, link timer, flow-control state, WOL/autoneg/speed/duplex settings, DMA ring memory, and optional debugfs entry.

The executable helpers are all inline MMIO accessors: `skge_read32()`, `skge_read16()`, `skge_read8()`, `skge_write32()`, `skge_write16()`, `skge_write8()`, `xm_read32()`, `xm_read16()`, `xm_write32()`, `xm_write16()`, `xm_outhash()`, `xm_outaddr()`, `gma_read16()`, `gma_read32()`, `gma_write16()`, and `gma_set_addr()`. These wrap Linux `readb/readw/readl` and `writeb/writew/writel`, including the XMAC quirk that 32-bit XMAC registers are accessed as two 16-bit operations.

## Control Flow
The header has no driver lifecycle control flow of its own. Its "flow" is declarative: constants encode what later driver code writes or reads during reset, ring setup, packet transmission, packet reception, interrupt handling, link negotiation, multicast filtering, WOL programming, and statistics collection. The inline accessors are the only procedural paths. They compute the right MMIO address for global registers, XMAC registers, or GMAC registers, then perform a typed MMIO load or store.

The descriptor and ring definitions imply the runtime queue flow used by the driver. RX/TX descriptors carry control bits such as `BMU_OWN`, `BMU_STF`, `BMU_EOF`, IRQ request bits, checksum opcodes, DMA addresses, status, timestamps, and checksum fields. `struct skge_element` binds a descriptor to an skb and DMA unmap metadata, while `struct skge_ring` tracks producer/consumer style linked elements through `to_clean`, `to_use`, and `start`.

## State and Persistence Behavior
No persistent state is stored in this header, but it describes all major mutable state surfaces of the hardware and driver. Hardware state includes PCI config registers, global control/status, interrupt masks/status, timers, descriptor poll state, RAM buffer pointers and thresholds, BMU queue state machines, MAC FIFOs, PHY control/status registers, GMAC/XMAC configuration, statistics counters, multicast hashes, source addresses, WOL pattern RAM, and WOL result bits. Driver runtime state is represented by `struct skge_hw` and `struct skge_port`; it is allocated and managed by the implementation file, not by the header.

The register definitions include state that survives longer than a single packet, such as WOL enable/result bits, PHY autonegotiation and advertisement settings, LED configuration, MAC source addresses, MIB counters, and EEPROM/VPD sizing. Any code using these constants must explicitly reset or restore those registers across probe, suspend, resume, close, and error recovery.

## Dependencies and Integration Points
The header depends on Linux networking and DMA abstractions through `struct net_device`, `struct napi_struct`, `struct sk_buff`, DMA unmap metadata helpers, timers, tasklets, spinlocks, PCI device state, and optional debugfs state. It includes `<linux/interrupt.h>` and assumes common kernel headers included by the corresponding C files provide the rest of the network and DMA types.

Integration points are the `skge` driver implementation, the Linux netdev stack, PCI/MMIO access, PHY/MII management, NAPI polling, DMA mapping/unmapping, ethtool/WOL/statistics paths, and debugfs when enabled. The register map also overlaps conceptually with `sky2.h` because both drivers target Marvell Yukon-family devices, but this header is specific to the older/new `skge` driver path and includes Genesis/XMAC definitions not used by the Yukon-2-only `sky2.c`.

## Risks and Edge Cases
The primary risk is register contract drift. Incorrect offsets, masks, endian assumptions, or port-offset calculations can make the executable driver corrupt unrelated hardware state. XMAC 32-bit helpers split accesses into two 16-bit operations, which must match hardware ordering expectations. Address helper macros such as `SK_REG()`, `SK_XMAC_REG()`, `SK_GMAC_REG()`, `Q_ADDR()`, `RB_ADDR()`, `WOL_REGS()`, and `WOL_PATT_RAM_BASE()` are central to safe register access.

Several constants encode chip-specific errata or mode differences: Genesis versus Yukon, XMAC versus GMAC, Broadcom versus Marvell PHY, copper versus fiber, and Fast Ethernet versus Gigabit PHY behavior. Flow-control resolution, autonegotiation advertisement, LED control, and WOL bits differ across PHY families. Descriptor ownership and DMA unmap metadata also create memory-ordering and lifetime risks for the implementation that consumes these structures.

## Test Signals
Useful signals are build coverage for all `skge` users, probe on supported Genesis/Yukon PCI IDs, ifup/ifdown cycling, TX/RX under checksum and VLAN modes, jumbo and normal MTU coverage, multicast/promiscuous filter changes, ethtool statistics reads, WOL suspend/resume, PHY autonegotiation across copper/fiber variants, interrupt masking/error interrupt handling, and DMA stress on 32-bit and 64-bit DMA-capable platforms. Static checks should catch missing includes, type-size mismatches, and accidental changes to descriptor layout or register constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/skge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/sky2.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/sky2.c

## Purpose
`sky2.c` implements the PCI Ethernet driver for Marvell Yukon-2 controllers. It owns PCI probe/remove, device reset, power management, netdev registration, NAPI interrupt processing, RX/TX DMA ring management, PHY and GMAC setup, Wake-on-LAN, ethtool operations, multicast filtering, statistics, MSI probing, debugfs diagnostics, suspend/resume, and shutdown. The driver intentionally handles only Yukon-2 hardware and relies on higher layers for link failover and policy-level link management.

## Important APIs, Types, and Functions
External integration is through `struct pci_driver sky2_driver`, `struct net_device_ops sky2_netdev_ops[]`, and `struct ethtool_ops sky2_ethtool_ops`. Probe and module lifecycle functions are `sky2_init_module()`, `sky2_cleanup_module()`, `sky2_probe()`, `sky2_remove()`, `sky2_suspend()`, `sky2_resume()`, and `sky2_shutdown()`. Netdev operations include `sky2_open()`, `sky2_close()`, `sky2_xmit_frame()`, `sky2_ioctl()`, `sky2_set_mac_address()`, `sky2_set_multicast()`, `sky2_change_mtu()`, `sky2_fix_features()`, `sky2_set_features()`, `sky2_tx_timeout()`, and `sky2_get_stats()`.

Core hardware setup functions are `sky2_init()`, `sky2_reset()`, `sky2_power_on()`, `sky2_power_aux()`, `sky2_mac_init()`, `sky2_phy_init()`, `sky2_phy_power_up()`, `sky2_phy_power_down()`, `sky2_hw_up()`, and `sky2_hw_down()`. Ring and DMA helpers include `sky2_alloc_buffers()`, `sky2_free_buffers()`, `tx_init()`, `sky2_qset()`, `sky2_prefetch_init()`, `sky2_rx_start()`, `sky2_rx_stop()`, `sky2_rx_clean()`, `sky2_rx_alloc()`, `sky2_rx_map_skb()`, `sky2_rx_unmap_skb()`, `sky2_rx_submit()`, `sky2_tx_unmap()`, `sky2_tx_complete()`, and `sky2_tx_reset()`.

Interrupt and receive paths are centered on `sky2_intr()`, `sky2_poll()`, `sky2_status_intr()`, `sky2_receive()`, `sky2_rx_checksum()`, `sky2_rx_tag()`, `sky2_rx_hash()`, `sky2_rx_done()`, `sky2_tx_done()`, `sky2_err_intr()`, `sky2_hw_intr()`, `sky2_hw_error()`, `sky2_mac_intr()`, `sky2_le_error()`, `sky2_phy_intr()`, and `sky2_qlink_intr()`. Link and PHY control is handled by `gm_phy_write()`, `__gm_phy_read()`, `gm_phy_read()`, `sky2_autoneg_done()`, `sky2_link_up()`, `sky2_link_down()`, `sky2_phy_reinit()`, and `sky2_flow()`.

## Control Flow
Module load initializes optional debugfs support and registers the PCI driver. `sky2_probe()` enables the PCI device, validates config access, requests BARs, configures DMA masks, maps MMIO, initializes hardware identity/flags with `sky2_init()`, allocates a coherent status ring, resets the chip, creates one or two netdevs, optionally enables and tests MSI with a forced software IRQ, registers netdevs, sets up shared IRQ for dual-port devices, and installs watchdog/restart work. Error labels unwind in reverse order.

Opening a netdev calls `sky2_alloc_buffers()` to allocate coherent TX/RX list-element rings and software ring metadata, sets up IRQ/NAPI for single-port devices, then `sky2_hw_up()` initializes TX state, handles PCI-X split transaction constraints, initializes MAC/PHY, partitions RAM buffer space, initializes BMU/prefetch units, programs VLAN/features, and starts RX. `sky2_open()` then enables port interrupts. Closing disables interrupts or synchronizes shared IRQ/NAPI, calls `sky2_hw_down()` to stop TX/RX, power down PHY, reset queues, and complete stuck TX entries, then frees buffers.

Transmit flow starts in `sky2_xmit_frame()`. It checks available list elements, DMA maps skb head and fragments, emits address-high, TSO, VLAN, checksum, packet, and buffer list elements as needed, records DMA unmap metadata in the software TX ring, marks end-of-packet, updates the producer index with a write memory barrier through `sky2_put_idx()`, and stops the queue if space is low. Completion is reported through status list elements: `sky2_status_intr()` decodes `OP_TXINDEXLE`, `sky2_tx_done()` calls `sky2_tx_complete()`, DMA mappings are released, skb memory is freed, byte/packet counters are updated, and the netdev queue is woken when enough room returns.

Receive flow allocates skbs, optional page frags for large MTUs, maps them for DMA, and submits one or more RX list elements per ring entry. Hardware writes status list elements. `sky2_status_intr()` decodes receive status, VLAN, checksum, and RSS-hash opcodes. `sky2_receive()` validates frame status and length, either copies small or unaligned packets with `receive_copy()` or swaps in a newly allocated skb with `receive_new()`, resubmits the consumed ring entry, and passes packets to GRO or normal receive via `sky2_skb_rx()`. `sky2_rx_done()` updates stats, records `last_rx`, and advances the hardware RX put index.

Interrupts are NAPI driven. The hard IRQ handler reads `B0_Y2_SP_ISRC2`, handles empty or removed hardware cases, prefetches the status ring, and schedules NAPI. `sky2_poll()` handles error, PHY, quick-link, and status-ring work until budget exhaustion, then completes NAPI and unmasks/acknowledges through status register reads. The watchdog detects lost IRQs and RX hangs, scheduling `restart_work` when needed. Restart is serialized under RTNL by `sky2_restart()`, which brings all ports down, resets hardware, and brings them back up.

## State and Persistence Behavior
Runtime adapter state lives in `struct sky2_hw` from `sky2.h`: PCI device, mapped MMIO, status ring, NAPI, watchdog timer, restart work, chip ID/revision/flags, port count, per-port netdev pointers, and MSI/IRQ state. Per-port state in `struct sky2_port` tracks TX/RX rings, producer/consumer indices, DMA addresses, pending sizes, feature flags, PHY lock, link settings, flow control mode/status, WOL flags, software stats, RX hang check state, and debugfs entry.

Hardware state includes PCI config registers, power/clock gating, chip reset state, PHY pages/registers, GMAC registers, RX/TX GMF FIFOs, BMU queues, prefetch units, RAM buffer partitions, status list address and timers, interrupt masks, WOL registers, MAC addresses, multicast hashes, MIB counters, and device-specific workaround registers. Suspend paths stop timers/work, bring running ports down, program WOL where enabled, and switch power toward auxiliary mode. Resume rewrites PCI clock config, resets hardware, and reopens running ports from driver state.

The driver persists user-facing settings in memory across close/reopen and reset while the module remains loaded: MTU, ring sizes, ethtool coalescing registers, flow-control settings, advertised link modes, WOL options, MAC address, netdev feature flags, and multicast filters. It does not implement durable persistence across unload; EEPROM/VPD access is exposed through ethtool get/set helpers guarded by a magic value.

## Dependencies and Integration Points
`sky2.c` depends on `sky2.h` for register definitions, list-element formats, chip flags, and state structures. Kernel integration points include PCI core, DMA mapping, netdev registration, NAPI, skb/GRO, ethtool, MII ioctl, VLAN acceleration, RSS hash keys, DMI-based MSI blacklist, debugfs, notifier blocks, workqueues, timers, device power management, OF MAC address lookup, and optional netpoll.

The PCI ID table binds many SysKonnect, D-Link, and Marvell Yukon-2 device IDs. Link control integrates with Marvell PHY registers through GMAC SMI operations. Feature integration includes RX/TX checksum offload, scatter-gather, TSO, high DMA, VLAN tag insertion/stripping, RX hash, jumbo MTU where supported, Wake-on-LAN for copper PHYs, ethtool register dumps, EEPROM/VPD access, coalescing, ring sizing, LED identification, pause parameters, and per-port statistics.

## Risks and Edge Cases
The driver is highly hardware-errata-driven. Many paths branch on chip ID/revision for PHY AFE workarounds, LED programming, RSS/checksum/VLAN quirks, jumbo frame limitations, ASF/MACSec bypass, PCIe power management, quick-link interrupts, RX truncation, TX checksum behavior, FIFO thresholds, and reset ordering. Regressions in these conditionals can break only specific Yukon-2 revisions.

DMA and ring ownership are central risks. TX mapping unwind must release all partially mapped entries, and completion must not free an skb before the end of a multi-list-element packet. RX buffers may be linear or fragmented, copied or replaced, and resubmitted after error or success. `sky2_put_idx()` uses `wmb()` before notifying hardware; removing or weakening ordering can expose descriptor races. Ring sizes are constrained to powers of two and hardware limits, and RX list-element usage can be multiple elements per skb.

Concurrency risks include hard IRQ versus NAPI, NAPI versus close/MTU change, `start_xmit()` versus TX completion, PHY accesses protected by `phy_lock`, reset work serialized by RTNL, ethtool/debugfs reads that temporarily disable NAPI, and shared IRQ handling on dual-port cards. Power-management and WOL paths also mutate PHY, GMAC, and PCI config state while interfaces may be administratively up.

Error handling is deliberately defensive but broad: hardware error interrupts clear PCI/AER/status bits, parity flags, FIFO underruns/overruns, and descriptor-check interrupts; watchdog can schedule full device restart for lost IRQ or RX hang; checksum inconsistency disables RX checksum offload for old list-element format. These recovery paths should be treated as part of normal operation on problematic hardware.

## Test Signals
Build coverage should include normal, debugfs, PM sleep, and netpoll configurations. Runtime signals include probe/remove for one-port and two-port devices, MSI enabled/disabled and DMI-blacklisted cases, ifup/ifdown cycles, TX/RX traffic with checksum offload, SG, TSO, VLAN RX/TX, RSS hash, multicast/promiscuous modes, MTU changes including jumbo limits, ringparam and coalesce ethtool changes, pause/autoneg settings, MII register ioctls, LED identification, ethtool stats/register/eeprom operations, suspend/resume with and without WOL, shutdown wake configuration, TX timeout recovery, RX hang watchdog recovery, and injected DMA mapping failures.

Hardware-specific test matrices should cover copper versus fiber PHYs, Fast Ethernet versus Gigabit chips, Yukon XL/EC/EC-U/EX/FE/FE+/Supreme/Optima/OptimaEEE/Optima2 variants when available, dual-port shared IRQ behavior, 32-bit versus 64-bit DMA, PCIe versus PCI-X paths, and jumbo-frame feature fallback on chips that disable checksum offload with large MTUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/sky2.c -->
