# sources/distributed-fs/ceph-client/samples/rust/rust_driver_faux.rs

## Purpose

This minimal Rust module demonstrates creation of a faux device through the Rust faux-device abstraction.

## Important APIs, Types, and Functions

It uses `module!`, `kernel::Module`, `faux::Registration::new()`, `pr_info!`, and `dev_info!`. `SampleModule` stores the registration so the device remains registered until module drop.

## Control Flow

Module init logs startup, registers a faux device named `rust-faux-sample-device`, logs through the device, and returns the module state.

## State and Persistence Behavior

The only persistent state is `_reg: faux::Registration`, whose lifetime controls device registration. No user data is stored.

## Dependencies and Integration Points

It depends on the kernel faux device support exposed to Rust. It is intended as a registration/lifetime sample rather than a functional driver.

## Risks and Edge Cases

Failure to register returns an error from module init. Because the module name string is `rust_faux_driver` while the Kconfig help says `rust_driver_faux`, packaging should be checked in builds.

## Test Signals

Load the module and verify the init and device log messages; unload should unregister the faux device through RAII.
