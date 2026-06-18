# sources/distributed-fs/ceph-client/samples/rust/Makefile

## Purpose

This Kbuild file maps Rust sample Kconfig symbols to kernel objects and configures one C/Rust mixed sample for trace events.

## Important APIs, Types, and Functions

It adds `ccflags-y += -I$(src)` for trace event headers, lists `obj-$(CONFIG_SAMPLE_RUST_...) += ...o`, defines `rust_print-y := rust_print_main.o rust_print_events.o`, and descends into `hostprogs` when `CONFIG_SAMPLE_RUST_HOSTPROGS` is enabled.

## Control Flow

During build, Kbuild evaluates each config symbol. Most entries compile a single `.rs` object. `rust_print.o` is a composite built from Rust main code plus C tracepoint definition code.

## State and Persistence Behavior

It has no runtime state. Its persistent effect is build dependency shape.

## Dependencies and Integration Points

It integrates with Rust-for-Linux Kbuild support, C tracepoint include rules, and the Kconfig file in the same folder.

## Risks and Edge Cases

The trace include path is required for generated trace headers; removing it can break `rust_print_events.c`. Composite object naming must match the module name selected by Kconfig.

## Test Signals

Build all enabled Rust samples and verify each configured module object appears; specifically check that `rust_print` links both Rust and C objects.
