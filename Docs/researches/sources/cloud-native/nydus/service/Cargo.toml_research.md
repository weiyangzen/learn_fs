# sources/cloud-native/nydus/service/Cargo.toml

## Purpose
`service/Cargo.toml` defines the `nydus-service` crate, version `0.4.0`, for the Nydus image service manager. It declares core service dependencies and feature gates for FUSE, virtiofs, block device export, NBD, userfaultfd, and confidential-computing related backend registration.

## Important APIs, Types, And Functions
The manifest exports feature names rather than Rust APIs. `default = ["fuse-backend-rs/fusedev"]` enables normal FUSE device support. `virtiofs` enables vhost-user and VM-memory dependencies. `block-device` enables `dbs-allocator` and `tokio/fs`. `block-nbd` extends `block-device` with `bytes`. `block-uffd` extends `block-device`. `coco` enables FUSE device support and `nydus-storage/backend-registry`.

## Control Flow
Build-time control flow is feature-based. `blob_cache.rs`, `block_device.rs`, `block_nbd.rs`, and `block_uffd.rs` rely on optional dependencies listed here. Linux-specific dependency sections add `tokio-uring` for runtime async file/socket I/O and `procfs` for Linux tests.

## State, Persistence, And Dependencies
The crate depends on internal workspace/path crates (`nydus-api`, `nydus-rafs`, `nydus-storage`, `nydus-upgrade`, `nydus-utils`) and external crates for serialization, logging, async channels, finite-state-machine behavior, fd passing, ioctl/syscall interaction, and versioned persistence. There is no runtime state in the manifest, but feature selection changes compiled code and available daemon modes.

## Integration Points
This manifest is the integration point between service modules and workspace dependency resolution. `block_nbd.rs` needs `bytes`; `block_device.rs` needs `dbs-allocator`; UFFD/NBD paths need Linux-only `tokio-uring`; daemon state code uses `rust-fsm`; live-upgrade or persistence code can use `versionize`.

## Risks
Feature coupling is important: enabling `block-nbd` or `block-uffd` without Linux support would fail because the implementation depends on Linux APIs. `block-uffd` currently adds no extra optional dependency beyond `block-device`, relying on always-on `flume`, `sendfd`, `mio`, and `tokio`. Dependency versions are partly pinned and partly workspace-inherited, so compatibility is controlled across the root workspace.

## Test Signals
Manifest validation comes from cargo feature builds, for example `cargo check -p nydus-service --features block-nbd` and `--features block-uffd`. The service modules include unit tests gated by normal Rust test compilation and Linux-only dependencies.
