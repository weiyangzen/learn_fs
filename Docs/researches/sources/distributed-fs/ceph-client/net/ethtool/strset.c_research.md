<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/strset.c -->
# sources/distributed-fs/ceph-client/net/ethtool/strset.c

## Purpose
Serves ethtool string-set queries over netlink, combining global static string sets with per-device and PHY-provided sets. It supports both full string payloads and counts-only responses.

## APIs, Types, and Functions
Defines `struct strset_info`, `info_template`, `struct strset_req_info`, `struct strset_reply_data`, `ethnl_strset_get_policy`, and `ethnl_strset_request_ops`. Key functions are `strset_parse_request()`, `strset_include()`, `strset_prepare_set()`, `strset_prepare_data()`, `strset_reply_size()`, `strset_fill_string()`, `strset_fill_set()`, `strset_fill_reply()`, and `strset_cleanup_data()`.

## Control Flow, State, and Persistence
Parsing optionally walks nested string-set requests and records requested `ETH_SS_*` IDs in a bitmap-like `u32`; counts-only is honored when explicit string sets are supplied. Preparation copies `info_template` into reply data. Nodev queries are allowed only for non-device string sets. Device queries may resolve a PHY, enter ethtool ops, and for each included per-device set ask driver or PHY ops for count and strings; allocated per-device string arrays are marked for cleanup. Reply sizing and filling skip empty sets, include set ID and count, and include indexed string values unless counts-only was requested. The file maintains no persistent state beyond static global string tables.

## Dependencies and Integration
Depends on ethtool string tables from `common.h`, driver `get_sset_count()` and `get_strings()`, optional `ethtool_phy_ops`, PHY resolution via ethtool header flags, and netlink nesting helpers. The static sets include features, RSS hash functions, tunables, link modes, message classes, WoL modes, timestamping names, UDP tunnel types, and standard stats names.

## Risks and Test Signals
Risks include `ETH_SS_COUNT` exceeding the `u32` request bitmask, driver count changing between count and strings retrieval, allocation cleanup on partial failure, nodev requests accidentally asking for per-device sets, and string names with missing static arrays. Test signals include global nodev query, per-device stats/test/private flags queries, counts-only mode, PHY stats fallback, unknown string-set ID rejection, and cleanup after allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/strset.c -->
