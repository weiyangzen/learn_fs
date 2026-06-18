# sources/distributed-fs/ceph-client/rust/ffi.rs

## Purpose
Defines the kernel-specific Rust mapping of C primitive FFI types, avoiding assumptions baked into `core::ffi` where the kernel compiler flags differ from the platform default.

## APIs, Types, and Functions
The `alias!` macro defines `c_char`, signed and unsigned integer aliases, `c_long`, `c_ulong`, and long-long types, while asserting each alias has the same size as the corresponding `core::ffi` type. It re-exports `c_void` and `CStr` from core.

## Control Flow, State, and Persistence
The crate has no runtime state. All checks occur at compile time through constant assertions. The key semantic choice is mapping kernel `c_char` to `u8` because the kernel uses `-funsigned-char`.

## Dependencies and Integration
Depends on Rust `core::ffi` only for size comparisons and reusable `c_void`/`CStr`. It is consumed by generated bindings and low-level Rust wrappers wherever C ABI types appear.

## Risks and Test Signals
Risks include architectures where kernel ABI type sizes diverge from `core::ffi`, signedness mistakes for `char`, and future C type additions not represented here. Test signals are cross-architecture Rust builds, bindgen output using `ffi::` prefixes, and compile-time assertion failures on unsupported ABI combinations.
