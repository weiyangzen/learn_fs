<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_port.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_port.c

Purpose: Implements PHY port objects that describe physical media-side or MII-side ports, parse firmware connector metadata, derive supported link modes from media/pair/interface data, restrict media choices, and expose a netdev `PORT_*` type.

Important APIs and functions: `phy_port_alloc()` and `phy_port_destroy()` allocate/free `struct phy_port`. `phy_of_parse_port()` parses an `ethernet-connector.yaml`-style DT node into a port, including `media` and BaseT `pairs`. `phy_port_update_supported()` derives or filters `port->supported`. `phy_port_restrict_mediums()` masks medium support and updates link modes. `phy_port_get_type()` returns `PORT_TP`, `PORT_FIBRE`, or `PORT_OTHER`.

Control flow: DT parsing reads a medium string, converts it to an ethtool medium, validates BaseT pair counts as 1, 2, or 4, rejects `pairs` for non-BaseT media, then returns a populated port. Supported-mode update first infers missing `pairs` from already-set supported link modes, then accumulates medium-compatible link modes for every medium bit. If `port->supported` is empty it adopts that mask; otherwise it intersects existing support with medium support. For MII/SFP-style ports without medium data, it derives internal `LINK_CAPA_*` from every set PHY interface mode and expands those to link modes. Restricting mediums rejects an empty result and filters supported modes to the remaining media.

State and persistence: Mutates each `phy_port`'s list node, `supported` bitmap, `mediums`, `pairs`, `interfaces`, `is_mii`, `is_sfp`, parent pointers, and active/not-described flags set by callers. No global state or durable persistence exists.

Dependencies and integration points: Depends on OF/fwnode properties, ethtool medium and pair metadata, `linux/phy_port.h`, and `phy-caps.h`. It is used by `phy_device.c` when parsing `mdi` child nodes, creating default ports, setting up SFP ports, and aggregating port capabilities back into `phydev->supported`.

Risks: Firmware descriptions directly constrain advertised PHY modes; bad `media` or `pairs` values can make probe fail or overly restrict support. `phy_port_update_supported()` preserves manual bits only if they intersect derived support, so call order with PHY driver attach hooks matters. SFP/MII support depends on `port->interfaces` being populated by a driver or SFP flow. `phy_port_restrict_mediums()` prevents empty media sets but can still remove needed modes when passed the wrong mask.

Test signals: Parse valid BaseT 1/2/4-pair and invalid pair values; parse unsupported medium strings; reject `pairs` on non-BaseT; derive supported modes from medium/pairs and from MII interface lists; restrict mediums success and empty-result failure; integration with PHY probe aggregation and `phydev->port` selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_port.c -->
