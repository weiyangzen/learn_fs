# sources/cloud-native/nydus/rafs/src/metadata/md_v6.rs

## Purpose
`md_v6.rs` connects the common `RafsSuper` facade to RAFS v6 loading and prefetch behavior. It performs version detection through the EROFS-compatible v6 superblock, loads the RAFS v6 extended superblock, fills shared metadata fields, and instantiates the v6 direct superblock implementation.

## Important APIs, Types, And Functions
The important methods are `RafsSuper::try_load_v6`, `is_inlay_prefetch_all`, and `prefetch_data_v6`. `try_load_v6` uses `RafsV6SuperBlock`, `RafsV6SuperBlockExt`, `DirectSuperBlockV6`, `RafsMode`, and `RafsSuperFlags`. Prefetch helpers use `RafsV6PrefetchTable` and, for the cross-version inlay check, also `RafsV5PrefetchTable`.

## Control Flow
`try_load_v6` seeks to determine bootstrap size, resets to offset zero, attempts to load the v6 superblock, returns `Ok(false)` when load or magic detection does not identify v6, validates the base superblock, then copies v6-specific fields into `self.meta`: version, magic, metadata block address, root nid, device table count and offset. It then loads and validates the extended superblock, copying chunk size, blob table location, chunk table location, inode count, RAFS flags, and prefetch location. Direct mode constructs and loads `DirectSuperBlockV6`; cached mode returns `enosys!`.

`is_inlay_prefetch_all` recognizes a special one-entry prefetch table meaning the root inode should be prefetched. It supports both v6 and v5 metadata by choosing the matching table loader. `prefetch_data_v6` mirrors v5 prefetch: load the hinted inode table, stop at zero padding, detect whether the root inode appears, recursively call shared `prefetch_data`, merge IO through `BlobIoMerge`, and flush the final descriptors.

## State And Persistence
The method copies persistent base and extended superblock values into `RafsSuperMeta`. It does not write metadata. Prefetch state is transient and consists of loaded inode hints, a hardlink deduplication set, and merged IO descriptors. V6 does not support cached mode through this file; all runtime metadata is owned by `DirectSuperBlockV6`.

## Dependencies And Integration Points
This file depends on `layout/v6.rs` for v6 superblocks and prefetch tables, `layout/v5.rs` for compatibility prefetch reads, `direct_v6` for the loaded superblock implementation, and common metadata/storage types from `metadata/mod.rs` and `nydus_storage`. It is invoked by `RafsSuper::load` after v5 detection fails.

## Risks
Version probing treats a failed v6 superblock load as `Ok(false)`, so callers must preserve the later generic invalid-superblock error. Cached mode rejection is intentional and must remain visible to configurations that request it. Prefetch table offsets come from validated metadata, but table loading can still fail and is mapped into `RafsError::Prefetch`. The one-entry inlay-prefetch-all optimization depends on root inode equality and can mislead callers if builders encode unexpected entries.

## Test Signals
Unit tests cover too-small bootstraps returning non-v6, invalid magic returning non-v6, and invalid v6 superblocks returning errors. A fuller `test_try_load_v6` against fixture bootstrap data is present but commented out.
