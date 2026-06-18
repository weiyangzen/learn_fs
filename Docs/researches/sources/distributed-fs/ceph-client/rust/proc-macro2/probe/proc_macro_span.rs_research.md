# sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span.rs

## Purpose

This compile-probe module exercises the full unstable `proc_macro::Span` API surface that `proc_macro2` can expose when available.

## Important APIs, types, and functions

It wraps compiler APIs for `byte_range`, `start`, `end`, `line`, `column`, `file`, `local_file`, `join`, and `Literal::subspan`. Under `procmacro2_build_probe` it enables `feature(proc_macro_span)` and includes `RUSTC_BOOTSTRAP` in the cache key.

## Control flow

Each function directly forwards to the matching `proc_macro` method. Failure is compile-time: if a method is unavailable, the probe does not compile and the cfg should not be enabled.

## State and persistence behavior

No runtime state is stored. The module returns spans, ranges, strings, and paths from compiler-owned span state.

## Dependencies and integration points

It depends on `proc_macro::{Literal, Span}`, `core::ops::{Range, RangeBounds}`, and `PathBuf`. `wrapper.rs` uses it for span locations, joining, and literal subspans when `proc_macro_span` is set.

## Risks and test signals

Risks include nightly API signature changes, incorrect cache invalidation, and calling wrappers outside procedural macro contexts. Signals include build-probe success/failure, span-location tests under nightly, and wrapper fallback behavior when the probe is disabled.
