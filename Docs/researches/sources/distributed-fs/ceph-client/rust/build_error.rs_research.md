# sources/distributed-fs/ceph-client/rust/build_error.rs

## Purpose
Provides a tiny no-std crate with a const function used by Rust build-time assertion machinery to force compile-time or link/build failures for impossible states.

## APIs, Types, and Functions
The sole API is `build_error(msg: &'static str) -> !`, exported as the C/Rust symbol `rust_build_error`, marked `cold`, `inline(never)`, and `track_caller`. It panics in const evaluation and remains a non-optimized call when a runtime build assertion is not eliminated.

## Control Flow, State, and Persistence
There is no mutable state or persistence. Control flow is deliberately terminal: any executed call panics, while intended use relies on compile-time const evaluation or optimizer elimination.

## Dependencies and Integration
Depends on the Rust core panic path and `rust/Makefile` rules that either build this object as always-needed or export `rust_build_error` under `CONFIG_RUST_BUILD_ASSERT_ALLOW`. It integrates with `build_assert!` in the kernel crate.

## Risks and Test Signals
Risks are optimizer/version behavior changes that fail to eliminate unreachable calls, runtime execution in paths assumed compile-time-only, and missing export for modules using build assertions. Test signals include Rust build assertion tests, negative compile tests, module builds with `CONFIG_RUST_BUILD_ASSERT_ALLOW`, and checking that failing assertions preserve useful caller locations.
