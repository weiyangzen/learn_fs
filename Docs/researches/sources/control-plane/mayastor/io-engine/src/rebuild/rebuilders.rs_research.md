# sources/control-plane/mayastor/io-engine/src/rebuild/rebuilders.rs

## Purpose
This file implements range-walking strategies for rebuilds: full, bitmap-filtered partial, and partial sequential with clean-segment skipping.

## Important APIs, Types, And Functions
`RangeRebuilder<T>` defines `next`, `peek_next`, `blocks_remaining`, `is_partial`, `desc`, and `copier`. `FullRebuild` steps through the descriptor range by segment size. `PartialRebuild` consumes a `SegmentMap` bit vector and schedules set bits. `PartialSeqRebuild` walks the whole descriptor range while `PartialSeqCopier` skips clean blocks and marks successful blocks clean. `PeekableIterator` provides immutable peek over iterators.

## Control Flow
Backends call `next` to get a block address and `copier` to get the copy implementation for that range. Full rebuild always schedules every segment. Partial rebuild iterates set bits and tracks dirty blocks consumed. Partial sequential rebuild schedules all segment starts but makes the copier no-op for clean segments.

## State, Persistence, And Dependencies
Range-walker state is in-memory iterator position, copied descriptor in `Rc`, and for partial sequential rebuild a mutex-protected `RebuildMap`. Dependencies include `SegmentMap`, `RebuildMap`, `BitVec`, `Rc`, and `parking_lot`.

## Integration Points
Bdev rebuild uses `FullRebuild` or `PartialRebuild`. Nexus rebuild uses `FullRebuild` or `PartialSeqRebuild` because it must coordinate with nexus dirty-map behavior.

## Risks
`PartialRebuild::is_partial` returns false despite being partial, likely affecting stats. In `PartialRebuild::next`, the enumerated bit index is returned as a block address without multiplying by segment size, which must match `SegmentMap` iterator semantics or it will address wrong blocks. Partial sequential mode schedules clean segments and only skips during copy, which can add overhead to mostly-clean maps.

## Test Signals
Coverage should validate block addresses from every walker, remaining-block calculations, `is_partial` values, clean-skip behavior, map mutation after success, no mutation after failure, and `PeekableIterator` correctness.
