# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/sky2.h

## Purpose
`sky2.h` is the private hardware contract for the Marvell Yukon-2 `sky2` Ethernet driver. It does not implement the driver by itself; it defines the register map, bit fields, descriptor layouts, per-port state, shared device state, and inline MMIO helpers used by the C implementation. Its scope covers PCI/PCIe configuration windows, core CSR blocks, BMU queues, RAM buffers, GMAC/GPHY/PHY control, WOL, ASF/status units, descriptor opcodes, and hardware statistics access.

## Important APIs, Types, and Constants
Important register addressing helpers include `RAM_BUFFER(port, reg)`, `SK_REG(port, reg)`, `Q_ADDR(reg, offs)`, `Y2_QADDR(q, reg)`, `RB_ADDR(offs, queue)`, `WOL_REGS(port, x)`, `WOL_PATT_RAM_BASE(port)`, and `SK_GMAC_REG(port, reg)`. These encode the chip's banked/port-relative layout and are central to avoiding hard-coded per-port offsets in the implementation.

The header defines PCIe power/clock/ASPM control, global CSR and interrupt state, queue/BMU/prefetch/RAM-buffer/status/polling units, Marvell PHY and GMAC programming fields, and descriptor opcodes/control flags. Core runtime types are `struct sky2_tx_le`, `struct sky2_rx_le`, `struct sky2_status_le`, `struct tx_ring_info`, `struct rx_ring_info`, `enum flow_control`, `struct sky2_stats`, `struct sky2_port`, and `struct sky2_hw`.

Inline helpers expose MMIO access: `sky2_read{8,16,32}()`, `sky2_write{8,16,32}()`, `gma_read{16,32,64}()`, `gma_write16()`, `gma_set_addr()`, `get_stats{32,64}()`, and PCI config-window helpers `sky2_pci_read{16,32}()` / `sky2_pci_write{16,32}()`.

## Control Flow
The header's control flow is declarative: it describes the state transitions the implementation must perform. Reset, power, clock, interrupt, and queue enable flows are represented by paired set/clear bits such as `CS_RST_SET/CLR`, `BMU_RST_SET/CLR`, `PREF_UNIT_RST_SET/CLR`, `RB_RST_SET/CLR`, `GMF_RST_SET/CLR`, `GMC_RST_SET/CLR`, and operational bits such as `BMU_START`, `SC_STAT_OP_ON`, or `GMF_OPER_ON`.

Transmit and receive flow is centered on descriptor ownership and status opcodes. TX and RX descriptors carry address, length, control, and opcode fields; status descriptors report RX status, VLAN/checksum/hash, TX index completion, and put-index notifications. `get_stats32()` and `get_stats64()` implement read-stable loops because multiword GMAC counters cannot be read atomically.

## State and Persistence
No durable persistence exists. State is live kernel/driver state mirrored in registers and DMA rings. `struct sky2_port` keeps ring producer/consumer indexes, pending counts, last checksum/MSS state, link advertising/speed/duplex/WOL flags, flow-control state, DMA mappings, and optional debugfs handle. `struct sky2_hw` keeps shared chip identity, status ring index/DMA address, per-port netdev pointers, feature flags, and watchdog/restart state.

## Dependencies and Integration Points
This file depends on Linux kernel networking, PCI, DMA, MMIO, NAPI, timers/workqueues, and optional debugfs types included by the implementation. It integrates with the associated `sky2.c` driver, the PCI probe path, netdev transmit/receive paths, ethtool statistics, Wake-on-LAN, PHY/GMAC register programming, and interrupt handling. Descriptor structs and opcodes are ABI-like contracts with the Yukon-2 hardware, so layout and endianness are critical.

## Risks
The highest-risk areas are register bit correctness, descriptor packing, endian handling, and DMA ownership ordering. Wrong set/clear semantics can leave queues or PHYs in reset, while a bad opcode/control combination can corrupt TX/RX rings. `get_stats32/64()` can spin longer than expected if hardware counters are unstable. Feature flags must match chip revisions; enabling RSS, VLAN, advanced power, or new descriptor formats on broken hardware variants can produce subtle data corruption or hangs.

## Test Signals
Useful signals include successful PCI probe across Yukon chip IDs/revisions, link-up/link-down and flow-control negotiation, TX/RX with checksum/VLAN/TSO/RSS variants, jumbo MTU up to `ETH_JUMBO_MTU`, ethtool/MIB counter stability, WOL suspend/resume behavior, MSI and legacy interrupt modes, and fault-injection or stress tests around BMU/status-ring errors and reset recovery.
