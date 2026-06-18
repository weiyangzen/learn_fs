# sources/distributed-fs/ceph-client/samples/rust/rust_print_events.c

## Purpose

This C companion file instantiates tracepoints used by the Rust printing sample.

## Important APIs, Types, and Functions

It defines `CREATE_TRACE_POINTS` and `CREATE_RUST_TRACE_POINTS`, then includes `<trace/events/rust_sample.h>`.

## Control Flow

There is no runtime function body. The preprocessor definitions cause tracepoint storage and registration code to be generated into this object during build.

## State and Persistence Behavior

Generated tracepoint descriptors become module/kernel static state for the linked `rust_print` object.

## Dependencies and Integration Points

It integrates C tracepoint generation with `rust_print_main.rs`, which declares and calls the Rust-visible tracepoint. The parent Makefile supplies include paths.

## Risks and Edge Cases

Exactly one object should create tracepoints for a given trace header. Missing include paths or mismatched header definitions break build/link.

## Test Signals

Build `rust_print`, load it, and confirm tracepoint availability plus invocation from Rust init.
