# sources/distributed-fs/ceph-client/rust/helpers/list.c

## Purpose
Exposes basic Linux intrusive list initialization and insertion to Rust.

## APIs, Types, and Functions
Exports `rust_helper_INIT_LIST_HEAD()` and `rust_helper_list_add_tail()`.

## Control Flow, State, and Persistence
Mutates caller-owned `list_head` links; no local state is kept.

## Dependencies and Integration
Depends on `linux/list.h` and Rust intrusive list abstractions.

## Risks and Test Signals
Risks include double insertion, missing initialization, and aliasing/lifetime errors around containing structs. Test signals are list insertion/removal KUnit tests and debug-list builds.
