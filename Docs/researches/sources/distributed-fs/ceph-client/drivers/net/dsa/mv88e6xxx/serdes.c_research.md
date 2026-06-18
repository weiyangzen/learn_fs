# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/serdes.c

## Purpose
Implements SERDES lane discovery, PCS state decoding, interrupt mapping, ethtool stats, and register dumps for 88E6xxx SERDES-capable chips.

## Important APIs, Types, and Functions
Public functions include `mv88e6xxx_pcs_decode_state`, lane mappers `mv88e6341_serdes_get_lane`, `mv88e6390_serdes_get_lane`, `mv88e6390x_serdes_get_lane`, `mv88e6393x_serdes_get_lane`, stats functions for 6352 and 6390 families, IRQ mapping helpers, and get-regs length/dump helpers. Internal read helpers use page-based 6352 access and Clause 45 6390 lane access.

## Control Flow and State
PCS decode first honors BMSR link status, then derives link, autoneg completion, speed, duplex, and pause from SGMII PHY status. Lane discovery maps current `chip->ports[port].cmode` to SERDES lane addresses and returns negative errno for non-SERDES ports. The 6352 stats path accumulates hardware counters into `chip->ports[port].serdes_stats`; 6390 stats return current 48-bit register values. Register dumps iterate static register lists or page ranges.

## Dependencies and Integration Points
Depends on `phy.h` page reads, Clause 45 PHY reads, `global2.h` scratch SERDES detection, `port.h` cmode values, irqdomain mapping, ethtool string/stats APIs, MII helpers, and phylink link-state semantics.

## Risks and Test Signals
Risks include stale cmode cache causing wrong lane selection, invalid speed decoding, counter read width/order mistakes, and register dump reads from inactive lanes. Test signals include phylink resolution for SGMII/1000BASE-X/2500BASE-X, ethtool stats/registers, SERDES IRQ delivery, and mode transitions on ports 0/5/9/10 depending on chip family.
