# sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span_location.rs

## Purpose

This probe covers the span start/end and line/column subset stabilized in Rust 1.88.

## Important APIs, types, and functions

It exports `start`, `end`, `line`, and `column`, forwarding to `proc_macro::Span` methods. `start` and `end` return compiler `Span` values; `line` and `column` extract numeric positions from a span.

## Control flow

Each function is a direct wrapper. Capability is determined entirely by cfg/build probing.

## State and persistence behavior

There is no local state. Returned values are snapshots of compiler span location data.

## Dependencies and integration points

It depends on `proc_macro::Span`. `wrapper.rs` combines these calls to build `LineColumn`, subtracting one from compiler columns to maintain proc-macro2's zero-indexed column contract.

## Risks and test signals

The main risks are off-by-one column conversion, changed compiler semantics for artificial spans, and location APIs being present without meaningful data in some macro contexts. Tests should cover call-site spans, parsed fallback spans, joined spans, and generated tokens with known source positions.
