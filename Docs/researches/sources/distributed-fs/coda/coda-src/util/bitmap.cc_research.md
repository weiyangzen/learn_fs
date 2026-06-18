# sources/distributed-fs/coda/coda-src/util/bitmap.cc

## Purpose
Implements the original `bitmap` class for tracking allocation/free status of indexed elements, with optional RVM-backed allocation and mutation logging.

## Important APIs, Types, And Functions
Custom `operator new(size_t,int)` allocates either heap or recoverable memory. `Resize()`, `Grow()`, `GetFreeIndex()`, `SetIndex()`, `FreeIndex()`, range helpers, `CopyRange()`, `Value()`, `Count()`, `Size()`, `purge()`, assignment, inequality, and print methods provide bitmap operations.

## Control Flow
Construction infers whether the object came from custom `new`, records `recoverable`, allocates `mapsize = (inputmapsize + 7) >> 3`, and zeroes the map. Mutators call `rvmlib_set_range()` before changing recoverable bytes. `GetFreeIndex()` scans bytes for a zero bit, sets the high-to-low bit, and returns the index. Resize allocates a fresh map, copies overlapping bytes, frees the old map, and updates object fields.

## State And Persistence
State is `recoverable`, `malloced`, `mapsize`, and `map`. With `recoverable` set, object and map bytes live in RVM and must be changed inside transactions; otherwise they are ordinary heap state. `Size()` reports byte capacity times eight, not the originally requested logical index count.

## Dependencies And Integration Points
Depends on `rvmlib`, `util.h`, `CODA_ASSERT`, and C runtime allocation. It is used by Coda components that allocate ids or slots and can place the allocation bitmap in recoverable storage.

## Risks
The stack-vs-new detection is a historical hack and the destructor asserts the object was allocated via custom `new`. `CopyRange()` appears to call `SetValue()` on `this` instead of destination `b` in the all-bit path. `SetRangeValue()` uses `memset(..., value, ...)`, so a set range writes `0x01` rather than `0xff` for full bytes. Logical size is rounded up to whole bytes, so trailing spare bits can be allocated.

## Test Signals
Run `testbitmap`, allocation until full, resize grow/shrink, range set/free/copy on byte-aligned and unaligned ranges, recoverable transaction tests, destructor/purge paths, and checks that spare trailing bits do not leak into callers that expect exact logical size.
