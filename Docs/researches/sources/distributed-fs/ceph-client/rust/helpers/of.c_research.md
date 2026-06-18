# sources/distributed-fs/ceph-client/rust/helpers/of.c

## Purpose
Exposes Open Firmware fwnode type checking to Rust.

## APIs, Types, and Functions
`rust_helper_is_of_node()` wraps `is_of_node()`.

## Control Flow, State, and Persistence
No local state; reads fwnode type information.

## Dependencies and Integration
Depends on `linux/of.h` and Rust firmware-node abstractions.

## Risks and Test Signals
Risks are null/invalid fwnode pointers and ACPI-vs-OF branch mistakes. Test signals are device-tree and ACPI build/runtime coverage.
