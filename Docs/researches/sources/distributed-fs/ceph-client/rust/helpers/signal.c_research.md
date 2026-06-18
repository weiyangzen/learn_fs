# sources/distributed-fs/ceph-client/rust/helpers/signal.c

## Purpose
Exposes signal-pending checks to Rust.

## APIs, Types, and Functions
`rust_helper_signal_pending()` wraps `signal_pending()` for a task.

## Control Flow, State, and Persistence
No local state; reads task signal state.

## Dependencies and Integration
Depends on `linux/sched/signal.h` and Rust task/wait abstractions.

## Risks and Test Signals
Risks include stale task pointers and checking the wrong task context. Test signals are interruptible wait tests and signal delivery races.
