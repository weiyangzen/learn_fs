# sources/distributed-fs/eos/mgm/groupbalancer/StdDevBalancerEngine.hh

## Purpose
Declares the standard deviation-from-average balancer engine used as the default group balancer.

## Important APIs, types, and functions
The class overrides `recalculate()`, `updateGroup()`, `configure()`, and `get_status_str()`. Accessors expose min and max deviation thresholds to unit tests.

## Control flow
The base class owns group data; this subclass supplies the average and classification policy. Groups over the average by more than max deviation become sources, and groups under the average by more than min deviation become targets.

## State and persistence
In-memory fields are `mAvgUsedSize`, `mMinDeviation`, and `mMaxDeviation`.

## Dependencies and integration points
Depends on `BalancerEngine.hh` and participates in `BalancerEngineFactory` as the fallback/default engine.

## Risks and test signals
The header does not initialize its doubles, so `configure()`/`recalculate()` ordering matters. Tests should verify constructor plus configure behavior and that status before population is either avoided or deterministic.
