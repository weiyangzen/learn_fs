# sources/distributed-fs/ceph-client/include/linux/array_size.h

## Purpose
Defines generic compile-time array sizing helpers.

## Important APIs, Types, And Functions
`ARRAY_SIZE(arr)` returns element count and adds `__must_be_array(arr)` to reject pointers. `ARRAY_END(arr)` returns a pointer one element past the final array entry.

## Control Flow, State, And Persistence
These are compile-time/runtime-expression macros without independent state. They typically fold to constants for true arrays.

## Dependencies And Integration Points
Depends on `linux/compiler.h` for `__must_be_array`. Integrated widely throughout kernel code for fixed-array bounds and iteration endpoints.

## Risks And Test Signals
The primary risk is passing pointer-like objects where an array is required; `__must_be_array` is the guard. Tests are compile-time: pointer misuse should fail, fixed arrays should compile, and flexible array members should not be mis-sized.
