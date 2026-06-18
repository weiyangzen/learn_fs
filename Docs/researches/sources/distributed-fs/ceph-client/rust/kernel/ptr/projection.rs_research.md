# sources/distributed-fs/ceph-client/rust/kernel/ptr/projection.rs

## Purpose
Implements `ptr::project!`, a raw-pointer projection macro for field and index access that preserves provenance and supports fallible bounds checking without requiring the base pointer to be dereferenceable.

## APIs, Types, and Functions
`OutOfBound` converts to `ERANGE`. Unsafe trait `ProjectIndex<T>` defines `get` and build-checked `index`; implementations cover arrays through slice forwarding, `usize`, `Range`, `RangeTo`, `RangeFrom`, and `RangeFull`. Unsafe trait `ProjectField<const DEREF: bool>` computes field offsets, with a guard implementation for `Deref` types to reject projections that could invoke custom deref behavior. `project_pointer!` parses `.field`, `[index]`, and `[index]?` chains for const and mutable raw pointers.

## Control Flow, State, and Persistence
Index projection either returns `None`/`OutOfBound` for runtime-checked forms or triggers `build_error!` when compile-time checking cannot prove safety. Field projection creates an uninitialized local allocation solely to compute field offsets with raw field pointers, then applies the offset to the original base using wrapping byte offsets. Macro expansion repeatedly shadows the projected pointer through each projection component. There is no runtime state.

## Dependencies and Integration
Depends on `MaybeUninit`, `Deref`, `build_error`, `Error`, and the parent `ptr` module. It integrates with low-level code that must compute subobject pointers for MMIO, DMA, packed-compatible checks, or non-address-space pointers.

## Risks and Test Signals
Risks include incorrect unsafe `ProjectIndex` implementations, projection through `Deref` or indexing traits that would be unsound, unaligned field access assumptions, and compiler changes around raw field pointer validity. Test signals include compile-fail tests for out-of-bounds static indexes and `Deref` bases, runtime `ERANGE` tests for `[index]?`, provenance-sensitive Miri-style tests where possible, and packed/unaligned field projection build checks.
