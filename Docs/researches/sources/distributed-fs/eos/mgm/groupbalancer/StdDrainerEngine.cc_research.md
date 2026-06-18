# sources/distributed-fs/eos/mgm/groupbalancer/StdDrainerEngine.cc

## Purpose
Implements the engine used by group draining: draining groups are sources, and underfilled ON groups are targets.

## Important APIs, types, and functions
`configure()` reads `threshold`. `recalculate()` computes average fill. `updateGroup()` marks `GroupStatus::DRAIN` groups as over-threshold sources and marks ON groups under average by more than the threshold as under-threshold targets; a zero threshold allows any ON group below average to be a target.

## Control flow
`GroupDrainer` fetches both DRAIN and ON groups, populates this engine, and then repeatedly asks for transfer pairs. The source set is therefore the set of groups explicitly marked for drain.

## State and persistence
Stores average fill and threshold in memory. Persistent changes happen in `GroupDrainer`, not this engine.

## Dependencies and integration points
Uses `BalancerEngineUtils.hh`, EOS logging, and `GroupSizeInfo::draining()/on()`. Owned by `GroupDrainer`.

## Risks and test signals
The method does not explicitly clear a non-draining group's prior source/target entries before classification, relying on base refresh behavior. Tests should cover draining groups, ON groups above/below average, zero threshold, and empty maps.
