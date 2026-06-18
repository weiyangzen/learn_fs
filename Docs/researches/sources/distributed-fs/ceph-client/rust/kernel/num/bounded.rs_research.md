# sources/distributed-fs/ceph-client/rust/kernel/num/bounded.rs

## Purpose
Implements `Bounded<T, N>`, a transparent integer wrapper whose value is guaranteed to fit in `N` low-order bits of an integer backing type. The abstraction is aimed at bitfield-style kernel code where compile-time or runtime proofs about representable ranges are useful.

## APIs, Types, and Functions
Core APIs are `Bounded::new::<VALUE>()`, `try_new`, `from_expr`, `get`, `extend`, `try_shrink`, `cast`, `shl`, and `shr`. `TryIntoBounded` provides fallible conversion from arbitrary integer types. The file implements comparison, arithmetic/bitwise operator forwarding, formatting traits, primitive `From` conversions gated by local size-marker traits, and single-bit bool conversions. `fits_within!` and `fits_within()` are the central range predicates and work for signed and unsigned integer types by shift-roundtripping.

## Control Flow, State, and Persistence
Construction is the only state transition that matters: every public constructor proves the value fits, then delegates to unsafe `__new`, which enforces `N != 0` and `N <= T::BITS` with const assertions. `Deref` rechecks the invariant and uses `unreachable_unchecked` to feed optimizer range knowledge. Arithmetic returns the primitive backing type rather than a new bounded value, avoiding accidental false range guarantees. There is no persistent runtime state.

## Dependencies and Integration
Depends on `kernel::num::Integer`, `Zeroable`, `build_assert`, `const_assert`, and core numeric/formatting traits. It integrates with the kernel Rust numeric module and supports const-generic callers that need type-level bit-width evidence.

## Risks and Test Signals
The main risks are invariant unsoundness in `__new` callers, misuse of `from_expr` on expressions the optimizer cannot prove, signed shift semantics assumptions, and the large macro-generated conversion lattice missing a width or signedness case. Useful test signals are doctests for boundary values, compile-fail tests for invalid bit widths and conversions, runtime signed/unsigned edge checks, bool conversion tests, and generated assembly or MIR inspection for `from_expr` assertions.
