## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_netdev.c

### Purpose
`sparx5_netdev.c` creates, registers, opens, stops, and exposes Linux `net_device` instances for Sparx5 front-panel ports. It bridges Linux netdev operations to phylink, SerDes power management, IFH construction, MACT programming, TC offload, and PTP timestamp configuration.

### Important APIs, Types, And Functions
The file exports `sparx5_create_netdev()`, `sparx5_register_netdevs()`, `sparx5_destroy_netdevs()`, `sparx5_unregister_netdevs()`, and `sparx5_netdevice_check()`. The `sparx5_port_netdev_ops` table wires `ndo_open`, `ndo_stop`, `ndo_start_xmit`, multicast sync, stats, parent ID, TC setup, and hwtstamp get/set callbacks. IFH builders include `sparx5_set_port_ifh()`, `sparx5_set_port_ifh_rew_op()`, `sparx5_set_port_ifh_pdu_type()`, `sparx5_set_port_ifh_pdu_w16_offset()`, and `sparx5_set_port_ifh_timestamp()`.

### Control Flow
Open enables the hardware port, connects phylink to the PHY, starts phylink, and powers up SerDes for fixed-link or in-band modes without `ndev->phydev`. Stop disables the port, stops/disconnects phylink, and powers SerDes down. Netdev creation allocates per-port private storage with TX queues equal to `SPX5_PRIOS`, marks TC offload feature support, attaches ethtool/netdev ops, and generates a MAC from the switch base MAC. Registration iterates existing ports and starts each injection timeout timer.

### State, Persistence, And Dependencies
State lives in `struct sparx5_port` private data, `port->conf`, phylink objects, SerDes PHY state, netdev feature flags, and MACT entries for local MAC addresses. IFH encoding writes a 36-byte header used by the packet injection path. The file depends on `sparx5_port.c`, `sparx5_packet.c`, `sparx5_ptp.c`, `sparx5_tc.c`, ethtool support, MACT helpers, and generated IFH bit positions.

### Integration Points
This file is the Linux networking face of the driver. It integrates with phylink for link negotiation, `sparx5_port_xmit_impl()` for TX, switchdev/bridge code through `sparx5_netdevice_check()`, TC through `ndo_setup_tc`, and PTP through netdev hwtstamp operations.

### Risks
Open error unwinding must leave the port disabled and phylink disconnected. Destroy calls `sparx5_port_stop()` under RTNL and then disconnects phy again, so lifecycle assumptions should be checked around phylink state. IFH bitfield encoding is endian/position-sensitive and allows widths only up to 40 bits. MAC address changes forget and learn entries using the current PVID, so bridge/VLAN state affects host reachability.

### Test Signals
Test netdev register/unregister cycles, open/stop with external PHY and SerDes-only ports, failed `phylink_of_phy_connect()` unwind, MAC address change programming, hwtstamp unsupported when PTP is disabled, TC setup dispatch, parent ID stability, and packet TX IFH fields by hardware or register-level tests.
