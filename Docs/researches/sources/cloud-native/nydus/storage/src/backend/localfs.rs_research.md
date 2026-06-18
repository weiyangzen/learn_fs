# sources/cloud-native/nydus/storage/src/backend/localfs.rs

## Purpose
This module implements a local filesystem blob backend. It opens blob files from either a fixed `blob_file`, a primary directory, or alternative directories.

## Important APIs, Types, and Functions
`LocalFs` is the backend and `LocalFsEntry` is the reader. `LocalFs::new` validates that either `blob_file` or `dir` is configured and requires an ID for metrics. `get_blob_path` resolves a blob path, preferring `blob_file`, then primary `dir`, then `alt_dirs`. `get_blob` caches open file readers by blob ID. `LocalFsEntry` implements `blob_size`, `try_read`, `readv`, and opts out of exact-read enforcement.

## Control Flow
When a reader is requested, the backend first checks the entries map. On a miss it resolves and canonicalizes the path, opens the file read-only, then inserts an `Arc<LocalFsEntry>` under a write lock with a second check to avoid duplicate opens. Reads use `pread` and vector reads use the shared `readv` utility.

## State and Persistence Behavior
Persistent state is the local filesystem file content. Runtime state includes configured path strings, alternate directories, metrics, and an `RwLock` cache of open files. Once a blob is cached, later changes to path resolution will not affect that blob ID until the backend is recreated.

## Dependencies and Integration Points
The backend integrates `nydus_api::LocalFsConfig`, Unix file descriptors, FUSE volatile slices, and the common backend traits. It is a local backend and therefore relies on short-read semantics rather than retrying for exact buffer length.

## Risks
The `is_valid` closure is written as though it receives a directory, but some calls pass a full blob path; this can produce surprising primary-directory checks, especially when `alt_dirs` are present. Zero-byte files are treated as invalid during directory search, which is intentional in tests but may surprise deployments that use valid empty blobs. Lock poisoning is unhandled. Cached file descriptors can keep reading old content after files are replaced on disk.

## Test Signals
Tests cover invalid config, blob path resolution, skipping zero-byte alt-dir candidates, fixed `blob_file` priority, missing paths, reader caching, scalar and vector reads, empty reads, and EOF behavior.
