# sources/distributed-fs/ceph-client/samples/rust/hostprogs/Makefile

## Purpose

This Kbuild fragment builds the Rust host program sample named `single`.

## Important APIs, Types, and Functions

It uses `hostprogs-always-y := single` and marks `single-rust := y`, telling Kbuild the host tool is implemented in Rust.

## Control Flow

When the parent Makefile descends into this directory, Kbuild builds the `single` host program and its Rust modules.

## State and Persistence Behavior

Only build artifacts are produced; no kernel runtime state is involved.

## Dependencies and Integration Points

It relies on kernel hostprog Rust support and the `single.rs`, `a.rs`, and `b.rs` files in this directory.

## Risks and Edge Cases

Host Rust compiler availability and Kbuild's module discovery are the main risks.

## Test Signals

Enable `SAMPLE_RUST_HOSTPROGS` and build; the `single` host binary should be produced and print the expected messages when run.
