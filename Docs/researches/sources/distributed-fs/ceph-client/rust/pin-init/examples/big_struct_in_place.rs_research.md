# sources/distributed-fs/ceph-client/rust/pin-init/examples/big_struct_in_place.rs

## Purpose
This example demonstrates why `pin-init` supports in-place construction: a `BigStruct` with a 1 GiB array can be initialized directly in heap memory without first materializing the whole value on the stack.

## Important APIs, Types, And Functions
`BigStruct` contains a 1 GiB `buf`, scalar fields, and a `ManagedBuf`. `ManagedBuf::new()` returns `impl Init<Self>` using `init!(ManagedBuf { buf <- init_zeroed() })`. `main()` uses `Box::init(init!(BigStruct { ... }))` when `std` or `alloc` is available.

## Control Flow
The initializer zeroes the big array in place, writes scalar fields, initializes `managed_buf` through its own initializer, allocates the final `Box`, and prints the size of the initialized value. No stack-sized temporary `BigStruct` is constructed.

## State And Persistence
State lives only in the allocated `Box<BigStruct>` during `main`. The example has no external persistence.

## Dependencies And Integration Points
It depends on `pin_init::*`, the `alloc`/`std` features for `Box::init`, and `init_zeroed()`. It is a documentation and regression signal for large in-place initialization.

## Risks And Edge Cases
The huge allocation can fail or be unsuitable for constrained test environments. The example is feature-gated for allocation support, so no meaningful work happens without `std` or `alloc`. It mainly tests stack avoidance rather than business logic.

## Test Signals
Useful signals are successful run without stack overflow, allocation-failure behavior, correct reported size, and ensuring code generation does not create large stack temporaries.
