# sources/distributed-fs/ceph-client/rust/helpers/refcount.c

## Purpose
Exposes refcount initialization and mutation helpers to Rust.

## APIs, Types, and Functions
APIs include `REFCOUNT_INIT`, `refcount_set`, `refcount_inc`, `refcount_dec`, and `refcount_dec_and_test` wrappers.

## Control Flow, State, and Persistence
State is the caller-provided `refcount_t`; no local state.

## Dependencies and Integration
Depends on `linux/refcount.h` and Rust reference-counted wrappers.

## Risks and Test Signals
Risks include underflow, use-after-final-dec, and mixing raw and safe refcount paths. Test signals are refcount saturation/underflow tests and Rust ownership wrapper tests.
