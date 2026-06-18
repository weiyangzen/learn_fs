<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/stats.c -->
# sources/distributed-fs/ceph-client/net/ethtool/stats.c

## Purpose
Implements standard ethtool netlink statistics groups and exports helpers that aggregate MAC merge EMAC/PMAC statistics into aggregate counters.

## APIs, Types, and Functions
Defines `stats_std_names`, per-group statistic name arrays, `struct stats_req_info`, `struct stats_reply_data`, `ethnl_stats_get_policy`, and `ethnl_stats_request_ops`. Main functions are `stats_parse_request()`, `stats_prepare_data()`, `stats_reply_size()`, `stat_put()`, group serializers such as `stats_put_mac_stats()` and `stats_put_rmon_stats()`, and aggregation exports `ethtool_aggregate_mac_stats()`, `ethtool_aggregate_phy_stats()`, `ethtool_aggregate_ctrl_stats()`, `ethtool_aggregate_pause_stats()`, and `ethtool_aggregate_rmon_stats()`.

## Control Flow, State, and Persistence
Requests must include a nonempty stats group bitset and may request aggregate, EMAC, or PMAC source. `stats_prepare_data()` resolves the PHY, enters ethtool ops, rejects EMAC/PMAC source when MAC merge is unsupported, initializes all counters to `ETHTOOL_STAT_NOT_SET`, stamps source fields, and invokes PHY or driver group callbacks only for requested groups. Reply sizing counts requested groups and possible counters, including RMON histograms. Serialization nests each group with group ID and string-set ID, then emits only counters not left at `ETHTOOL_STAT_NOT_SET`; 64-bit alignment is handled explicitly. Aggregation helpers query EMAC and PMAC variants and sum each u64 counter while preserving not-set semantics.

## Dependencies and Integration
Depends on ethtool bitset helpers, phylib stats helpers, driver stats callbacks, MAC merge support detection, netlink nested attribute encoding, and string-set names consumed by `strset.c`.

## Risks and Test Signals
Risks include group struct layout assumptions in generic aggregation, not-set sentinel handling during sums, reply size over/underestimation for sparse counters and histograms, PHY fallback behavior, and source validation for devices without MAC merge. Test signals include empty group rejection, group bitset parsing by names and indexes, aggregate versus EMAC/PMAC requests, not-set counters being omitted, RMON histogram ranges, 64-bit alignment on strict architectures, and aggregation where one or both sources are unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/stats.c -->
