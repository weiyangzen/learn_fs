# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/serdes.h

## Purpose
Defines SERDES register addresses, interrupt bits, lane IDs, PCS operational constants, and public SERDES/PCS helper prototypes.

## Important APIs, Types, and Functions
Important definitions include 6352 fiber page and interrupt registers, 6390 lane IDs, 10G/SGMII/USXGMII register offsets, SGMII PHY status bits, 6393X POC and power/reset bits, and errata register fields. It declares lane lookup, IRQ mapping, stats, get-regs, PCS decode, and external PCS ops descriptors. Inline wrappers `mv88e6xxx_serdes_get_lane` and `mv88e6xxx_serdes_irq_mapping` gate optional chip ops.

## Control Flow and State
The only executable logic is optional-ops dispatch in inline helpers. Persistent state is hardware-defined: lane identity and PCS mode are inferred from port cmode and SERDES registers, not stored in this header.

## Dependencies and Integration Points
Includes `chip.h` and forward-declares `phylink_link_state`. Used by `serdes.c`, `port.c`, PCS implementation files, chip descriptors, and interrupt setup paths.

## Risks and Test Signals
Risks are ABI-style: wrong lane IDs or bit masks break link setup, interrupts, and stats. Test signals are compile coverage for all chip descriptors, SERDES link-up in each supported interface mode, interrupt status decode, and ethtool register dumps matching known hardware values.
