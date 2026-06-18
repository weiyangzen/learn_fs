# sources/cloud-native/nydus/storage/src/backend/localdisk.rs

## Purpose
This module implements a local block-device or disk-image backend. It maps blob IDs to byte ranges on a device file, optionally discovering those ranges from GPT partitions.

## Important APIs, Types, and Functions
`LocalDisk` is the backend and `LocalDiskBlob` is the reader. `LocalDisk::new` canonicalizes and opens the configured device path, captures capacity, creates metrics, and optionally scans GPT. `add_blob` manually registers a blob offset and length when not in GPT mode. `get_blob` resolves a blob from the in-memory map or GPT fallback. Under `backend-localdisk-gpt`, `scan_blobs_by_gpt` reads partitions and derives blob IDs from partition names and GUIDs, while `truncate_blob_id` supports legacy 32-byte GPT names.

## Control Flow
Reads use `nix::sys::uio::pread` against cloned file descriptors. `try_read` returns `0` when the requested offset is at or beyond blob length and clamps reads to the remaining blob length. `readv` builds iovecs from FUSE volatile slices and calls a utility `readv` at the absolute device offset. `expect_exact_read` returns `false`, allowing EOF short reads without remote-style retry errors.

## State and Persistence Behavior
Persistent data is the underlying disk image or block device. Runtime state is an `RwLock<HashMap<String, Arc<LocalDiskBlob>>>`, the open device file, capacity, GPT mode flag, and metrics. Manual `add_blob` state is in-memory only and must be reconstructed by higher layers on restart unless GPT discovery is used.

## Dependencies and Integration Points
The backend consumes `nydus_api::LocalDiskConfig`, FUSE `FileVolatileSlice`, `nix` pread/uio, optional `gpt`, and common backend traits. It shares metrics across all blob readers.

## Risks
`readv` validates against the sum of all input slice lengths rather than the `max_size` actually consumed, so callers with larger buffers and smaller `max_size` can be rejected near EOF. GPT mode disallows `add_blob`, making configuration mode important. Lock poisoning is unhandled via `unwrap`. GPT blob ID derivation depends on partition naming conventions and legacy truncation, which can collide in pathological cases.

## Test Signals
Tests cover invalid construction, manual blob registration bounds, duplicate detection, EOF short reads, and GPT blob ID truncation when the feature is enabled.
