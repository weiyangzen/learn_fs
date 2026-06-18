<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/fs.rs -->
# sources/cloud-native/nydus/rafs/src/fs.rs

## Purpose

This is the core RAFS filesystem implementation that glues FUSE requests, RAFS metadata, blob storage devices, cache/prefetch policy, metrics, and access checks together.

## Important APIs, Types, and Functions

`Rafs` stores instance id, `BlobDevice`, IO stats, `RafsSuper`, initialization flags, validation/prefetch/xattr settings, optional streaming `BlobPrefetcher`, and runtime UID/GID/time defaults. Key methods include `new`, `update`, `import`, `destroy`, `id`, `metadata`, `fetch_range_synchronous`, `get_root_inode`, `do_prefetch`, `convert_file_list`, `get_inode_attr`, and `get_inode_entry`. It implements `BackendFileSystem`, `FileSystem`, and Linux `Layer`.

## Control Flow

`new` validates config, loads metadata, creates a blob device, enforces RAFS v6 cache/validation constraints, and configures metrics. `import` starts stream prefetch, normal device prefetch, or no prefetch, then marks initialized. `destroy` stops prefetchers, destroys superblock, stops device prefetch, and closes the device. FUSE lookup/getattr/read/readdir/xattr/access calls read metadata, allocate blob IO vectors, fetch data, and record metrics.

## State and Persistence Behavior

The struct owns runtime initialization state and references blob cache/device state. Prefetch can populate local cache asynchronously or via streaming Dragonfly proxy optimization. `update` swaps metadata/device backend after initialization. RAFS itself is read-only through FUSE operations.

## Dependencies and Integration Points

It integrates with `fuse_backend_rs`, `nydus_storage::BlobDevice`, RAFS metadata traits, Nydus config v2, metrics, prefetcher, Linux overlay `Layer`, and Nydus error macros. It is the central runtime object mounted by nydusd.

## Risks and Test Signals

Read amplification and prefetch policies are performance-critical and differ between RAFS v5 and v6. `Arc::get_mut` in `destroy` assumes no extra superblock references. Access checks reimplement POSIX-like logic and need care for root/execute behavior. Tests cover simple constructor-like state, ID, xattr support, forget no-ops, negative entries, file-list conversion, plus commented historical integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/fs.rs -->
