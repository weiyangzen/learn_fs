# sources/distributed-fs/ceph-client/rust/helpers/maple_tree.c

## Purpose
Exposes maple tree initialization with flags to Rust.

## APIs, Types, and Functions
`rust_helper_mt_init_flags()` wraps `mt_init_flags()`.

## Control Flow, State, and Persistence
Initializes caller-owned maple tree state and persists only in that object.

## Dependencies and Integration
Depends on `linux/maple_tree.h` and Rust data structure wrappers.

## Risks and Test Signals
Risks include reinitializing non-empty trees and wrong flag selection. Test signals are Rust maple-tree wrapper tests and memory-leak checks.
