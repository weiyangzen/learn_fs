<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.h

## Purpose

The header declares `ChunkCopiesCalculator`, the master-side helper for deciding how to transform available chunk parts into a desired goal and how safe the current chunk is.

## Important APIs, Types, and Functions

Public APIs include target setup, part add/remove, `optimize()`, redundancy evaluation/update, safety checks, removal/move queries, label recovery/removal queries, operation counts, full-copy counts, state getters, and mutable access to available/target goals. Internal containers cache per-slice redundancy and operation counts.

## Control Flow

The intended lifecycle is set available/target state, call `optimize()`, then query required recover/delete/move operations and safety. `evalRedundancyLevel()` can be used separately when only state is needed.

## State and Persistence Behavior

The object is an in-memory calculator. `Goal` inputs and outputs may reflect persisted metadata elsewhere, but this class does not write storage.

## Dependencies and Integration Points

It depends on `ChunkPartType`, `ChunksAvailabilityState`, `Goal`, `MediaLabel`, and compact maps/vectors. It is integrated with replication/deletion scheduling and chunk health reporting.

## Risks and Edge Cases

Several getters return mutable references to internal goals, so callers can invalidate cached redundancy/operation counts without the class noticing. Many methods assert valid part indices rather than returning errors. Querying before optimization can return stale/default counts.

## Test Signals

Unit tests in this subset exercise the main lifecycle. Additional tests should cover EC goals, wildcard-heavy goals, mutation through `getAvailable()` after optimization, and large expected-copy limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.h -->
