# sources/distributed-fs/orangefs/src/io/buffer/flags.h

## Purpose
Defines bit positions and macros for manipulating NCAC extent state flags and access counters.

## Important APIs, Types, And Functions
Provides low-level `test_bit`, `set_bit`, `clear_bit`, `test_and_set_bit`, page/extent flag bits (`PG_locked`, `PG_clean`, `PG_dirty`, `PG_readpending`, `PG_writepending`, `PG_rmw`, etc.), and macros such as `PageDirty`, `SetPageClean`, `ClearPageReadPending`, `IncReadCount`, and `ClearPageFlags`.

## Control Flow
NCAC job and state code uses these macros to move extents through blank, pending read/write, clean, dirty, communication, LRU, active, referenced, and read-modify-write states.

## State And Persistence
Macros mutate the `flags`, `reads`, and `writes` fields of `struct extent` in memory. They perform no locking or atomic CPU operations despite Linux-like names.

## Dependencies And Integration Points
Included throughout the buffer cache. It assumes every target object has `flags`, `reads`, and `writes` fields matching `struct extent`.

## Risks And Test Signals
Risks include non-atomic bit updates, macro side effects, trailing semicolons inside macros, no underflow checks on counters, and no-op `extent_ref_release/get`. Concurrency and state-transition tests should verify flag consistency around read/write completion and eviction.
