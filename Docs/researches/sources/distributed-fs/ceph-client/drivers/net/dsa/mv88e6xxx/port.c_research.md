# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/port.c

## Purpose
Implements Marvell 88E6xxx per-port register programming helpers. It is the chip-variant aware layer used by the main DSA driver to configure link forcing, speed/duplex, RGMII delays, cmode/SERDES mode selection, bridge state, VLAN/FID/PVID behavior, egress tagging, flooding, mirroring, policy actions, jumbo mode, priority remapping, and special EtherType handling.

## Important APIs, Types, and Functions
The base helpers are `mv88e6xxx_port_read`, `mv88e6xxx_port_write`, and `mv88e6xxx_port_wait_bit`, which add `chip->info->port_base_addr` to the logical port and call the common register accessors. Public configuration entry points include `mv88e6xxx_port_set_link`, `mv88e6xxx_port_sync_link`, chip-specific `*_port_set_speed_duplex`, `*_port_set_cmode`, `mv88e6xxx_port_set_state`, `mv88e6xxx_port_set_vlan_map`, `mv88e6xxx_port_get_fid`, `mv88e6xxx_port_set_fid`, `mv88e6xxx_port_get_pvid`, `mv88e6xxx_port_set_pvid`, `mv88e6xxx_port_set_mirror`, `mv88e6xxx_port_set_policy`, `mv88e6393x_port_set_policy`, and TCAM-enabling helpers.

## Control Flow and State
Most functions follow read-modify-write control flow with early error returns. Capability restrictions are encoded by chip-specific wrappers, for example 2500/10000 Mbps only on selected ports and cmode changes only on SERDES-capable ports. Persistent state is split between hardware registers and `chip->ports[port]` fields such as `cmode`, `mirror_ingress`, and `mirror_egress`. FID state spans registers 0x06 and 0x05 on devices with more than 16 databases. `mv88e6393x` policy and EtherType operations use indirect pointer/EPC sequences and busy waits.

## Dependencies and Integration Points
Depends on `chip.h` for device metadata and ops, `global2.h` for monitor destination writes, `port.h` constants, `serdes.h` cmode values, phylink/PHY interface enums, bridge STP states, DSA port iteration, and common `mv88e6xxx_*` register access under the driver's outer locking discipline. The ops table in chip descriptors selects the appropriate functions.

## Risks and Test Signals
Main risks are wrong chip/port capability gates, incorrect bit preservation during read-modify-write, cmode cache drift after failed writes, and indirect register sequences racing if called outside the register lock. Regression signals include phylink mode tests, STP state transitions, VLAN/FID/PVID programming, bridge flooding/mirroring behavior, ethtool or debug register dumps, and hardware tests for 200/2500/5000/10000 Mbps edge cases.
