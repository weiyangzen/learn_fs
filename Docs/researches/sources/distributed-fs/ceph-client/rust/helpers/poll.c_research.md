# sources/distributed-fs/ceph-client/rust/helpers/poll.c

## Purpose
Exposes `poll_wait()` to Rust file operations.

## APIs, Types, and Functions
`rust_helper_poll_wait()` wraps `poll_wait()` for a file, waitqueue, and poll table.

## Control Flow, State, and Persistence
State is registered waitqueue entries in the poll table; no helper-local state.

## Dependencies and Integration
Depends on `linux/poll.h`, file operations, and Rust character/file abstractions.

## Risks and Test Signals
Risks include waitqueue lifetime, null poll table handling, and missed wakeups. Test signals are Rust file poll/select/epoll tests.
