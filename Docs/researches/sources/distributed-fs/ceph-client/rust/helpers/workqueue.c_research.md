# sources/distributed-fs/ceph-client/rust/helpers/workqueue.c

## Purpose
Exposes a Rust-oriented work item initialization helper with lockdep metadata.

## APIs, Types, and Functions
`rust_helper_init_work_with_key()` initializes work data, lockdep map, list head, and function pointer using `__init_work()` and `WORK_DATA_INIT()`.

## Control Flow, State, and Persistence
State is caller-owned `work_struct` initialization and lockdep class association.

## Dependencies and Integration
Depends on `linux/workqueue.h` and Rust workqueue abstractions.

## Risks and Test Signals
Risks include reinitializing queued work, function pointer lifetime/ABI mismatch, and lock class key lifetime. Test signals are Rust workqueue queue/cancel tests and debugobjects/lockdep builds.
