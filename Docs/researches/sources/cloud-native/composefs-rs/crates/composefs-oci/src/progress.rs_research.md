# sources/cloud-native/composefs-rs/crates/composefs-oci/src/progress.rs

## Purpose

`progress.rs` is a compatibility shim. Progress types now live in the core `composefs` crate, and this module re-exports them so existing `composefs-oci` users can keep importing `crate::progress::*` while migrating to `composefs::progress`.

## Important APIs, Types, and Functions

- `pub use composefs::progress::*;` re-exports the production progress API, including reporter traits/types and helpers such as `ProgressEvent`, `ProgressReporter`, `SharedReporter`, `NullReporter`, `ComponentId`, `ProgressRead`, `ProgressUnit`, and any other upstream progress items.
- `#[cfg(any(test, feature = "test"))] pub use composefs::progress::test_support;` re-exports progress test support only for test builds or when the crate `test` feature is enabled.

There are no local structs, functions, or implementations in this file.

## Control Flow

The file has no runtime control flow. Compilation conditionally exposes `test_support`, then publicly re-exports everything from `composefs::progress`.

## State and Persistence Behavior

This module owns no state and performs no persistence. It affects API compatibility only.

## Dependencies and Integration Points

The only dependency is the workspace/core `composefs` crate. Internal modules such as `lib.rs` and `oci_layout.rs` import progress symbols through `crate::progress`, while the actual implementations are provided by `composefs::progress`. Tests in `lib.rs` use `crate::progress::test_support::RecordingReporter` through the gated re-export.

## Risks and Edge Cases

- This shim couples the `composefs-oci` progress API surface to `composefs::progress`; upstream renames or removals are immediately reflected here.
- `test_support` is not available in normal builds unless the `test` feature is enabled. Production code must not depend on it.
- Because this is a wildcard re-export, rustdoc and downstream imports may expose more items than the OCI crate explicitly needs.

## Test Signals

There are no local tests. Coverage comes from callers, especially the OCI layout progress integration tests in `lib.rs`, which import `NullReporter`, `ProgressEvent`, `SharedReporter`, and test support through `crate::progress`.
