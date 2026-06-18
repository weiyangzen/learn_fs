<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/Cargo.toml -->
# sources/cloud-native/nydus/rafs/Cargo.toml

## Purpose

This manifest defines the `nydus-rafs` Rust crate, which implements the RAFS filesystem format and FUSE integration for Nydus Image Service.

## Important APIs, Types, and Functions

Package metadata declares version `0.4.1`, edition 2021, Apache-2.0 OR BSD-3-Clause license, and repository/homepage. Dependencies include config/error/logging/concurrency crates, `fuse-backend-rs`, `vm-memory`, `nydus-api`, `nydus-storage` with localfs backend feature, and `nydus-utils`. Features enable `fusedev`, `virtio-fs`, and `vhost-user-fs`.

## Control Flow

Cargo uses this manifest to compile the crate with feature-gated modules, especially `blobfs` under `virtio-fs`.

## State and Persistence Behavior

The manifest does not persist runtime state, but feature/dependency choices determine which filesystem backends and transports are compiled.

## Dependencies and Integration Points

It integrates with workspace dependencies and sibling Nydus crates. `nydus-storage` supplies blob devices/cache, `nydus-api` supplies config and error macros, and `fuse-backend-rs` supplies FUSE traits.

## Risks and Test Signals

Feature combinations affect public API availability. Dependency versions are part of the security/license surface governed by `deny.toml`. Tests are defined inside source modules rather than manifest targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/Cargo.toml -->
