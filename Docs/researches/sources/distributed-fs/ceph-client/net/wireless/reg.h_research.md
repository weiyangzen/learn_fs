# sources/distributed-fs/ceph-client/net/wireless/reg.h

## Purpose

`reg.h` is the internal cfg80211 regulatory header. It declares the regulatory core's public-in-subsystem state and helper APIs used by wireless core files and drivers, including request validation, user/driver/country/beacon hints, wiphy register/deregister handling, DFS helpers, regdb reload, and channel enforcement scheduling.

## Important APIs, Types, and Functions

- `enum ieee80211_regd_source` distinguishes regdomains sourced from the internal database, CRDA, or cached data.
- `cfg80211_regdomain` is the RCU-protected global regulatory domain pointer.
- Request/domain helpers include `reg_is_valid_request()`, `is_world_regdom()`, `reg_supported_dfs_region()`, `reg_get_dfs_region()`, `set_regdom()`, `reg_get_max_bandwidth()`, and `reg_last_request_cell_base()`.
- Hint APIs include `regulatory_hint_user()`, `regulatory_hint_indoor()`, `regulatory_netlink_notify()`, `regulatory_hint_found_beacon()`, `regulatory_hint_country_ie()`, and `regulatory_hint_disconnect()`.
- Wiphy lifecycle APIs include `wiphy_regulatory_register()` and `wiphy_regulatory_deregister()`.
- DFS and channel APIs include `cfg80211_get_unii()`, `regulatory_indoor_allowed()`, `regulatory_propagate_dfs_state()`, `reg_dfs_domain_same()`, `reg_reload_regdb()`, and `reg_check_channels()`.
- Certificate arrays for shipped and extra regdb keys are declared for signed regulatory database support.

## Control Flow

The header defines no flow itself, but it sets the call graph contracts for `reg.c`. Init code calls `regulatory_init()` and `regulatory_exit()`. Drivers and cfg80211 code submit hints through the declared functions. Firmware/CRDA loaders call `set_regdom()` with a source enum. Wiphy lifecycle code calls register/deregister hooks so current regulatory settings are applied to newly registered devices and cleaned on removal.

## State and Persistence Behavior

Persistent state is declared, not owned, here. `cfg80211_regdomain` is externally visible under RCU. The APIs declared here mutate long-lived global regulatory state, per-wiphy regdomains, channel flags, DFS state, beacon-hint lists, cached user domains, indoor state, and pending work in `reg.c`.

## Dependencies and Integration Points

The header includes `net/cfg80211.h` and is included by cfg80211 core files needing regulatory decisions. It connects nl80211 user commands, driver hints, scan/beacon processing, DFS code, and wiphy lifecycle management to the implementation in `reg.c`.

## Risks and Edge Cases

Callers must respect locking and context requirements documented in comments, especially RTNL for DFS propagation and process context for disconnect restore. Misusing `set_regdom()` without a matching outstanding request fails by design. `cfg80211_regdomain` readers need RCU, RTNL, or the relevant wiphy lock depending on the access path.

## Test Signals

Build coverage catches signature drift between `reg.h` and `reg.c`. Runtime tests should validate user hints, indoor netlink ownership cleanup, beacon and country IE hints, DFS propagation, regdb reload, and delayed channel enforcement through the declared APIs.
