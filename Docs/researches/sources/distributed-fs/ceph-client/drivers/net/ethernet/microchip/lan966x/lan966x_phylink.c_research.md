# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_phylink.c

Purpose: provides LAN966x phylink MAC and PCS operations. It connects Linux phylink state transitions to SerDes mode selection, port link configuration, PCS status/configuration, and link down reset handling.

Important APIs and functions: exported ops are `lan966x_phylink_mac_ops` and `lan966x_phylink_pcs_ops`. MAC callbacks include `lan966x_phylink_mac_select`, `lan966x_phylink_mac_prepare`, `lan966x_phylink_mac_link_up`, and `lan966x_phylink_mac_link_down`. PCS callbacks include `lan966x_pcs_get_state`, `lan966x_pcs_config`, and `lan966x_pcs_aneg_restart`.

Control flow: phylink selects the per-port PCS, optionally programs SerDes Ethernet mode in `mac_prepare`, records speed/duplex/pause in `port->config` on link up, updates RGMII SerDes speed when needed, and calls `lan966x_port_config_up`. Link down calls `lan966x_port_config_down` and releases PCS reset bits. PCS config copies current port config, updates interface/in-band/autoneg/advertising, and delegates to `lan966x_port_pcs_set`.

State and persistence: per-port `lan966x_port_config` persists the active interface, speed, duplex, pause, in-band, autoneg, and advertising data used by port configuration code. Hardware state is programmed by port/PCS helpers and SerDes PHY APIs.

Dependencies and integration points: depends on Linux phylink, PHY/SerDes APIs, LAN966x port config/status helpers, and generated DEV clock reset registers.

Risks and test signals: `mac_config` is empty, so all meaningful changes must be handled in prepare/link_up/PCS config. SerDes mode failures abort link setup. RGMII speed updates assume `port->serdes` is valid when required. Test every supported interface mode, in-band autoneg, pause negotiation, link flap, SerDes mode failures, and PCS state polling.
