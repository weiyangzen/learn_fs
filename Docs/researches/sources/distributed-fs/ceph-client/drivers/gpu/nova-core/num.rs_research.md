# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/num.rs

Purpose: numeric conversion helper module staging safe cast utilities for Nova-Core until equivalent kernel crate support is available.

Important APIs and types: `impl_safe_as!` generates const lossless widening conversion functions such as `u32_as_usize`. `FromSafeCast<T>` and `IntoSafeCast<T>` provide infallible architecture-checked conversions. `impl_const_into!` generates compile-time checked narrowing for constants. `bounded_enum!` creates enums backed by `kernel::num::Bounded` with `From` or `TryFrom` conversion behavior.

Control flow: all logic is compile-time or simple inline conversion. `bounded_enum!` uses match arms and `EINVAL` for unknown bounded values when a `TryFrom` mode is requested.

State and persistence: no runtime state. The module preserves numeric invariants at compile time and call sites.

Dependencies and integration: depends on `kernel::static_assert!`, `build_assert!`, `kernel::num::Bounded`, and `paste`. Used by register, firmware, and VBIOS code to avoid lossy `as` conversions.

Risks: conversion availability is architecture-config dependent. Missing implementations can surface only on 32-bit or 64-bit build variants. Macro-generated code must stay consistent with kernel-supported integer widths.

Test signals: doctest-like examples in comments, compile coverage for both CONFIG_32BIT and CONFIG_64BIT, and call-site type checking are the main signals.
