# sources/distributed-fs/eos/mgm/groupbalancer/FreeSpaceBalancerEngine.hh

## Purpose
Declares the free-space based `BalancerEngine` implementation for balancing groups toward equal free bytes.

## Important APIs, types, and functions
`FreeSpaceBalancerEngine` overrides `recalculate()`, `updateGroup()`, `configure()`, and `get_status_str()`. Test-facing getters expose expected per-group free space and computed lower/upper limits. `group_set_t` holds blocklisted group names.

## Control flow
The base `BalancerEngine` owns group maps and calls this subclass to compute aggregate free space and classify each group. Calls are synchronized by a private mutex in methods that mutate configuration or computed state.

## State and persistence
Members include `mTotalFreeSpace`, `mGroupFreeSpace`, `mMinDeviation`, `mMaxDeviation`, `mtx`, and `mBlocklistedGroups`. All state is in memory and recomputed from `FsView` snapshots supplied by `GroupsInfoFetcher`.

## Dependencies and integration points
Inherits from `mgm/groupbalancer/BalancerEngine.hh` and participates in `BalancerEngineFactory.hh`. The blocklist is populated from space configuration `groupbalancer.blocklist`.

## Risks and test signals
The header comments state that the getters are not thread-safe on their own and depend on callers holding locks. Tests should instantiate the class through the factory, validate defaults, and verify the monitoring/status strings.
