# sources/cloud-native/nydus/contrib/nydus-backend-proxy/Cargo.toml

## Purpose
This manifest defines the `nydus-backend-proxy` Rust binary crate: a fake HTTP container registry serving Nydus blob files for `nydusd`.

## Important APIs, Types, and Functions
The manifest sets package metadata, Rust 2021 edition, and dependencies on `rocket`, `http-range`, `nix` with `uio`, `clap`, `once_cell`, and `lazy_static`. It also marks this directory as its own workspace.

## Control Flow
Cargo uses the dependency graph to compile the Rocket server and CLI. The `nix` `uio` feature enables positional reads for range streaming.

## State, Persistence, and Dependencies
Persistent state is only build output. Runtime state is implemented in `src/main.rs`. Dependency versions are pinned semver-style.

## Integration Points
It integrates with its Makefile for formatting, debug, release, and static musl builds. Runtime integration is with Nydus clients expecting registry-like blob endpoints.

## Risks and Test Signals
`rocket = 0.5.0` and global workspace isolation matter for dependency resolution. No manifest-level tests exist; behavior is in the source file.
