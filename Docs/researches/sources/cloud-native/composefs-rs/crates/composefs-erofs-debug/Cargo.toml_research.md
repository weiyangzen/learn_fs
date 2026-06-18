# sources/cloud-native/composefs-rs/crates/composefs-erofs-debug/Cargo.toml

Purpose: declares the unpublished `composefs-erofs-debug` binary crate, described as an EROFS image debugging tool.

Important APIs/types/functions: the manifest has package metadata inherited from the workspace for edition, license, readme, repository, Rust version, and version. Runtime dependencies are `clap` with a minimal feature set (`std`, `help`, `usage`, `derive`) and the workspace `composefs` crate.

Control flow: Cargo builds a single default binary from `src/main.rs`; no custom bin/test targets are declared here. Workspace lint settings apply through `[lints] workspace = true`.

State and persistence: the manifest itself has no runtime state. It configures a local diagnostic tool that reads EROFS images and emits deterministic debug output.

Dependencies and integration points: the tool integrates tightly with `composefs::erofs::debug::debug_img` and `clap::Parser`. `publish = false` keeps it internal to the repository.

Risks: because this crate is unpublished and minimal, regressions are most likely to come from changes to the `composefs` debug API or workspace lints. The reduced clap feature set is intentional but means shell completions/color/env support are absent unless added.

Test signals: no crate-local tests are declared. Confidence comes from workspace builds and any tests that compare EROFS/debug output or use the tool manually for deterministic diffs.
