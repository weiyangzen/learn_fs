# sources/distributed-fs/ceph-client/rust/helpers/device.c

## Purpose
Exposes selected driver-core device helper APIs to Rust.

## APIs, Types, and Functions
Exports `devm_add_action`, `devm_add_action_or_reset`, `dev_get_drvdata`, `dev_set_drvdata`, and `dev_name` wrappers.

## Control Flow, State, and Persistence
State is device-managed action lists and device driver data; helpers only mutate or read the `struct device` fields managed by driver core.

## Dependencies and Integration
Depends on `linux/device.h` and Rust device/driver abstractions.

## Risks and Test Signals
Risks include drvdata type confusion, action callback lifetime, and cleanup ordering during probe failures. Test signals are Rust driver probe/remove tests and devres leak checks.
