<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tsconfig.c -->
# sources/distributed-fs/ceph-client/net/ethtool/tsconfig.c

## Purpose
Implements ethtool netlink GET and SET for active hardware timestamp configuration: selected timestamp provider, TX type, RX filter, and hwtstamp flags.

## APIs, Types, and Functions
Defines `struct tsconfig_req_info`, `struct tsconfig_reply_data`, `ethnl_tsconfig_get_policy`, `ethnl_tsconfig_set_policy`, and `ethnl_tsconfig_request_ops`. Main functions are `tsconfig_prepare_data()`, `tsconfig_reply_size()`, `tsconfig_fill_reply()`, `tsconfig_send_reply()`, `ethnl_set_tsconfig_validate()`, `tsconfig_set_hwprov_from_desc()`, and `ethnl_set_tsconfig()`.

## Control Flow, State, and Persistence
GET requires `ndo_hwtstamp_get`, reads the active kernel hwtstamp config through `dev_get_hwtstamp_phylib()`, converts selected TX/RX enums into single-bit bitsets, preserves flags, then reports an explicit provider from `dev->hwprov` or derives one from `__ethtool_get_ts_info()`. SET requires both hwtstamp netdev ops, rejects absent devices, optionally parses a new provider descriptor, resolves it to either netdev or PHY topology, and fetches current config unless the provider is changing. It updates bitsets for TX type, RX filter, and flags, enforcing exactly one TX type and one RX filter, then validates with `net_hwtstamp_validate()`. If provider changes, current timestamping is disabled, `dev->hwprov` is replaced with RCU cleanup, and modified config is applied via `dev_set_hwtstamp_phylib()`. SET sends an action reply with the new config and has no notification.

## Dependencies and Integration
Depends on net timestamping, PTP clock descriptors, phylib timestamp plumbing, RCU replacement under RTNL, ethtool bitset helpers, provider parsing from `ts.h`, and device hwtstamp netdev ops.

## Risks and Test Signals
Risks include returning early in GET after derived PHC failure without calling `ethnl_ops_complete()`, provider switch leaving timestamping disabled if the later config application fails, single-bit selection edge cases when a bitset becomes zero, and topology lookup ambiguity between netdev and PHY providers. Test signals include GET with explicit `dev->hwprov`, GET fallback to tsinfo, no PHC, provider not in topology, multi-bit TX/RX rejection, flags validation, provider switch with zeroed old config, and action-reply generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ethtool/tsconfig.c -->
