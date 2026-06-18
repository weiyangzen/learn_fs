# sources/distributed-fs/eos/mgm/groupbalancer/BalancerEngineTypes.hh

## Purpose
Defines shared types for EOS group balancing: group lifecycle status, size/capacity records, maps/sets used by engines, engine configuration maps, engine type enum, and a helper for deciding whether an engine should average fill levels.

## Important APIs, types, and functions
`GroupStatus` models `ON`, `OFF`, `DRAIN`, `DRAINCOMPLETE`, and `DRAINFAILED`. `getGroupStatus(std::string_view)` parses status text. `GroupStatusToStr()` formats a status. `GroupSizeInfo` stores status, used bytes, and capacity, with `swapFile()`, `usedBytes()`, `capacity()`, `filled()`, `draining()`, and `on()`. Type aliases define `group_size_map`, `threshold_group_set`, `groups_picked_t`, and `engine_conf_t`. `BalancerEngineT` selects stddev, minmax, freespace, or `total_count`. `engine_should_average()` returns false for freespace and true for the other engines.

## Control flow
Fetchers and orchestration code create `GroupSizeInfo` objects, concrete engines classify them, and selected transfer pairs are represented as `groups_picked_t`. Simulated or planned transfers can call `swapFile()` to update two group sizes in memory before reclassification.

## State and persistence
`GroupSizeInfo` is a small value object and does not persist directly. The aliases define the shape of in-memory snapshots and configuration maps. `std::less<>` on maps enables heterogeneous lookup by `std::string_view` or `std::string` without allocations when used carefully.

## Dependencies and integration points
Depends only on standard integer/string/map/set headers. It is included by base and concrete balancer engines, factories, group-size fetchers, and code that interprets engine status/configuration.

## Risks and test signals
`getGroupStatus("drainfailed")` returns `GroupStatus::DRAINCOMPLETE`, which conflicts with the declared `DRAINFAILED` enum and `GroupStatusToStr()` branch; this is a likely bug. `GroupStatusToStr(DRAINCOMPLETE)` returns `"drained"` while parsing expects `"draincomplete"`, so round trips are asymmetric. `GroupSizeInfo::filled()` divides by capacity without a zero guard and returns a fraction, not a percent. `swapFile()` can underflow used bytes if asked to move more than the source contains and ignores target capacity. Tests should cover status parse/format round trips, zero-capacity groups, transfer underflow/overflow, heterogeneous map lookup, and `engine_should_average()` for each enum including `total_count`.
