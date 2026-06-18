# sources/distributed-fs/ceph-client/drivers/net/dsa/dsa_loop.c

Purpose: this is a DSA loopback/mock switch driver. It creates a synthetic switch on the fixed MDIO bus, registers fixed PHYs, exposes basic DSA operations, tracks VLAN and PHY-access state, and is mainly useful for DSA framework development and lockdep coverage rather than real packet switching.

Important APIs, types, and functions: `struct dsa_loop_priv` stores the MDIO bus, VLAN table, conduit netdev, and per-port MIB/PVID/MTU state. `struct dsa_loop_vlan` tracks members and untagged ports. Entry points include `dsa_loop_init()`, `dsa_loop_create_switch_mdiodev()`, `dsa_loop_drv_probe()`, `dsa_loop_setup()`, `dsa_loop_phy_read()`, `dsa_loop_phy_write()`, VLAN add/delete/filtering callbacks, MTU callbacks, devlink VTU resource helpers, and module exit cleanup.

Control flow: module init creates an MDIO device at address 31 on bus `fixed-0`, stores platform data naming four LAN ports and an `eth0` CPU conduit, registers fixed PHYs, then registers an MDIO driver whose bus match only accepts this driver. Probe obtains the conduit netdev, fills the CPU port netdev pointer, allocates a DSA switch, attaches loop ops, and registers it. DSA setup initializes per-port MIB names and registers a devlink VTU resource. VLAN add/delete mutate the software VLAN table and deliberately perform a sleeping MDIO read to exercise locking constraints.

State and persistence: all state is volatile module state: global fixed PHY pointers, global switch MDIO device, per-port MIB counters, per-port PVID/MTU, and the software VLAN table. Devlink occupancy reports non-empty VLAN entries. Remove unregisters DSA and drops the conduit netdev reference; module exit unregisters the MDIO driver, fixed PHYs, and MDIO device.

Dependencies and integration points: it uses DSA, fixed PHY, MDIO, phylink, bridge/VLAN switchdev objects, devlink resources, and an existing `eth0` netdev. It returns `DSA_TAG_PROTO_NONE` and supports broad phylink capabilities for test flexibility.

Risks: the hardcoded `fixed-0` bus, MDIO address 31, and `eth0` conduit make it environment-specific. There is no real hardware forwarding, so state only exercises DSA callbacks. VLAN delete does not range-check `vlan->vid` while add does. The init path must unwind fixed PHYs and MDIO device registration correctly on failure.

Test signals: module load/unload, fixed PHY registration, DSA switch registration, devlink VTU occupancy changes after VLAN operations, ethtool stats for PHY read/write success and errors, bridge and STP callback logging, MTU set/get behavior, and lockdep validation around sleeping VLAN callbacks.
