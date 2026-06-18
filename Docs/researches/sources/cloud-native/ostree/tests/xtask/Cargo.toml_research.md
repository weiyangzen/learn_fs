# sources/cloud-native/ostree/tests/xtask/Cargo.toml

## Purpose
This manifest defines a standalone dev-only Rust `ostree-xtask` binary used for OSTree integration testing tasks.

## Important APIs, Types, And Functions
It declares package metadata, a separate `[workspace]`, binary `ostree-xtask` at `src/main.rs`, and dependencies `anyhow`, `clap` with derive, `serde` with derive, `serde_json`, `tempfile`, and `xshell`.

## Control Flow
Cargo uses this manifest to compile the xtask binary outside the root workspace. Runtime behavior is implemented in `src/main.rs` and `src/tmt.rs`.

## State And Persistence
The manifest stores tool dependency policy and prevents publishing with `publish = false`. Cargo build artifacts are generated externally under the chosen target directory.

## Dependencies And Integration Points
This integrates with Rust Cargo tooling and external commands used by the xtask, especially `bcvk` and `tmt` through `xshell`.

## Risks
Because it declares a separate workspace, dependency versions are not inherited from the root. Dependency drift can affect dev tooling while leaving main project builds untouched.

## Test Signals
Successful `cargo run --manifest-path tests/xtask/Cargo.toml -- run-tmt ...` or `cargo check` validates the manifest and dependency graph.
