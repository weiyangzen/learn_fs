## sources/distributed-fs/ceph-client/rust/kernel/sizes.rs

Purpose: exposes common Linux `SZ_*` constants to Rust as `usize` module constants and as typed associated constants for device address-width calculations.

Important APIs/types/functions: the `define_sizes!` macro emits constants from `bindings::SZ_*`, the `SizeConstants` trait, and implementations for `u32`, `u64`, and `usize`. Constants range from `SZ_1K` through `SZ_2G`.

Control flow: all behavior is compile-time macro expansion and constant evaluation. Implementations assert each value fits in the target integer type before casting.

State/persistence: no runtime state.

Dependencies/integration: depends on generated C bindings for `include/linux/sizes.h`. Used by drivers for page arithmetic, MMIO windows, heaps, and hardware address-space sizing.

Risks: constants are only as correct as the C bindings. The typed constants intentionally cover only values fitting in `u32`; adding larger sizes would require revisiting the `u32` implementation. Trait constants require type qualification, which may surprise callers expecting module constants.

Test signals: doctests show module-level `usize` use and typed `u64`/`u32` use. Compile-time assertions are the main safety signal for lossless casts.
