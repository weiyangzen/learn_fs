# sources/distributed-fs/eos/mgm/groupbalancer/StdDrainerEngine.hh

## Purpose
Declares the balancer-engine variant used by the group drainer workflow.

## Important APIs, types, and functions
`StdDrainerEngine` overrides `recalculate()`, `updateGroup()`, and `configure()`. `get_threshold()` exposes configured threshold for validation.

## Control flow
The engine follows the common `BalancerEngine` populate/update/pick contract but interprets over-threshold groups as drain sources and under-threshold groups as acceptable destinations.

## State and persistence
Fields are `mAvgUsedSize` and `mThreshold`, both transient.

## Dependencies and integration points
Inherits `BalancerEngine`. `GroupDrainer` constructs it directly rather than via the standard factory.

## Risks and test signals
As with other engines, uninitialized doubles require configuration before use. Tests should verify construction in `GroupDrainer`, threshold parsing, and interactions with `GroupStatus` values.
