# sources/distributed-fs/ceph-client/rust/helpers/sync.c

## Purpose
Exposes lockdep key registration and unregistration to Rust synchronization primitives.

## APIs, Types, and Functions
APIs are `rust_helper_lockdep_register_key()` and `rust_helper_lockdep_unregister_key()`.

## Control Flow, State, and Persistence
State is lockdep's global key registry for caller-owned `lock_class_key` objects.

## Dependencies and Integration
Depends on `linux/lockdep.h` and Rust lock-class management.

## Risks and Test Signals
Risks include unregistering keys too early, leaking registered keys, and conditional lockdep behavior. Test signals are lockdep-enabled Rust lock tests and module unload checks.
