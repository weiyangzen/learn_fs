# sources/distributed-fs/ceph-client/rust/helpers/platform.c

## Purpose
Exposes platform-device type checking to Rust.

## APIs, Types, and Functions
`rust_helper_dev_is_platform()` wraps `dev_is_platform()`.

## Control Flow, State, and Persistence
No local state; checks the device bus/type state.

## Dependencies and Integration
Depends on `linux/platform_device.h` and Rust platform driver abstractions.

## Risks and Test Signals
Risks are invalid device pointers and incorrect downcasting. Test signals are Rust platform driver probe tests.
