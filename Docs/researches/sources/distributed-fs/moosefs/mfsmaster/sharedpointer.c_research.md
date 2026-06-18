# sources/distributed-fs/moosefs/mfsmaster/sharedpointer.c

## Purpose
`sharedpointer.c` is a tiny reference-counted wrapper for a raw pointer plus destructor callback. In this subset it is used by changelog restore/merge code to keep filename strings alive across calls.

## Important APIs, Types, And Functions
The private `shp` struct stores `pointer`, `freefn`, and `refcnt`. `shp_new()` allocates a wrapper with refcount 1. `shp_get()` returns the wrapped pointer. `shp_inc()` increments the count. `shp_dec()` decrements and, at zero, calls `freefn(pointer)` and frees the wrapper.

## Control Flow
Users create a wrapper around an already allocated payload and a destructor function. Ownership is shared by explicit increments and decrements. The module does not copy the payload and does not know its type.

## State, Persistence, And Dependencies
State lives entirely in heap-allocated wrapper objects. There is no persistence and no global registry. Dependencies are only standard allocation and integer headers.

## Integration Points
`restore.c` calls `shp_get()`, `shp_inc()`, and `shp_dec()` for the last processed changelog filename. `merger.c` is the likely creator of filename shared pointers passed to `restore_file()`.

## Risks
There are no null checks, no overflow checks on `refcnt`, and no atomic operations. The helper is single-threaded/manual-lifetime infrastructure. Passing a raw pointer instead of a `shp_new()` result will corrupt memory.

`shp_dec()` silently allows decrement calls when `refcnt` is already zero, then frees again if the wrapper is still reachable, so double-decrement after free remains unsafe.

## Test Signals
Tests should cover creation, get, increment/decrement ordering, destructor invocation exactly once, and integration with `restore_file()` filename switching. Threaded tests are not appropriate unless the implementation is changed.
