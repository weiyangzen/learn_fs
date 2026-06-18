# sources/cloud-native/ostree/rust-bindings/tests/tests.rs

Purpose: This is the top-level Rust integration test module that wires submodules into the test binary.

Important APIs, types, and functions: It declares `mod core`, `mod functions`, `mod repo`, `mod util`, and conditionally `mod sign` for feature `v2020_2` or `dox`.

Control flow: Rust test discovery compiles this module, then discovers `#[test]` functions in each child module. The only branch is compile-time feature gating for signing tests.

State and persistence behavior: This file has no runtime state. It controls which test modules can create temporary repos or key material.

Dependencies and integration points: Integrates the test suite modules under `rust-bindings/tests` and applies feature-sensitive coverage selection.

Risks: If a module is omitted here, its tests silently stop running. Feature gating can also hide regressions unless CI runs appropriate feature matrices.

Test signals: Successful compilation confirms the integration test tree is wired; actual behavioral signal comes from the submodules.
