# sources/distributed-fs/ceph-client/rust/helpers/mutex.c

## Purpose
Exposes mutex operations and lockdep assertions to Rust.

## APIs, Types, and Functions
Exports `mutex_lock`, `mutex_trylock`, `__mutex_init`, lock-held assertion, and `mutex_destroy` wrappers.

## Control Flow, State, and Persistence
State is caller-owned mutex lock state and lockdep class metadata.

## Dependencies and Integration
Depends on `linux/mutex.h` and Rust lock abstractions.

## Risks and Test Signals
Risks include deadlocks, uninitialized locks, destroy while locked, and lock-class lifetime errors. Test signals are Rust mutex tests, lockdep, and PREEMPT_RT builds.
