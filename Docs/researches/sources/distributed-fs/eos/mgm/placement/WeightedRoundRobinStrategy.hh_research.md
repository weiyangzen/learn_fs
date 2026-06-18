<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.hh -->
# sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.hh

Source read size: 44 lines, 2215 bytes.

## Purpose

Declares the weighted round-robin placement strategy.

## Important APIs, Types, and Functions

Defines class `WeightedRoundRobinPlacement : PlacementStrategy` with constructor, `placeFiles`, `access`, destructor, and private PIMPL `Impl`.

## Control Flow

Public methods dispatch to the `.cc` implementation. `access` is part of the virtual interface but currently returns an error in the implementation.

## State and Persistence Behavior

In-memory state lives in the PIMPL and tracks weight counters across placement calls.

## Dependencies and Integration Points

Included by `FlatScheduler`; selected through `PlacementStrategyT::kWeightedRoundRobin`.

## Risks and Edge Cases

The class comment repeats weighted-random wording, which can confuse maintainers. Because access is not supported directly, callers must rely on scheduler-level remapping or handle `EINVAL`.

## Test Signals

Compile and virtual dispatch coverage, construction/destruction, strategy selection through `makePlacementStrategy`, and scheduler access fallback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.hh -->
