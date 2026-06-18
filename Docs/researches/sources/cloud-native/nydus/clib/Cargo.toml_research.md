# sources/cloud-native/nydus/clib/Cargo.toml

## Purpose
This manifest defines `nydus-clib`, the C wrapper library around selected Nydus SDK functionality. It builds both dynamic and static C-compatible Rust libraries so C programs can open RAFS filesystems and file handles through the FFI exported in `clib/src`.

## Important APIs, Types, and Functions
The important package-level settings are `crate-type = ["cdylib", "staticlib"]`, package metadata, and feature flags for storage backends. The crate name exposed to Cargo is `nydus-clib`, while the library artifact name is `nydus_clib`.

## Control Flow
Cargo uses this file to resolve dependencies and enabled backend features. The feature section maps crate features to `nydus-storage` backend features for S3, OSS, registry, HTTP proxy, and local disk. There is a typo-like feature name `baekend-s3`, which appears to be intended as `backend-s3`.

## State, Persistence, and Dependencies
The manifest depends on `libc`, `log`, `fuse-backend-rs`, `nydus-api`, `nydus-rafs`, and `nydus-storage`, with most Nydus crates resolved from sibling paths. Persistent build output is produced by Cargo as C ABI libraries.

## Integration Points
This crate bridges Rust Nydus RAFS/storage code to generated C headers under `clib/include/nydus.h`. Downstream users link the produced static or dynamic library and include the generated header.

## Risks and Test Signals
The backend feature typo can surprise users expecting `backend-s3`. Because this is a cdylib/staticlib FFI crate, ABI stability depends on the exported symbols in Rust and the generated header matching. Tests live in Rust source files rather than this manifest.
