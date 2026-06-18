# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_ethtool.c

Purpose: Implements ethtool operations for Prestera netdevs: driver info, link settings, advertised/supported modes, port type, MDIX, FEC, statistics names/values, link status, and autoneg restart.

Important APIs/types/functions: Exports `prestera_ethtool_ops`. Internal mapping tables translate Prestera link modes, FEC modes, and port types to ethtool bitsets. Key functions include `prestera_ethtool_get_link_ksettings()`, `prestera_ethtool_set_link_ksettings()`, `prestera_ethtool_get_fecparam()`, `prestera_ethtool_set_fecparam()`, stats string/count/get helpers, and `prestera_ethtool_nway_reset()`.

Control flow: Get link settings either delegates to phylink or composes supported/advertising/lp-advertising from cached port capabilities and firmware reads. Set link settings validates port type and MDIX, converts ethtool advertising to Prestera bitmaps, then chooses autoneg or forced speed/duplex configuration. FEC get reads active firmware MAC mode; FEC set requires autoneg off and rewrites cached MAC configuration through `prestera_port_cfg_mac_write()`.

State and persistence: Uses runtime port state: `caps`, `autoneg`, advertised link modes/FEC, `cfg_phy`, `cfg_mac`, cached MAC/PHY state, and cached hardware stats. Settings are pushed to firmware but not persisted by the driver beyond in-memory port structures.

Dependencies/integration: Depends on `prestera_hw` port PHY/MAC/stat calls, `prestera_main.c` config helpers, phylink for SFP-backed ports, and Linux ethtool core. Stats mirror `struct prestera_port_stats` layout using offset-based macros.

Risks: Mapping tables must stay aligned with firmware enums and ethtool bit definitions. Forced type/speed selection can reject valid combinations if caps are stale. FEC changes while autoneg is on are explicitly blocked. Cached stats may lag hardware by the delayed stats worker.

Test signals: `ethtool -i`, `ethtool <dev>`, advertised mode changes, autoneg on/off transitions, MDIX on copper ports, SFP phylink delegation, `ethtool --show-fec/--set-fec`, stats string count matching struct fields, and link mode tests across copper/fibre/direct-attach port types.
