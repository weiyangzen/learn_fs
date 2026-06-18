# sources/distributed-fs/ceph-client/rust/proc-macro2/probe.rs

## Purpose

This module is the conditional hub for build-probed compiler span APIs used by the wrapper backend.

## Important APIs, types, and functions

It conditionally declares `proc_macro_span`, `proc_macro_span_file`, and `proc_macro_span_location` submodules under their matching cfg flags. It also allows dead code because these files are compile probes and conditional adapters.

## Control flow

There is no runtime logic. The build configuration decides which submodules exist, and `wrapper.rs` imports only the available ones.

## State and persistence behavior

No state is stored. The module expresses capability state through cfg-selected module availability.

## Dependencies and integration points

It integrates with the crate build script/probe results and with `wrapper.rs` span methods such as `byte_range`, `start`, `end`, `file`, `local_file`, `join`, and literal `subspan`.

## Risks and test signals

The risk is cfg skew: wrapper code may assume a probed API exists when the compiler lacks it, or docs/tests may enable incompatible flags. Build matrix tests over stable, beta, nightly, and `procmacro2_nightly_testing` are the main signal.
