# sources/distributed-fs/ceph-client/drivers/net/ethernet/spacemit/k1_emac.h

## Purpose
`k1_emac.h` defines the SpacemiT K1 EMAC hardware contract used by `k1_emac.c`: APMU syscon bits, DMA and MAC register offsets, register bitfields, DMA descriptor layouts, and hardware statistic counter unions.

## Important APIs, Types, And Functions
- APMU definitions cover interface selection, reference/function clocks, RMII/RGMII clock choices, PHY IRQ, AXI single-ID mode, and RX/TX delay-line fields.
- DMA register offsets include configuration/control/status/interrupts, poll-demand, base addresses, current pointers, missed frame, and IRQ mitigation.
- MAC register offsets include global/transmit/receive controls, frame/jabber size, address filters, multicast hash tables, flow control, MDIO, stats counters, FIFO thresholds, and MAC interrupts.
- Descriptor bitfields describe RX and TX ownership, first/last descriptors, buffer sizes, ring end, timestamp flags, error/status bits, and interrupt-on-completion.
- `struct emac_desc` is a four-word descriptor with `desc0`, `desc1`, and two buffer addresses.
- `union emac_hw_tx_stats` and `union emac_hw_rx_stats` map ordered 64-bit software counters to hardware counter indices. The array view is intentionally tied to struct member order.

## Control Flow
This header has no executable control flow. Its definitions are consumed by `k1_emac.c` to compose and decode hardware register values with `FIELD_PREP()` and `FIELD_GET()`.

## State And Persistence
The header defines in-memory layouts and symbolic constants. Statistic unions become persistent runtime state when embedded in `struct emac_priv`.

## Dependencies And Integration Points
It depends on Linux bitfield/bitops macros available through included headers and kernel context. It is tightly coupled to the K1 EMAC hardware programming model and the driver assumptions about descriptor size and stats ordering.

## Risks
- The stats unions rely on struct order matching hardware counter numbering; reordering members changes behavior.
- Delay-line field widths and units must match silicon documentation.
- Descriptor address fields are 32-bit in `struct emac_desc` even though the driver enables 64-bit DMA mode, so hardware constraints must be understood before broad platform reuse.
- Typos in macro names such as `MREGBIT_BIG_LITLE_ENDIAN` and `MREGBIT_ACOOUNT_VLAN` are harmless but may complicate future maintenance.

## Test Signals
Compile-time coverage should catch missing macros and type mismatches. Runtime signals are correct register programming, descriptor ownership transitions, ethtool stats counter alignment, and successful traffic at all supported PHY modes/speeds.
