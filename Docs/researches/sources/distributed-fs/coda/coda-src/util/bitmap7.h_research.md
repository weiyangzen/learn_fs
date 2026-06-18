# sources/distributed-fs/coda/coda-src/util/bitmap7.h

## Purpose
Declares `bitmap7`, the exact-size-aware variant of the Coda bitmap allocator.

## Important APIs, Types, And Functions
It adds `indexsize` to the original bitmap state, retains `recoverable`, `malloced`, `mapsize`, and `map`, and exposes the same custom allocation, index, range, copy, count, comparison, purge, and print interface as `bitmap`.

## Control Flow
Callers create a bitmap with a requested bit count, use index/range methods to mark occupancy, and can request recoverable storage through the second constructor/new argument.

## State And Persistence
The header distinguishes logical bit count from storage byte count. Recoverable mutations are marked with transaction annotations for RVM users.

## Dependencies And Integration Points
Includes `stddef.h`, `stdint.h`, `stdio.h`, and `coda_tsa.h`; implementation uses `rvmlib`.

## Risks
The public `Size()` contract can be ambiguous because implementation returns rounded storage capacity. The same custom allocation caveats as `bitmap` apply.

## Test Signals
Compile and run exact-size boundary tests, especially sizes 0, 1, 7, 8, and 9, plus recoverable construction and range updates.
