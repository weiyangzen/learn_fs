# sources/distributed-fs/ceph-client/rust/helpers/cred.c

## Purpose
Exposes credential reference management to Rust.

## APIs, Types, and Functions
`rust_helper_get_cred()` and `rust_helper_put_cred()` wrap `get_cred()` and `put_cred()`.

## Control Flow, State, and Persistence
The helpers adjust refcounts on immutable credential objects and keep no local state.

## Dependencies and Integration
Depends on `linux/cred.h` and Rust security/task abstractions.

## Risks and Test Signals
Risks are refcount leaks, use-after-put, and confusing subjective vs objective credentials. Test signals are refcount leak detection and Rust task/cred wrapper tests.
