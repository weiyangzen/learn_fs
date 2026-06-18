<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tsinfo.c -->
# sources/distributed-fs/ceph-client/net/ethtool/tsinfo.c

## Purpose
Implements ethtool netlink timestamp capability and statistics queries, including per-provider filtering and dump traversal across netdev and PHY timestamp providers.

## APIs, Types, and Functions
Defines `struct tsinfo_req_info`, `struct tsinfo_reply_data`, `ethnl_tsinfo_get_policy`, `ethnl_tsinfo_request_ops`, and dump context `struct ethnl_tsinfo_dump_ctx`. Important functions are `ts_parse_hwtst_provider()`, `tsinfo_parse_request()`, `tsinfo_prepare_data()`, `tsinfo_reply_size()`, `tsinfo_fill_reply()`, `tsinfo_put_stats()`, `ethnl_tsinfo_dump_one_netdev()`, `ethnl_tsinfo_dump_one_phydev()`, `ethnl_tsinfo_dump_one_net_topo()`, `ethnl_tsinfo_dumpit()`, `ethnl_tsinfo_start()`, and `ethnl_tsinfo_done()`.

## Control Flow, State, and Persistence
GET optionally parses a provider descriptor. With an explicit provider it calls `ethtool_get_ts_info_by_phc()` and returns that provider's data. Without a provider, it optionally initializes and collects timestamp stats, then calls `__ethtool_get_ts_info()`. Replies encode timestamping capabilities, TX types, RX filters, PHC index, provider descriptor, source, PHY index, and optional stats. Dump setup allocates request and reply data, parses an optional device header, and initializes netdev/PHY cursors. Dumping walks either one device or all devices under RTNL, then for each device emits supported netdev qualifiers and PHY providers from either the legacy `dev->phydev` or `dev->link_topo->phys`. State is only per-dump callback cursor data; no durable configuration is changed.

## Dependencies and Integration
Depends on ethtool timestamp helpers, driver `get_ts_info()` and `get_ts_stats()`, PHY timestamp support checks, link topology XArray iteration, compact bitset encoding, and generic-netlink dump lifecycle hooks.

## Risks and Test Signals
Risks include cursor correctness across partial dump buffers, stats only being available for non-provider-specific GET, PHY topology iteration under concurrent changes, source/PHY index omission when fields are zero, and provider qualifier support drift. Test signals include explicit provider lookup, stats flag output, compact and verbose bitsets, dump of netdev and PHY providers, partial `-EMSGSIZE` dump resume, devices without timestamp ops, and cleanup of allocated dump context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tsinfo.c -->
