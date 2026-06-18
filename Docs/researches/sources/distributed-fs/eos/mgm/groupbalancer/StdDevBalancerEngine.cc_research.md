# sources/distributed-fs/eos/mgm/groupbalancer/StdDevBalancerEngine.cc

## Purpose
Implements the default percentage-deviation balancer engine, classifying groups relative to average fill level.

## Important APIs, types, and functions
`configure()` reads `min_threshold` and `max_threshold` as percent deviations. `recalculate()` sets `mAvgUsedSize` from `calculateAvg()`. `updateGroup()` compares a group's fill ratio to the average, clears old state, marks high positive deviation as source and low negative deviation as target. `get_status_str()` reports average and deviations.

## Control flow
On each group snapshot refresh, the base engine recalculates the average and updates each group. Later `pickGroupsforTransfer()` pairs groups from the classified sets.

## State and persistence
Stores average fill and deviation thresholds in memory only.

## Dependencies and integration points
Uses `BalancerEngineUtils.hh` and EOS logging. It is the default engine created by `GroupBalancer`.

## Risks and test signals
Defaults are passed as `0.05` to `extract_percent_value()`, which divides by 100 and therefore yields `0.0005`, unless this is intentional to represent 0.05 percent. Tests should verify expected default threshold semantics, average calculation on empty maps, boundary equality, and status output.
