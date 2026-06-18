# sources/distributed-fs/ceph-client/rust/pin-init/examples/error.rs

## Purpose
`error.rs` defines a tiny example error type used by other `pin-init` examples to unify infallible and allocation-failure paths.

## Important APIs, Types, And Functions
`pub struct Error` is a marker error. It implements `From<Infallible>` by matching the impossible value and, under `alloc`, implements `From<AllocError>` by returning `Error`.

## Control Flow
There is no substantive control flow beyond conversion implementations. The dead-code `main()` only creates the type.

## State And Persistence
The error type has no fields and carries no persistent state.

## Dependencies And Integration Points
It depends on `core::convert::Infallible` and optionally `std::alloc::AllocError`. Other examples import it where `? Error` initializers need an error type that can absorb allocation or impossible errors.

## Risks And Edge Cases
Because it is fieldless, it discards detailed allocation error context. That is acceptable for examples but not a rich production error model.

## Test Signals
Tests can compile examples that convert `Infallible` and `AllocError` into this type and verify feature-gated allocation conversions compile only when expected.
