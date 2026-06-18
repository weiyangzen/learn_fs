# sources/distributed-fs/ceph-client/rust/helpers/wait.c

## Purpose
Exposes waitqueue-entry initialization to Rust.

## APIs, Types, and Functions
`rust_helper_init_wait()` wraps `init_wait()`.

## Control Flow, State, and Persistence
Initializes caller-owned waitqueue entry state; no local state.

## Dependencies and Integration
Depends on `linux/wait.h` and Rust waitqueue abstractions.

## Risks and Test Signals
Risks include adding uninitialized or stack-expired entries to waitqueues. Test signals are Rust waitqueue tests and wakeup race stress.
