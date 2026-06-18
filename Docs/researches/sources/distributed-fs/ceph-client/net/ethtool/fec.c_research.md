# sources/distributed-fs/ceph-client/net/ethtool/fec.c

## Purpose
This file implements ethtool netlink GET/SET support for Forward Error Correction modes and optional FEC statistics. It maps legacy `ethtool_fecparam` bit flags to link-mode bitsets and exposes active FEC plus corrected/uncorrectable counters and histograms.

## Important APIs, Types, And Functions
Important local types are `fec_req_info`, `fec_reply_data`, and `fec_stat_grp`. Public objects are `ethnl_fec_get_policy`, `ethnl_fec_set_policy`, and `ethnl_fec_request_ops`. Core helpers include `ethtool_fec_to_link_modes()`, `ethtool_link_modes_to_fecparam()`, `fec_stats_recalc()`, `fec_prepare_data()`, `fec_reply_size()`, `fec_put_hist()`, `fec_put_stats()`, `fec_fill_reply()`, `ethnl_set_fec_validate()`, and `ethnl_set_fec()`.

## Control Flow
GET requires `get_fecparam`, reads current FEC settings, optionally reads stats when `ETHTOOL_FLAG_STATS` and `get_fec_stats` are available, recalculates total/per-lane groups, maps configured and active FEC bits to link modes, and emits modes, auto flag, active mode, and optional stats. SET reads current FEC, maps to link modes and auto flag, applies requested bitset and auto updates, converts back to `ethtool_fecparam`, rejects invalid extra link modes and empty FEC selections, then calls `set_fecparam()`.

## State, Persistence, And Dependencies
Persistent state is driver-owned FEC configuration changed by `set_fecparam()`. Statistics are read-only snapshots. Dependencies include shared link mode names, bitset helpers, ethtool stats initialization, `ethtool_ops` FEC callbacks, and netlink 64-bit stat attribute helpers.

## Integration Points
The request ops cover FEC GET/SET/notification messages. Link-mode naming is shared with EEE and link mode reporting. Legacy ioctl FEC paths use the same driver callbacks but a different userspace ABI.

## Risks
Only FEC NONE, RS, BASER, LLRS, and AUTO map to `ethtool_fecparam`; any leftover link-mode bits must be rejected. `ETHTOOL_FEC_OFF` is represented as link-mode FEC_NONE but active FEC omits NONE/AUTO. Histogram and per-lane stat encoding must handle `ETHTOOL_STAT_NOT_SET` consistently. Drivers returning reserved bits trigger warnings.

## Test Signals
Tests should cover each FEC mode mapping, auto flag changes, invalid extra link modes, empty mode rejection, active FEC reporting, stats with totals only and per-lane values, histogram bins, compact/verbose bitsets, and unsupported callback errors.
