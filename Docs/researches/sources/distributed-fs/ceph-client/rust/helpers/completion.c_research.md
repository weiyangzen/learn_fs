# sources/distributed-fs/ceph-client/rust/helpers/completion.c

## Purpose
Exposes completion initialization to Rust.

## APIs, Types, and Functions
`rust_helper_init_completion()` wraps `init_completion()`.

## Control Flow, State, and Persistence
The helper initializes caller-provided `struct completion` state and keeps no local state.

## Dependencies and Integration
Depends on `linux/completion.h` and Rust synchronization wrappers.

## Risks and Test Signals
Risks are reinitializing live completions and missing wakeup ordering. Test signals are Rust completion wait/complete KUnit tests and race stress.
