# sources/distributed-fs/eos/mgm/groupbalancer/GroupsInfoFetcher.cc

## Purpose
Fetches current group capacity and usage data from `FsView` for a configured space, applying group-status filters and averaging or summing filesystem counters.

## Important APIs, types, and functions
`eosGroupsInfoFetcher::fetch()` locks `FsView::gFsView.ViewMutex`, verifies the space exists in `mSpaceGroupView`, iterates each `FsGroup`, converts its `status` config to `GroupStatus`, applies `is_valid_status()`, computes used bytes and capacity through either `AverageDouble()` or `SumLongLong()`, skips zero-capacity groups, and returns a `group_size_map`.

## Control flow
Balancer and drainer loops call `fetch()` before populating engine state. The `do_average` flag determines whether per-filesystem statistics are averaged or summed, with freespace balancing explicitly using summed values.

## State and persistence
No durable state is modified. The method reads live filesystem view state and returns a new map.

## Dependencies and integration points
Uses `FsView`, `FsGroup` config members, `GroupStatus` helpers, and `GroupSizeInfo`. It is the data source for all engines in this subset.

## Risks and test signals
The method logs and returns an empty map for unknown spaces, which disables picking but may mask configuration mistakes. Tests should cover missing spaces, status filtering, average versus sum mode, zero capacity, and multiple statuses including drain states.
