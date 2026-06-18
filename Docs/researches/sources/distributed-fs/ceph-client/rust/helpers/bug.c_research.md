# sources/distributed-fs/ceph-client/rust/helpers/bug.c

## Purpose
Makes kernel BUG/WARN primitives callable from Rust.

## APIs, Types, and Functions
`rust_helper_BUG()` is noreturn and delegates to `BUG()`. `rust_helper_WARN_ON()` returns whether the condition triggered `WARN_ON()`.

## Control Flow, State, and Persistence
State is limited to kernel warning/bug side effects such as logs and taint state; no local state is kept.

## Dependencies and Integration
Depends on `linux/bug.h` and Rust assertion/panic-adjacent abstractions.

## Risks and Test Signals
Risks are using `BUG()` where recoverable error handling is expected and test environments treating warnings as failures. Test signals are KUnit warning tests and build configs with BUG disabled or altered.
