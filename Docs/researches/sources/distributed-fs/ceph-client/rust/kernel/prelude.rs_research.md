# sources/distributed-fs/ceph-client/rust/kernel/prelude.rs

## Purpose
Defines the common import surface for Rust kernel code, bundling core traits, C FFI aliases, macros, pin-init helpers, allocator types, errors, logging macros, and frequently used kernel utilities.

## APIs, Types, and Functions
Re-exports selected `core::mem` functions and `Pin`, FFI scalar aliases and `CStr`, procedural/helper macros, pin-init traits/macros, allocator containers and flags, build assertions, current task, device and printk logging macros, `Error`/`Result` and errno constants, `InPlaceInit`, `UserPtr`, `ThisModule`, and `dbg`.

## Control Flow, State, and Persistence
There is no runtime control flow or state. The file controls namespace visibility and compile-time ergonomics for downstream modules that use `kernel::prelude::*`.

## Dependencies and Integration
Depends on the crate's allocator, error, init, string, uaccess, print, and macro modules plus external `ffi`, `macros`, and `pin_init` crates. It is imported by most Rust kernel modules and affects public API discoverability.

## Risks and Test Signals
Risks include accidental API bloat, name collisions, making hidden implementation details part of common usage, or removing an export relied on by many drivers. Test signals are broad build coverage, doctests using `prelude::*`, rustdoc visibility checks, and compile-fail tests for intentionally non-prelude APIs.
