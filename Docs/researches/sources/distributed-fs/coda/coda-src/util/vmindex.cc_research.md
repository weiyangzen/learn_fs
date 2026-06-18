# sources/distributed-fs/coda/coda-src/util/vmindex.cc

## Purpose
Implements `vmindex`, a growable array of `unsigned long` indexes, and an iterator returning indexes sequentially.

## Important APIs, Types, And Functions
`vmindex::vmindex`, destructor, and `add()` manage storage. `vmindex_iterator::operator()()` returns the next stored value or -1 at end.

## Control Flow
Construction allocates an initial array if size is positive. `add()` doubles capacity or initializes default capacity when full, copies existing entries, and appends. The iterator holds the current array index and advances until `count`.

## State And Persistence
State is heap-only: `indices`, `size`, and `count`. Values are copied by value; no persistence or ownership beyond the array exists.

## Dependencies And Integration Points
Depends on `vmindex.h` and `util.h` for assertions. It is a small legacy alternative to vectors for index lists.

## Risks
Negative or zero constructor size leaves `size` uninitialized in the `else` branch because it assigns `sz = 0` rather than `size = 0`. Iterator end marker `-1` conflicts with valid `unsigned long` values when cast to signed long. No copy protection is declared.

## Test Signals
Construct with positive, zero, and negative sizes; append past growth boundaries; iterate all values; store values near `ULONG_MAX`; and run under sanitizers for uninitialized `size`.
