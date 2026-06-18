<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/Cargo.toml -->
## sources/cloud-native/ostree/tests/bootc-integration/Cargo.toml

Purpose: defines a standalone Rust workspace/package for bootc OSTree integration tests built inside a container or VM, with one binary named `ostree-bootc-integration-tests`.

Important APIs/types/functions: declares `src/main.rs` as the binary and uses `anyhow`, `libtest-mimic`, `linkme`, `paste`, `quick-junit`, `tempfile`, and `xshell`. `linkme` and `paste` support distributed test registration; `quick-junit` supports optional XML output.

Control flow/state: no runtime logic, but the manifest intentionally separates this test workspace from the repository root workspace. It disables publishing and pins edition 2021.

Dependencies/integration: integrates Rust test harness logic with VM/container execution driven externally by bootc/tmt tooling. Dependencies imply a custom test runner instead of Rust's built-in `#[test]` harness.

Risks/test signals: dependency version drift can affect test registration or JUnit serialization. A successful build is a prerequisite signal before any privileged integration checks can run.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/Cargo.toml -->
