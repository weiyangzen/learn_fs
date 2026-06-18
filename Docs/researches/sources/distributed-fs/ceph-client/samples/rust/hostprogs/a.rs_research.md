# sources/distributed-fs/ceph-client/samples/rust/hostprogs/a.rs

## Purpose

This is a tiny Rust host-program module used by `single.rs` to demonstrate splitting a host Rust binary into modules.

## Important APIs, Types, and Functions

It exports `pub(crate) fn f(x: i32)`, which prints `The number is {x}.` with Rust's standard `println!` macro.

## Control Flow

There is no independent entry point. `single.rs` imports module `a` and calls `a::f(b::CONSTANT)`.

## State and Persistence Behavior

The function is stateless and persists nothing.

## Dependencies and Integration Points

It depends on the Rust standard library available to host programs, not kernel Rust APIs.

## Risks and Edge Cases

No material runtime risk; build risk is module path discovery from `single.rs`.

## Test Signals

Running the built `single` binary should include `The number is 42.`
