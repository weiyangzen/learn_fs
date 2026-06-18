# sources/distributed-fs/ceph-client/rust/helpers/rcu.c

## Purpose
Exposes RCU read-side lock and unlock to Rust.

## APIs, Types, and Functions
`rust_helper_rcu_read_lock()` and `rust_helper_rcu_read_unlock()` delegate to core RCU APIs.

## Control Flow, State, and Persistence
State is current execution context RCU nesting; helpers keep no local state.

## Dependencies and Integration
Depends on `linux/rcupdate.h` and Rust RCU guard abstractions.

## Risks and Test Signals
Risks include nesting imbalance, sleeping in non-sleepable RCU sections, and using protected pointers after unlock. Test signals are lockdep/RCU debug and Rust RCU guard tests.
