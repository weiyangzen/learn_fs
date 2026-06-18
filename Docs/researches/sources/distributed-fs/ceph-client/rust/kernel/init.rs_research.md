# sources/distributed-fs/ceph-client/rust/kernel/init.rs

## Purpose
`init.rs` extends the `pin-init` crate for kernel allocation and initialization patterns. It provides smart-pointer in-place initialization traits and kernel-default fallible initializer macros.

## Important APIs, Types, and Functions
`InPlaceInit<T>` abstracts smart pointers that can allocate and initialize `T` in place. It defines `try_pin_init`, `pin_init`, `try_init`, and `init`, with `PinnedSelf` for pointer-specific pinning behavior. The exported `try_init!` and `try_pin_init!` macros wrap `pin_init` macros with default error type `crate::error::Error`.

## Control Flow
`pin_init` and `init` convert initializer error types into kernel `Error` by wrapping user initializers in unsafe closures that delegate to `__pinned_init`. Smart pointer implementations perform allocation with `Flags` and either run pin or non-pin initialization. The macros pass through to the underlying crate with a default error attribute.

## State and Persistence
The file defines initialization mechanics only. Any persistent state is created in the target object and smart pointer chosen by callers.

## Dependencies and Integration Points
It depends on `pin_init::{Init, PinInit}`, kernel allocation flags, `AllocError`, and `Error`. Many wrappers in this subset use the macros for safe construction of pinned C-backed structs, including GPU buddy lists and devres-managed mappings.

## Risks
Unsafe initializer closures must maintain pin-init rules: no references to uninitialized fields, correct cleanup on failure, and full initialization before success. Incorrect smart pointer implementations can cause moves of pinned data or leaks after partial initialization.

## Test Signals
Compile and runtime tests should cover fallible initialization success, allocation failure, conversion of custom errors to `Error`, pinned non-`Unpin` types, and partial initialization cleanup paths.
