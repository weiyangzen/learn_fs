# sources/cloud-native/composefs-rs/crates/composefs-storage/Cargo.toml

## Purpose
This manifest defines the `composefs-storage` library crate, which provides read-only access to containers-storage overlay driver data and tar-split reconstruction support.

## Important APIs, Types, and Functions
The package metadata names storage, overlay, Podman, and Buildah keywords. Feature `userns-helper` enables optional `jsonrpc-fdpass`, `tokio`, and `tracing` support. Default features are empty. The manifest also enables workspace lints.

## Control Flow
Cargo builds the base storage library with capability-oriented filesystem access, OCI parsing, JSON/TOML parsing, compression, CRC, and tar-core support. Enabling `userns-helper` adds async networking/fd-passing dependencies for helper/proxy behavior without imposing them on default builds.

## State and Persistence
The manifest has no runtime state, but its dependency choices define the crate's access model: read-only overlay storage inspection, layer/image metadata parsing, tar-split gzip/zstd processing, and optional user namespace helper communication.

## Dependencies and Integration Points
Key dependencies are `cap-std` and `cap-std-ext`, `oci-spec`, `serde_json`, `toml`, `tar-core`, `flate2`, `zstd`, `crc`, `sha2`, `rustix`, `thiserror`, and optional `jsonrpc-fdpass`/`tokio`/`tracing`. This shows integration with containers-storage layouts, OCI metadata, compressed tar-split files, Linux permission/capability checks, and optional fd proxying.

## Risks
The crate defaults to no helper feature, so rootless storage access requiring helper/proxy support must opt in. Multiple parser/compression dependencies increase attack surface for untrusted storage metadata, making the fd-relative and read-only design important. Version differences in containers-storage layout can affect runtime behavior more than the manifest can express.

## Test Signals
The manifest supplies `tempfile` for filesystem-layout tests in `storage.rs` and `layer.rs`. Other module tests use only normal test dependencies and validate config parsing, manifest parsing, whiteout/opaque handling, and discovery parsing.
