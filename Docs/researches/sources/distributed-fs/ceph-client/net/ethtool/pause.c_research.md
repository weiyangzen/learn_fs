# sources/distributed-fs/ceph-client/net/ethtool/pause.c

## Purpose
This file implements netlink `PAUSE_GET` and `PAUSE_SET` for pause-frame autonegotiation, RX/TX pause enablement, and optional pause statistics from aggregate/eMAC/pMAC sources.

## Important APIs, Types, And Functions
`struct pause_req_info` stores requested stats source. `struct pause_reply_data` stores `ethtool_pauseparam` and `ethtool_pause_stats`. Key callbacks are `pause_parse_request()`, `pause_prepare_data()`, `pause_reply_size()`, `pause_put_stats()`, `pause_fill_reply()`, `ethnl_set_pause_validate()`, and `ethnl_set_pause()`. `ethnl_pause_request_ops` registers GET and SET.

## Control Flow
Request parsing accepts `ETHTOOL_A_PAUSE_STATS_SRC` only when `ETHTOOL_FLAG_STATS` is set, defaulting to aggregate stats. Preparation verifies `get_pauseparam`, initializes stats, enters ethtool ops, rejects eMAC/pMAC stats when MAC Merge is unsupported, reads pause parameters, and optionally reads pause stats. SET fetches current pause parameters, updates supplied boolean fields using `ethnl_update_bool32()`, and calls `set_pauseparam()` when changed.

## State And Persistence
The file itself is stateless. SET updates driver/device pause configuration; GET snapshots current pause configuration and stats.

## Dependencies And Integration Points
It depends on `ethtool_ops::{get_pauseparam,set_pauseparam,get_pause_stats}` and `__ethtool_dev_mm_supported()` from `mm.c` for eMAC/pMAC source validation. It uses stats-capable common header policy and generic notification `ETHTOOL_MSG_PAUSE_NTF`.

## Risks And Edge Cases
Supplying a stats source without the stats flag is rejected. eMAC/pMAC source requests require MAC Merge support even if a driver might have partial stats. SET policy declares booleans as `NLA_U8` rather than max-1, so nonzero values are normalized by `ethnl_update_bool32()`.

## Test Signals
Tests should cover stats source parsing, aggregate versus eMAC/pMAC requests, unsupported MAC Merge rejection, absent stats hook with stats flag, no-op SET, and notification after change.
