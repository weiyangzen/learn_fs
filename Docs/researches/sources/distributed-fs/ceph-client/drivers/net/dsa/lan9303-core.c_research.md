# sources/distributed-fs/ceph-client/drivers/net/dsa/lan9303-core.c

Purpose: bus-independent DSA core for SMSC/Microchip LAN9303-family three-port Ethernet switches, including switch discovery, reset sequencing, indirect switch/PHY access, DSA registration, special tag setup, bridge separation, FDB/MDB programming, STP state, MIB statistics, and phylink MAC handling.

Important APIs/types/functions: exports `lan9303_register_set`, `lan9303_indirect_phy_ops`, `lan9303_probe()`, `lan9303_remove()`, and `lan9303_shutdown()`. Core helpers include `lan9303_read()`, `lan9303_read_wait()`, `lan9303_write_switch_reg()`, `lan9303_read_switch_reg()`, ALR cache helpers, virtual PHY helpers, and `lan9303_switch_ops`.

Control flow: probe initializes mutexes, handles optional reset GPIO, performs a byte-order dummy read, waits for `HW_CFG_READY`, validates LAN9303/LAN9354 IDs, disables user-port processing, detects PHY address strapping, and registers a three-port DSA switch. DSA setup requires CPU port 0, clears virtual PHY Turbo MII, enables special VLAN tagging, separates ports 1/2 by default, enables CPU processing, and traps IGMP to port 0. Bridge join switches into bridged mode only when both user ports share a bridge; leave restores separation.

State and persistence: runtime state is in `struct lan9303`: PHY address base, bridge flag, cached SWE port state, reset metadata, indirect and ALR mutexes, and static ALR cache. Hardware state lives in ALR, tagging, mirror, port-state, MIB, flow-control, and MAC registers and is rebuilt after reset.

Dependencies and integration: Linux DSA, phylink, regmap, GPIO descriptors, OF, MII/PHY, bridge/VLAN helpers, Ethernet address helpers, and `DSA_TAG_PROTO_LAN9303`. I2C/MDIO front-ends provide `regmap`, `dev`, and PHY ops.

Risks and test signals: watch indirect-register timeouts, EEPROM/I2C arbitration delays, ALR cache divergence, unsupported VLAN-aware MDBs, port-0 CPU assumptions, and limited accepted chip IDs. Test DSA registration, isolated default forwarding, bridge join/leave traffic, FDB/MDB add/delete/dump, STP transitions, PHY strap detection, ethtool stats, and xMII phylink speed/duplex/pause.
