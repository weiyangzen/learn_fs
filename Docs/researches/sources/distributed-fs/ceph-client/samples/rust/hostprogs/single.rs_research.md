# sources/distributed-fs/ceph-client/samples/rust/hostprogs/single.rs

## Purpose

This is the entry point for the Rust host-program sample. It demonstrates a Kbuild-built Rust host binary using sibling modules.

## Important APIs, Types, and Functions

The file declares `mod a;` and `mod b;`, then defines `fn main()` using `println!`, `a::f`, and `b::CONSTANT`.

## Control Flow

`main()` prints `Hello world!` and then calls `a::f(42)` through the constant imported from module `b`.

## State and Persistence Behavior

The host program has no durable state and exits immediately after printing.

## Dependencies and Integration Points

It integrates with `hostprogs/Makefile` through `single-rust := y` and uses standard Rust host facilities rather than kernel APIs.

## Risks and Edge Cases

The sample is intentionally simple; risk is limited to Rust hostprog build support.

## Test Signals

Run the resulting `single` binary and verify it prints both the greeting and number line.
