# sources/distributed-fs/ceph-client/rust/helpers/auxiliary.c

## Purpose
Exposes auxiliary bus device teardown helpers to Rust code.

## APIs, Types, and Functions
`rust_helper_auxiliary_device_uninit()` and `rust_helper_auxiliary_device_delete()` delegate to `auxiliary_device_uninit()` and `auxiliary_device_delete()`.

## Control Flow, State, and Persistence
The helpers mutate auxiliary-device lifecycle state owned by driver core; they keep no local state.

## Dependencies and Integration
Depends on `linux/auxiliary_bus.h` and Rust auxiliary-bus abstractions that need non-inline C entry points.

## Risks and Test Signals
Risks include lifecycle ordering mistakes, double uninit/delete, and mismatched Rust ownership. Test signals are Rust auxiliary-device registration/unregistration tests and driver-core leak checks.
