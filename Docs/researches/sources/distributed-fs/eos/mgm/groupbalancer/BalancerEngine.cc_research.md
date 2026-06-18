# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngine.cc

## Purpose
Implements the common, policy-neutral part of the EOS group balancer engine. It stores per-group size information, delegates threshold classification to derived engines, chooses source/target group pairs for transfers, and renders status for humans and monitoring.

## Important APIs, types, and functions
`populateGroupsInfo()` resets current state, moves in a `group_size_map`, then calls virtual `recalculate()` and `updateGroups()`. `clear_threshold()`, `clear_thresholds()`, and `clear()` maintain `BalancerEngineData`. `updateGroups()` reclassifies every known group by calling virtual `updateGroup()`. `pickGroupsforTransfer()` chooses a random over-threshold source and under-threshold target using `common::getRandom()`. `pickGroupsforTransfer(uint64_t index)` does deterministic round-robin selection through `common::pickIndexRR()`. `generate_table()` formats selected groups with used bytes, capacity, and fill value. `get_status_str()` returns either compact monitoring counters or a detailed human report with average fill/range and source/target tables.

## Control flow
The base engine receives a complete group-size snapshot, recalculates engine-specific thresholds, and rebuilds source/target sets. Transfer picking first verifies that both sets are non-empty; empty sets cause debug logging, a threshold recalculation, and an empty pair. Non-empty sets are selected independently, either randomly or by index, so pairing is not tied to relative imbalance magnitude in the base class.

## State and persistence
All state is in-memory inside `BalancerEngineData`: the full `mGroupSizes` map and two sets of group names over and under the active policy threshold. No persistence occurs here; upstream group balancer orchestration is responsible for fetching group sizes and acting on picked pairs.

## Dependencies and integration points
Depends on `BalancerEngine.hh`, `BalancerEngineTypes.hh`, policy helpers from `BalancerEngineUtils.hh`, EOS logging, `TableFormatterBase`, and common container/random utilities. Derived engines such as stddev, minmax, and freespace supply `recalculate()`, `updateGroup()`, and `configure()` implementations while inheriting common status and picking behavior.

## Risks and test signals
`GroupSizeInfo::filled()` returns a ratio, while status labels and average text print `%`; tests should confirm whether downstream helpers expect 0..1 or 0..100. `pickGroupsforTransfer()` recalculates on empty sets but does not re-run `updateGroups()` before returning `{}`, so callers must tolerate a no-op cycle. Selection from `std::set` is stable by lexicographic ordering for round-robin but random selection depends on the shared random helper. Tests should cover empty source/target sets, single-source/single-target behavior, deterministic index wrapping, status output in monitoring/detail modes, groups erased from `mGroupSizes`, and derived-engine classification after `populateGroupsInfo()`.
