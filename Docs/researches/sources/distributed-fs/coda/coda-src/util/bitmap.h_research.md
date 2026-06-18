# sources/distributed-fs/coda/coda-src/util/bitmap.h

## Purpose
Declares the original recoverable-capable `bitmap` class used to track occupied/free indices.

## Important APIs, Types, And Functions
The type defines allocation markers `BITMAP_NOTVIANEW` and `BITMAP_VIANEW`, bit constants `ALLOCMASK` and `HIGHBIT`, private `SetValue()` and `SetRangeValue()`, custom placement-like `new` with a recoverable flag, and public resize, allocation, range, count, assignment, comparison, purge, and print APIs.

## Control Flow
Callers allocate with `new bitmap(size, recable)` when heap or RVM ownership is needed, mutate bits through index/range APIs, and free with `delete` or `purge()`.

## State And Persistence
The declaration exposes no map internals but defines in-object flags that control heap versus RVM-backed persistence. Mutating APIs are annotated with transaction attributes where needed.

## Dependencies And Integration Points
Depends on `stdint.h`, `stdio.h`, and `coda_tsa.h` transaction annotations. The implementation binds it to `rvmlib`.

## Risks
The API reports rounded capacity, not an exact logical length. Copy/assignment and range operations require destination maps to be appropriately sized. The custom allocation contract is nonstandard and fragile for stack instances.

## Test Signals
Compile transaction-annotated callers, verify recoverable and nonrecoverable allocation, and exercise all index/range methods through the implementation.
