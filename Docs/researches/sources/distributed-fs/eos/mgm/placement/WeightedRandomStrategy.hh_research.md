<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.hh -->
# sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.hh

Source read size: 44 lines, 2192 bytes.

## Purpose

Declares the weighted-random placement strategy.

## Important APIs, Types, and Functions

Defines class `WeightedRandomPlacement : PlacementStrategy` with constructor, `placeFiles`, `access`, destructor, and private PIMPL `Impl`.

## Control Flow

The public methods delegate to `Impl` in the `.cc` file after base validation. PIMPL hides the random distribution cache and locking.

## State and Persistence Behavior

Strategy state is in-memory distribution data owned by `Impl`. No persistence is done.

## Dependencies and Integration Points

Included by `FlatScheduler` and used for both placement and weighted access choices.

## Risks and Edge Cases

The header comment says weighted random based on disk sizes; if future weights include utilization or admin overrides, documentation and tests need updating. PIMPL lifetime must remain stable for strategy array storage.

## Test Signals

Compile construction/destruction, virtual dispatch through `PlacementStrategy`, and integration tests through `FlatScheduler` for weighted-random placement and access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.hh -->
