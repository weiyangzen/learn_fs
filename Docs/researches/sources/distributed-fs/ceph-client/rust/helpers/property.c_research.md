# sources/distributed-fs/ceph-client/rust/helpers/property.c

## Purpose
Exposes firmware node reference release to Rust.

## APIs, Types, and Functions
`rust_helper_fwnode_handle_put()` wraps `fwnode_handle_put()`.

## Control Flow, State, and Persistence
State is fwnode reference counts; no local state.

## Dependencies and Integration
Depends on `linux/property.h` and Rust fwnode/property wrappers.

## Risks and Test Signals
Risks are put imbalance and using fwnodes after release. Test signals are device property wrapper tests and refcount leak checks.
