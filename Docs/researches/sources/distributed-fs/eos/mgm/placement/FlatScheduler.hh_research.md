<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FlatScheduler.hh -->
# sources/distributed-fs/eos/mgm/placement/FlatScheduler.hh

Source read size: 62 lines, 2562 bytes.

## Purpose

Declares the flat placement scheduler facade used by EOS MGM scheduling code.

## Important APIs, Types, and Functions

Defines `makePlacementStrategy` and class `FlatScheduler` with constructors, `schedule`, `access`, `accessStategyIndex`, private `scheduleDefault`, `mPlacementStrategy`, and `mDefaultStrategy`.

## Control Flow

The header establishes that all placement calls pass immutable `ClusterData` plus `PlacementArguments`, while access calls pass mutable `AccessArguments`. Strategy implementations are hidden behind `PlacementStrategy` pointers.

## State and Persistence Behavior

Scheduler state is the array of strategy instances plus a default strategy enum. Strategy internals may hold seed/cached weight state; the scheduler itself has no persistence.

## Dependencies and Integration Points

Depends on cluster data and placement strategy abstractions. It is constructed by `FSScheduler` and used for both file placement and replica access choice.

## Risks and Edge Cases

The strategy array is indexed directly by enum ordinals, so enum changes must keep `TOTAL_PLACEMENT_STRATEGIES` and factory behavior aligned. A constructor that creates only one strategy leaves other slots null.

## Test Signals

Compile coverage for every enum strategy, constructor coverage for all-strategy and single-strategy modes, null-strategy error handling, and ABI checks for callers using `accessStategyIndex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FlatScheduler.hh -->
