# sources/cloud-native/composefs-rs/crates/composefs-storage/src/error.rs

## Purpose
This module defines the storage crate's error model and result alias. It centralizes user-facing failure categories for storage discovery, image/layer lookup, link resolution, tar-split processing, IO, and JSON parsing.

## Important APIs, Types, and Functions
`pub type Result<T> = std::result::Result<T, StorageError>` is the crate result alias. `StorageError` derives `thiserror::Error` and includes `RootNotFound(PathBuf)`, `InvalidStorage(String)`, `LayerNotFound(String)`, `ImageNotFound(String)`, `LinkReadError(String)`, `TarSplitError(String)`, `Io(std::io::Error)`, and `JsonParse(serde_json::Error)`.

## Control Flow
The enum is consumed throughout the storage crate via `?`, manual mapping, and `From` conversions for IO and JSON. More specific variants are used when lookup or validation semantics matter, while lower-level failures are wrapped in `Io`, `InvalidStorage`, or `LinkReadError`.

## State and Persistence
The module has no persistence. It preserves contextual data in variant payloads, such as missing root paths, missing layer/image IDs, and invalid storage messages.

## Dependencies and Integration Points
It depends on `thiserror`, `PathBuf`, `std::io`, and `serde_json`. It is re-exported from `lib.rs` and used by `config`, `image`, `layer`, `storage`, and tar-split/userns modules.

## Risks
Many call sites wrap structured IO failures into string-bearing `InvalidStorage` or `LinkReadError`, which is readable but less machine-actionable. `JsonParse` has a `From` impl, but some JSON parse sites deliberately map to `InvalidStorage` to add file context, so consumers should not rely on every JSON failure using the same variant.

## Test Signals
There are no direct tests for this file. It is exercised indirectly by storage validation tests, image/layer lookup tests, JSON parsing paths, and tar-split error propagation.
