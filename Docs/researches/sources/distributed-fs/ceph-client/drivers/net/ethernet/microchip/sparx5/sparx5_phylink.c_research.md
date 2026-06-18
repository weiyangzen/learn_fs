## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_phylink.c

### Purpose
`sparx5_phylink.c` adapts Linux phylink MAC/PCS callbacks to Sparx5 port and PCS configuration. It selects the per-port PCS, translates phylink negotiation state into `struct sparx5_port_config`, and reports PCS link state back to phylink.

### Important APIs, Types, And Functions
It exports `sparx5_phylink_mac_ops` and `sparx5_phylink_pcs_ops`. Key helpers are `port_conf_has_changed()`, `sparx5_phylink_mac_select_pcs()`, `sparx5_phylink_mac_link_up()`, `sparx5_pcs_get_state()`, and `sparx5_pcs_config()`.

### Control Flow
MAC PCS selection returns `port->phylink_pcs` for SGMII, QSGMII, 1000BASE-X, 2500BASE-X, and Base-R modes; other modes do not use a PCS. Link-up copies current port config, applies resolved speed/duplex/pause, and calls `sparx5_port_config()`. PCS config builds a config from interface, in-band negotiation mode, advertised pause bits, and Base-R media type, skips programming if unchanged, and otherwise calls `sparx5_port_pcs_set()`. PCS state reads hardware via `sparx5_get_port_status()`.

### State, Persistence, And Dependencies
Persistent state is `port->conf`, the phylink PCS object embedded in `struct sparx5_port`, and hardware PCS/MAC registers programmed by `sparx5_port.c`. The file depends on Linux phylink, SFP/PHY interface mode enums, and Sparx5 port helpers.

### Integration Points
Netdev open starts phylink, and phylink invokes these callbacks during negotiation, link-up, and state polling. The PCS callbacks are a key integration point for SerDes, in-band autonegotiation, pause advertisement, and MAC configuration.

### Risks
The expression setting `conf.inband` is true for both disabled and enabled PCS negotiation modes, so interpretation depends on phylink semantics and port code. `mac_link_down()` and PCS autoneg restart are no-ops, making disable/restart behavior rely on later config changes. Base-R media is inferred only from advertised `FIBRE`.

### Test Signals
Test PCS selection for each supported interface, link-up speed/pause propagation, no-op config when unchanged, in-band pause advertisement, Base-R media selection, link state reporting after sticky link-down, and unsupported interface handling.
