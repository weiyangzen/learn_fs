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
