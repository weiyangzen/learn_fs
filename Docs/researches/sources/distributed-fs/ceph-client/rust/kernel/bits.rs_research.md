<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bits.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/bits.rs

## Purpose
This file provides Rust equivalents of common Linux bit macros for fixed unsigned integer types.

## Important APIs, Types, and Functions
The `impl_bit_fn!` macro generates `checked_bit_u64/u32/u16/u8` and const `bit_u64/u32/u16/u8`. The `impl_genmask_fn!` macro generates runtime-checked `genmask_checked_*` and const-build-asserted `genmask_*` functions for the same integer types.

## Control Flow and State
Checked bit functions call `checked_shl` and return `None` on out-of-range shifts. Const bit functions use `build_assert!(n < <$ty>::BITS)` and then shift. Checked genmask functions reject reversed ranges, compute high and low bits through checked helpers, and build `(high | (high - 1)) & !(low - 1)`. Const genmask functions assert `start <= end` and rely on const bit helpers for range validation.

## State and Persistence Behavior
The module is stateless. It computes integer masks from inputs and emits no persistent data.

## Dependencies and Integration Points
It uses `crate::prelude::*` for `build_assert!`, `core::ops::RangeInclusive`, and the `macros::paste` helper. It mirrors `include/linux/bits.h` behavior for Rust kernel code that needs masks without invoking C macros.

## Risks
The const APIs require compile-time provability; misuse with non-constant or invalid values leads to build failures. Runtime APIs return `None` for invalid ranges, so callers must not unwrap unchecked values from untrusted inputs. The mask formula depends on valid high/low bit values and would underflow if range checks were removed.

## Test Signals
Doc examples cover edge single-bit masks, full-width masks, middle ranges, out-of-range endpoints, and reversed ranges for all supported integer widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/bits.rs -->
