<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/blobfs/mod.rs -->
# sources/cloud-native/nydus/rafs/src/blobfs/mod.rs

## Purpose

This module implements setup for a virtio-fs blob passthrough filesystem that mirrors a host blob cache directory while using RAFS metadata/device logic to fetch blob ranges on demand.

## Important APIs, Types, and Functions

`BlobOndemandConfig` parses embedded JSON containing `ConfigV2`, bootstrap path, and blob cache directory. `Config` combines passthrough FS config with the on-demand config string. `BlobFs` holds `BlobfsState` and `PassthroughFs`. Important helpers include `BlobfsState::get_rafs_handle`, `BlobFs::new`, `import`, `ensure_path_exist`, `load_bootstrap`, `get_blob_id_and_size`, `stat`, and `open_file`.

## Control Flow

`BlobFs::new` parses and validates config, creates the passthrough FS, ensures cache dir exists, validates bootstrap file, and spawns a background thread to build/import a `Rafs` instance. `init` later joins that thread through `get_rafs_handle`. `get_blob_id_and_size` resolves a passthrough inode to a proc path, opens it with no-follow flags, stats it, and caches `(size, blob_id)` by inode.

## State and Persistence Behavior

The module creates cache directories and caches inode-to-blob mappings in memory. The RAFS handle transitions from a join handle to an initialized `Rafs` inside an `RwLock`. It reads bootstrap metadata but does not itself write blob data.

## Dependencies and Integration Points

It depends on `fuse_backend_rs` passthrough FS, `ConfigV2`, `BlobPrefetchRequest`, RAFS core, UNIX fd/path APIs, and serde JSON. `sync_io.rs` supplies the FUSE trait implementation and on-demand fetches.

## Risks and Test Signals

Initialization errors can be delayed until FUSE `init` joins the RAFS thread. Blob ID extraction trusts the file name from the passthrough path. Negative file sizes are rejected. Tests in the module actually cover generic RAFS IO writer/iterator behavior rather than blobfs construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/blobfs/mod.rs -->
