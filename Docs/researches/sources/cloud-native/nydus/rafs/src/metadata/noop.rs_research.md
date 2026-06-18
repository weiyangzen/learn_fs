# sources/cloud-native/nydus/rafs/src/metadata/noop.rs

## Purpose
`noop.rs` provides a placeholder metadata driver used as the default `RafsSuper.superblock` before real v5 or v6 metadata is loaded. It satisfies the `RafsSuperBlock` and `RafsSuperInodes` trait requirements without implementing operational metadata access.

## Important APIs, Types, And Functions
`NoopSuperBlock` is an empty default struct with `new`. Its `RafsSuperInodes` implementation defines `get_max_ino`, `get_inode`, and `get_extended_inode` as `unimplemented!`. Its `RafsSuperBlock` implementation leaves `load`, `update`, `root_ino`, `get_chunk_info`, and `set_blob_device` unimplemented, implements `destroy` as a no-op, and returns an empty vector from `get_blob_infos`.

## Control Flow
There is no normal runtime control flow beyond construction and replacement. `RafsSuper::default` installs `Arc::new(NoopSuperBlock::new())`. Later `try_load_v5` or `try_load_v6` replaces it with a real direct or cached superblock implementation. If code accidentally calls operational methods before successful metadata loading, the method panics immediately.

## State And Persistence
The struct holds no state and writes no persistent data. The only observable non-panic behavior is that `destroy` succeeds and `get_blob_infos` reports no blobs.

## Dependencies And Integration Points
The file depends on the shared metadata traits, inode traits, `BlobInfo`, `BlobChunkInfo`, `BlobDevice`, and RAFS reader/result aliases. It is tightly integrated with `RafsSuper::default` in `metadata/mod.rs` as the initial trait-object value.

## Risks
This is intentionally unsafe as a real driver: most methods panic. That is acceptable for a sentinel, but any path that exposes a default `RafsSuper` without loading metadata can crash. The empty `get_blob_infos` behavior is useful for cleanup but can also hide missing load failures if callers ignore earlier errors and only inspect blob lists.

## Test Signals
Tests assert that unimplemented methods panic for inode lookup, max inode, root inode, v6 chunk lookup, and blob-device injection. A non-panic test checks that a new noop superblock has no blob infos and that `destroy` is harmless.
