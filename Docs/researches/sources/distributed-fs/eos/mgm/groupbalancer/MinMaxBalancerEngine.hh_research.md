# sources/distributed-fs/eos/mgm/groupbalancer/MinMaxBalancerEngine.hh

## Purpose
Declares the configured min/max fill-percentage balancer engine.

## Important APIs, types, and functions
`MinMaxBalancerEngine` overrides `updateGroup()`, `configure()`, and `get_status_str()`, while `recalculate()` is intentionally empty. `get_min_threshold()` and `get_max_threshold()` are test-facing accessors.

## Control flow
The base engine populates group information and invokes `updateGroup()` for each group. Groups are classified independently from all other groups.

## State and persistence
The class stores `mMinThreshold` and `mMaxThreshold` as doubles. There is no direct persistent state.

## Dependencies and integration points
Inherits `BalancerEngine` and is constructed by the factory for `minmax`.

## Risks and test signals
The thresholds have no in-class initializers, so tests should call `configure()` before using the instance. Header-level tests should assert no aggregate recalculation is required and accessors reflect parsed config.
