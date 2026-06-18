# sources/distributed-fs/ceph-client/drivers/net/phy/phy-caps.h

## Purpose
This internal phylib header declares the link capability abstraction used to convert among speed/duplex pairs, ethtool link modes, PHY interface modes, and link media.

## Important APIs, Types, and Functions
The anonymous enum defines capability indices from 10 half/full through 1.6T full duplex, with `LINK_CAPA_ALL` covering the complete mask. `struct link_capabilities` stores speed, duplex, and an ethtool linkmode mask. Declared functions include `phy_caps_init()`, `phy_caps_speeds()`, `phy_caps_linkmode_max_speed()`, `phy_caps_valid()`, `phy_caps_linkmodes()`, `phy_caps_from_interface()`, lookup helpers by linkmode or speed/duplex, and medium conversion helpers.

## Control Flow
The header itself has no runtime flow, but the declared implementation is intended to initialize capability tables, derive supported speeds, filter by maximum speed, validate requested speed/duplex combinations, and map interface/media constraints into ethtool linkmode sets.

## State and Persistence
There is no state in the header. Implementations likely maintain static capability data initialized by `phy_caps_init()`. Callers pass linkmode bitmaps that are modified or queried.

## Dependencies and Integration Points
It depends on `<linux/ethtool.h>` and `<linux/phy.h>`. The functions are internal phylib glue for PHY drivers, phylink, and ethtool-facing capability reporting.

## Risks
Capability translation tables must stay synchronized with ethtool link mode additions and PHY interface definitions. Incorrect duplex or medium mappings can cause advertised modes, validation, or interface selection to be wrong across many drivers.

## Test Signals
Test speed enumeration ordering, max-speed filtering, validity checks for half/full duplex, interface-to-capability mapping, medium lane filtering, and new ethtool link modes as they are added.
