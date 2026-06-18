# sources/cloud-native/nydus/Cargo.toml

## Purpose
This is the root Cargo manifest for the Nydus Rust workspace and main `nydus-rs` package. It defines binaries, library target, dependencies, feature flags, profiles, workspace members, and shared workspace dependency versions.

## Important APIs, Types, and Functions
The package exports binaries `nydusctl`, `nydusd`, and `nydus-image`, plus library `nydus`. Workspace members include `api`, `builder`, `clib`, `rafs`, `storage`, `service`, `upgrade`, and `utils`. Default features enable FUSE backend support, several storage backends, and dedup. Optional features include `virtiofs`, `block-nbd`, `block-uffd`, backend-specific flags, and `dedup`.

## Control Flow
Cargo uses this manifest to resolve workspace crates and build selected targets. Target-specific dependencies enable the Dragonfly proxy backend for x86_64/aarch64. Release profile sets `panic = "abort"`; dev profile uses `opt-level = 1` and debug info.

## State and Persistence
Cargo generates build artifacts under `target/` and lockfile state elsewhere in the repository. This file itself stores dependency and feature policy.

## Dependencies and Integration Points
The manifest ties together external crates such as `fuse-backend-rs`, `hyper`, `tokio`, `rusqlite`, `openssl` vendored, rust-vmm crates, and internal Nydus crates. CI Makefile targets and workflows call Cargo through this manifest.

## Risks and Edge Cases
Feature coupling is significant: default builds include many backend features, while `virtiofs` pulls several optional rust-vmm crates. Vendored OpenSSL improves static build reproducibility but increases build time. Target-specific Dragonfly proxy support means behavior can differ on unsupported architectures.

## Test Signals
`make build`, `make release`, `make ut-nextest`, `make miri-ut-nextest`, CI smoke builds, and cargo-deny are the key validation paths.
