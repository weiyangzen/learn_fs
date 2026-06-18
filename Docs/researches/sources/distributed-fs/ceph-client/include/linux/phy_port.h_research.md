# sources/distributed-fs/ceph-client/include/linux/phy_port.h

## Purpose
Represents physical ports exposed by a PHY, including MDI copper/fiber ports and MII/SerDes ports, with callbacks for link state and MII configuration.

## Important APIs, Types, and Functions
Defines `enum phy_port_parent`, `struct phy_port_ops`, and `struct phy_port`. APIs include `phy_port_alloc()`, `phy_port_destroy()`, `port_phydev()`, `phy_of_parse_port()`, `phy_port_is_copper()`, `phy_port_is_fiber()`, `phy_port_update_supported()`, `phy_port_restrict_mediums()`, and `phy_port_get_type()`.

## Control Flow
PHY drivers allocate or parse ports, attach them to a PHY, update supported modes, restrict advertised media, and invoke ops for out-of-band link changes or MII configuration.

## State and Persistence
`struct phy_port` persists list membership, parent PHY, ops, pair count, medium bitmask, supported link modes, interface bitmap, and flags for described/active/MII/SFP status.

## Dependencies and Integration Points
Depends on ethtool link mode/media definitions, generic Ethernet PHY interfaces, device-tree parsing, and PHY driver attach callbacks in `struct phy_driver`.

## Risks
Incorrect medium/interface masks can advertise impossible links. Active-port state must match physical routing, especially for multi-port PHYs or SFP cages.

## Test Signals
DT port parsing tests, copper/fiber/SFP detection, ethtool advertised mode checks, and multi-port PHY attach tests.
