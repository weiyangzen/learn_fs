<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_caps.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/phy_caps.c

Purpose: Maintains a normalized mapping between ethtool link modes and PHY speed/duplex capabilities, then provides lookup, validation, conversion, max-speed filtering, interface capability, and medium/pair filtering helpers for the rest of phylib.

Important APIs and functions: `phy_caps_init()` initializes the static `link_caps` table from `link_mode_params`. `phy_caps_speeds()` returns distinct supported speeds. `phy_caps_lookup_by_linkmode()` and `phy_caps_lookup_by_linkmode_rev()` choose fastest or slowest matching capabilities. `phy_caps_lookup()` matches speed/duplex against a supported mask with exact or fallback behavior. `phy_caps_linkmode_max_speed()` removes modes above a speed limit. `phy_caps_valid()` checks if a speed/duplex pair exists in a linkmode set. `phy_caps_linkmodes()` expands internal `LINK_CAPA_*` bitmasks to ethtool link modes. `phy_caps_from_interface()` maps PHY interface modes to possible speeds. `phy_caps_medium_get_supported()` and `phy_caps_mediums_from_linkmodes()` translate between media/pair metadata and linkmode masks.

Control flow: At module init, `phy_caps_init()` iterates every ethtool link mode, checks pair-count consistency, converts speed/duplex to an internal capability slot, and sets that linkmode bit. Lookup helpers then scan the resulting table in ascending or descending speed order. Medium filtering walks `link_mode_params`, keeping special non-medium bits and including modes whose medium and pair constraints match.

State and persistence: The `link_caps` array is marked `__ro_after_init`; after initialization it is effectively read-only kernel state. Helper functions mutate caller-provided linkmode bitmaps but maintain no per-device state.

Dependencies and integration points: Depends on `linux/ethtool.h`, `linux/linkmode.h`, `linux/phy.h`, and `phy-caps.h`. It is consumed by core helpers, port handling, generic PHY link status resolution, max-speed DT policy, interface capability derivation, and PHY probing.

Risks: The internal `LINK_CAPA_*` enum must track every meaningful speed/duplex in `link_mode_params`; unknown non-`SPEED_UNKNOWN` entries make `phy_caps_init()` fail. Descending lookup semantics prefer full duplex at the same speed because of table order. Medium and pair calculations rely on ethtool metadata correctness. `phy_caps_from_interface()` must be updated when new PHY interface modes or aggregate interfaces appear.

Test signals: Boot/module init after ethtool link-mode changes; unit-style validation that known linkmodes map to expected speeds and duplexes; max-speed clamping for PHY and port masks; interface-to-capability checks for RGMII, SGMII, USXGMII, Base-X, 10G/25G/50G/100G modes; medium/pair filtering for BaseT 1/2/4-pair and fiber modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/phy_caps.c -->
