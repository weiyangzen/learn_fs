# File Research: sources/cow-pools/bcachefs-tools/package-ci/Cargo.toml

## Purpose
Rust package manifest for the bcachefs package CI orchestrator.

## Contents
- Workspace root and binary package `bcachefs-package-ci`.
- Rust edition 2021.
- Binary entrypoint at `src/main.rs`.

## Dependencies
- `anyhow`
- `log`
- `env_logger`
- `serde`, `serde_json`
- `chrono` with clock support
- `libc`
- `signal-hook`

## Integration
This manifest builds the filesystem-backed Debian package CI daemon described in `src/main.rs`.
