# sources/distributed-fs/coda/coda-src/util/bitmap7.cc

## Purpose
Implements `bitmap7`, a revised bitmap that preserves the requested logical bit count in `indexsize` while retaining RVM-capable allocation semantics.

## Important APIs, Types, And Functions
The implementation mirrors `bitmap` with custom recoverable `new/delete`, `Resize()`, `Grow()`, `GetFreeIndex()`, `SetIndex()`, `FreeIndex()`, range methods, `CopyRange()`, `Value()`, `Count()`, `Size()`, `purge()`, assignment, inequality, and print helpers.

## Control Flow
Construction records both `mapsize` and `indexsize`. Resize creates a new zeroed map, copies overlapping bytes, frees the old map, updates `indexsize`, and clears bits from the logical end to the rounded byte end. Range copy/set calculate `end_bit`, `start_byte`, and `end_byte` to bulk-copy or bulk-fill whole bytes and handle edge bits individually. Recoverable operations log touched object/map ranges.

## State And Persistence
State is in-memory or RVM-backed depending on `recoverable`. `indexsize` is intended to make operations with `len < 0` stop at the logical end rather than the rounded storage end.

## Dependencies And Integration Points
Depends on `rvmlib`, `util.h`, transaction annotations, and C runtime allocation. It is likely intended as a safer replacement for `bitmap` in code that needs exact logical bounds.

## Risks
`GetFreeIndex()` still scans all rounded storage bits and can return an index beyond `indexsize` if trailing bits are free. `Size()` still returns `mapsize << 3` rather than `indexsize`. Assignment only updates `indexsize` when `mapsize` changes, so same-byte-size assignments with different logical sizes can leave stale logical length.

## Test Signals
Compare behavior against `bitmap`, especially non-multiple-of-eight sizes, grow/shrink cleanup, `len < 0` range operations, allocation at the logical end, recoverable mutation logging, and assignment between maps with equal `mapsize` but different `indexsize`.
