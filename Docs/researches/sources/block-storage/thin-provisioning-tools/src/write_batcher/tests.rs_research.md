# File Research: sources/block-storage/thin-provisioning-tools/src/write_batcher/tests.rs

## Purpose
Tests `WriteBatcher` allocation tracking, out-of-space behavior, batched writes, write coalescing, and read-your-writes behavior.

## Main Components
- `MockEngine` implements `IoEngine` with `mockall`.
- `MockTestSpaceMap` implements both `RefCount` and `SpaceMap`.
- `NR_BLOCKS` is `65536`.
- `runs_out_of_space_should_fail()` allocates every block from a real `CoreSpaceMap` and verifies the next allocation fails.
- `allocated_ranges_should_be_coalesced()` returns shuffled block allocations from a mock space map, then verifies `RangeSet` coalesces them into `0..65536`.
- `writes_should_be_performed_in_batch()` expects three `write_many()` calls of 16 blocks after writing 48 blocks with batch size 16.
- `write_hit()` writes the same block twice, expects only one durable write, and verifies the second payload wins.
- `read_hit()` writes a block, reads it before flushing, and verifies the queued payload is returned.

## Behavior Under Test
The tests confirm:
- allocation failure surfaces as an error,
- `RangeSet` allocation tracking is independent of allocation order,
- full queues flush automatically,
- repeated writes to a queued block are coalesced,
- reads consult the queue before the engine.

## Dependencies and Interactions
The tests use `mockall`, `rand` shuffling and deterministic `SmallRng`, checksum block type `BT::NODE`, `CoreSpaceMap`, and IO buffer traits from the main IO engine abstraction.

## Research Notes
The batching test relies on `Drop` to flush final batches where applicable. The mock engine expectations focus on batch size and payload equivalence rather than testing per-block error propagation.
