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
