# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/zeroable.rs

## Purpose
`zeroable.rs` implements derives for the public `Zeroable` marker trait. It supports strict deriving when all fields must implement `Zeroable` and a maybe-derive mode that silently fails when field bounds are not met.

## Important APIs, Types, And Functions
`derive(input, dcx)` handles `#[derive(Zeroable)]`. `maybe_derive(input, dcx)` handles `#[derive(MaybeZeroable)]`. Both accept structs and unions and reject enums. The generated unsafe impl targets `::pin_init::Zeroable`.

## Control Flow
For strict derive, the macro adds `Zeroable` bounds to type parameters, emits an unsafe impl, and emits a const helper that calls `assert_zeroable::<FieldType>()` for each field to force field validation. For maybe derive, it adds type-parameter and per-field HRTB `Zeroable` where predicates, then emits the unsafe impl; if the predicates are unsatisfied, normal trait selection prevents use rather than producing a custom derive error.

## State And Persistence
The only persistent effect is a trait implementation. No runtime state is generated.

## Dependencies And Integration Points
It depends on `syn`, `quote`, `DiagCtxt`, and the public `Zeroable` trait. The `init!` macro's zeroing trailer and `init_zeroed()` rely on correct `Zeroable` implementations.

## Risks And Edge Cases
Unsafe impl correctness rests on every field accepting the all-zero bit pattern and padding being safe to zero. Enums are rejected because not all discriminant values are valid. Maybe-derive's silent behavior can surprise users if they expect an impl but a field is not zeroable.

## Test Signals
Tests should include structs, unions, generic fields, non-zeroable fields, enums, maybe-derive success/failure, arrays/tuples, and use with `Zeroable::init_zeroed()`.
