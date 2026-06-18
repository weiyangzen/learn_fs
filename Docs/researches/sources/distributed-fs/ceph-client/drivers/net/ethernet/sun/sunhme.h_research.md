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
