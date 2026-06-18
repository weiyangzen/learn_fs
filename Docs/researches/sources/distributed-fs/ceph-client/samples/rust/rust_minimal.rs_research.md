# sources/distributed-fs/ceph-client/samples/rust/rust_minimal.rs

## Purpose

This is the minimal Rust kernel module sample. It demonstrates module metadata, a typed module parameter, allocation into a kernel vector, init logging, and drop-time cleanup logging.

## Important APIs, Types, and Functions

It uses `module!`, `kernel::Module`, `ThisModule`, `KVec`, `GFP_KERNEL`, `module_parameters::test_parameter.value()`, `pr_info!`, and `Drop`.

## Control Flow

Module init logs startup, whether it is built-in, the `test_parameter` value, allocates a `KVec<i32>`, pushes three numbers, and returns `RustMinimal`. Drop logs the vector and exit message.

## State and Persistence Behavior

State is the `numbers` vector held by the module instance. The module parameter persists through module/kernel configuration while loaded.

## Dependencies and Integration Points

It depends on core Rust kernel allocation and module parameter support.

## Risks and Edge Cases

Allocation failure during vector pushes aborts module init. The sample has no synchronization needs because state is not shared after init.

## Test Signals

Load with default and custom `test_parameter`, verify init logs and unload logs, and build as both built-in and module where supported.
