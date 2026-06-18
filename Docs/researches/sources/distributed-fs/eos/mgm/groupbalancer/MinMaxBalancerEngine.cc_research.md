# sources/distributed-fs/eos/mgm/groupbalancer/MinMaxBalancerEngine.cc

## Purpose
Implements a threshold engine that classifies groups solely by configured minimum and maximum fill percentages.

## Important APIs, types, and functions
`configure()` reads `min_threshold` and `max_threshold`, defaulting to 60% and 90%. `updateGroup()` clears previous classification, marks groups above max as sources, and groups below min as targets. `get_status_str()` reports thresholds and base engine state.

## Control flow
Unlike stddev/freespace engines, `recalculate()` is a no-op because classification does not depend on global aggregates. `updateGroup()` operates on each group's `filled()` value from `data.mGroupSizes`.

## State and persistence
Stores two in-memory threshold fractions. No persistence or external state changes occur.

## Dependencies and integration points
Uses `BalancerEngineUtils.hh` and `common/Logging.hh`. Selected by `groupbalancer.engine=minmax`.

## Risks and test signals
Invalid config is rejected earlier by `GroupBalancer::Configure()` for minmax, but this class still logs conversion errors and keeps defaulted values. Tests should cover exact boundary behavior, missing config defaults, min greater than max, and groups absent from the map.
