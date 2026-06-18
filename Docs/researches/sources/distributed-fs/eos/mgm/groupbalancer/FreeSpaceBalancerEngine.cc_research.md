# sources/distributed-fs/eos/mgm/groupbalancer/FreeSpaceBalancerEngine.cc

## Purpose
Implements a balancer engine that classifies groups by absolute free space rather than used-percentage deviation.

## Important APIs, types, and functions
`configure()` reads `min_threshold`, `max_threshold`, and `blocklisted_groups`. `recalculate()` sums capacity and used bytes across non-blocklisted ON groups, then computes expected free space per participating group. `getFreeSpaceULimit()` and `getFreeSpaceLLimit()` derive deviation bounds. `updateGroup()` classifies groups with too much free space as targets and groups with too little free space as sources. `get_status_str()` reports engine state and blocklisted groups.

## Control flow
After `populateGroupsInfo()`, the base engine calls `recalculate()` and `updateGroup()` per group. Blocklisted groups are excluded from totals and classification. Balancer scheduling then picks one source from `mGroupsOverThreshold` and one target from `mGroupsUnderThreshold`.

## State and persistence
Stores total free space, computed per-group free space, min/max deviation fractions, and an in-memory blocklist protected by `mtx`. No persistent storage is modified.

## Dependencies and integration points
Uses `BalancerEngineUtils.hh` for config parsing and `common/Logging.hh` for errors. `GroupBalancer` selects this engine via `groupbalancer.engine=freespace` and disables average mode in `eosGroupsInfoFetcher`.

## Risks and test signals
`mTotalFreeSpace` and `mGroupFreeSpace` are not explicitly initialized in the header, so status before first recalculation can expose indeterminate values. `mGroupFreeSpace` is not reset when all groups are filtered out. Tests should cover blocklist exclusion, zero participating groups, integer division, threshold boundaries, and thread-safe concurrent status/config/update calls.
