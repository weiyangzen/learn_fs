# File Research: sources/block-storage/thin-provisioning-tools/src/write_batcher.rs

## Purpose
Provides a write-back batching layer for metadata block writes, combining allocation through a space map with queued block writes to an `IoEngine`.

## Main Components
- `WriteBatcher` owns:
  - shared `engine`,
  - shared/mutexed metadata `SpaceMap`,
  - `batch_size`,
  - queued `Block`s,
  - `allocations: RangeSet<u64>` recording allocated block numbers.
- `new()` constructs the batcher and preallocates the queue.
- `alloc()` allocates a metadata block and returns an uninitialized `Block::new(loc)`.
- `alloc_zeroed()` allocates and returns `Block::zeroed(loc)`.
- `clear_allocations()` swaps out and returns the allocation range set.
- `write()` checksums a block, updates an already queued block with the same location if present, otherwise flushes when full and appends the block.
- `read()` returns a copy of the most recent queued block for a location or reads through to the engine.
- `flush_()` writes a supplied queue via `engine.write_many()`.
- `flush()` drains and writes the current queue.
- `Drop` asserts that final flush succeeds.

## Behavior
The queue is write-coalescing for blocks still in memory: writing the same location again updates the latest queued copy rather than enqueueing a duplicate. Reads also observe queued writes before durable writes, preserving read-your-writes behavior.

Allocation tracking inserts each allocated block into a `RangeSet`, coalescing adjacent allocations. Comments note that allocations are a hint for potentially modified blocks because callers can later decrement/free blocks through the space map.

## Dependencies and Interactions
This file is used by metadata restore/rebuild paths that need block allocation and batched writes. It depends on project checksum block types, IO engine abstraction, and the metadata space-map trait.

## Research Notes
`flush_()` ignores per-block results inside the `Vec<io::Result<()>>` returned by `write_many()` and only propagates the outer IO error. `Drop` uses `assert!`, so a flush failure during destruction can panic.
