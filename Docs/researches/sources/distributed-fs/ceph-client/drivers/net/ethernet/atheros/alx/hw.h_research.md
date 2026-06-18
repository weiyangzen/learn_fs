# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/hw.h

## Purpose
Defines the ALX hardware-facing ABI: TX/RX descriptor formats, descriptor bitfield helpers, flow-control and sleep flags, frame-size limits, interrupt masks, hardware statistics layout, `struct alx_hw`, MMIO helpers, and prototypes for `hw.c`.

## Important APIs, Types, and Functions
Descriptor types are `struct alx_txd`, `struct alx_rfd`, and `struct alx_rrd`. `DESC_GET`, `ALX_GET_FIELD`, and `ALX_SET_FIELD` manipulate packed fields. `struct alx_hw_stats` must match ethtool stat strings. `struct alx_hw` stores PCI/MMIO handles, MAC addresses, MTU, interrupt moderation, DMA channel config, RX control image, multicast hash, link state, flow-control/advertisement config, MDIO interface, PHY ids, workaround flag, and accumulated stats. Inline accessors wrap `readl`/`writel`/`readw`/`writew`.

## Control Flow and State
No substantial executable logic beyond inline accessors and `alx_speed_to_ethadv()`. The header defines persistent hardware state that `main.c`, `ethtool.c`, and `hw.c` share.

## Dependencies and Integration Points
Includes MDIO, PCI, VLAN, and `reg.h`. It is central to all ALX files. The descriptor layout is the contract between DMA hardware and driver; the stats struct is the contract between hardware MIB reads and ethtool/netdev stats.

## Risks and Test Signals
Descriptor packing, endian conversions, and bit masks are high risk because corruption affects DMA directly. Tests should validate TSO/checksum descriptor generation, RX error decoding, MTU-derived frame sizes, interrupt mask composition, and stats ordering. Static assertions in code catch some but not all layout drift.
