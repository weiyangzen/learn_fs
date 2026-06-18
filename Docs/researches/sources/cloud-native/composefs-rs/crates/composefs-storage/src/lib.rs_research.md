# sources/cloud-native/composefs-rs/crates/composefs-storage/src/lib.rs

## Purpose
This is the public facade for the `composefs-storage` crate. It documents the read-only, capability-based approach to containers-storage overlay access and re-exports the crate's primary modules and types.

## Important APIs, Types, and Functions
Modules exported are `config`, `error`, `image`, `layer`, `storage`, `tar_split`, and `userns`, plus feature-gated `userns_helper`. Re-exports include `AdditionalLayerStore`, `StorageConfig`, `Result`, `StorageError`, `Image`, `Layer`, `LayerMetadata`, `Storage`, `TarHeader`, `TarSplitFdStream`, `TarSplitItem`, `can_bypass_file_permissions`, optional helper/proxy types, and OCI `Descriptor`, `ImageConfiguration`, and `ImageManifest`.

## Control Flow
There is no runtime control flow beyond module loading and feature-gated exports. The file enforces clippy denials for stdout/stderr in non-test library code, which guides diagnostics toward returned errors or logging rather than direct printing.

## State and Persistence
This facade stores no state. It defines the crate boundary through which callers access persistent containers-storage data via `Storage`, `Image`, `Layer`, and tar-split stream types.

## Dependencies and Integration Points
The crate facade integrates internal modules with external consumers and re-exports OCI spec types to reduce dependency friction. Optional `userns-helper` exports expose fd-passing proxy support only when the feature is enabled.

## Risks
The public API exposes low-level storage concepts directly, so semver changes in module types can affect consumers. The module docs mention SQLite database access, but the current researched files use JSON metadata and directory layouts rather than SQLite, so documentation may be partially stale. Feature-gated exports require consumers to compile with matching features before helper types are available.

## Test Signals
No direct tests exist in this facade. Its test signal is successful compilation of downstream module tests and doctest-like examples that use `Storage::discover()` and common re-exports.
