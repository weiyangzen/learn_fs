# sources/distributed-fs/ceph-client/rust/proc-macro2/probe/proc_macro_span_file.rs

## Purpose

This probe covers the subset of `proc_macro::Span` file APIs stabilized in Rust 1.88.

## Important APIs, types, and functions

It exports `file(&Span) -> String` and `local_file(&Span) -> Option<PathBuf>`, each forwarding to the compiler span method.

## Control flow

There is no branching. The module exists only if the probed compiler supports these methods.

## State and persistence behavior

It has no state and returns compiler-derived path/display data. The distinction between display file and local file is important because `local_file` can reveal real disk paths.

## Dependencies and integration points

It depends on `proc_macro::Span` and `PathBuf`. `wrapper.rs` uses it when both `span_locations` and `proc_macro_span_file` are configured; otherwise compiler-backed spans fall back to placeholder file data or `None`.

## Risks and test signals

Risks include accidentally exposing remapped paths where display paths are expected, or relying on local file data in generated macro output. Tests should assert file/local_file behavior under stable compilers that support the APIs and fallback defaults when disabled.
