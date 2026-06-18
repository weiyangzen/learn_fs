# sources/cloud-native/nydus/rafs/src/metadata/mod.rs

## Purpose
`mod.rs` is the central RAFS metadata facade. It declares shared traits, common types, flags, version/mode handling, superblock metadata cache, path and directory traversal helpers, prefetch orchestration, and file-loading behavior that is independent of RAFS v5 or v6 implementation details.

## Important APIs, Types, And Functions
Core traits are `RafsSuperInodes`, `RafsSuperBlock`, `RafsInode`, `RafsInodeExt`, and `RafsStore`. `RafsSuperBlock` abstracts version-specific metadata implementations, including inode lookup, update, destroy, blob enumeration, root inode, v6 chunk lookup, and blob-device injection. `RafsInode` exposes validation, IO vector allocation, FUSE `Entry` and `Attr` conversion, file type checks, xattrs, symlink access, directory child traversal, size, chunk count, and `Any` downcasting. `RafsInodeExt` adds builder and directory-walker fields such as parent, name, flags, digest, and chunk info.

Shared structs/enums include `RafsBlobExtraInfo`, `RafsInodeWalkAction`, `RafsSuperFlags`, `RafsSuperConfig`, `MergeError`, `RafsSuperMeta`, `RafsVersion`, `RafsMode`, and `RafsSuper`. Important methods include `RafsSuper::new`, `load_from_file`, `load`, `set_blob_id_from_meta_path`, `create_blob_device`, `update`, inode lookup wrappers, `ino_from_path`, `prefetch_files`, `prefetch_inode`, `prefetch_data`, `path_from_ino`, `get_prefetched_inos`, and `walk_directory`.

## Control Flow
`load_from_file` opens a bootstrap path, constructs a `RafsSuper`, and calls `load`. If loading fails, it tries to extract inlined RAFS metadata from a blob TOC and reload from the extracted metadata. On success it fixes blob IDs for inlined-meta compatibility and may create a `BlobDevice` when digest or chunk validation needs inlined chunk digests. `load` tries v5 first, then v6, and errors if neither loader recognizes the file.

Path lookup starts at the root inode and resolves normalized path components through `get_child_by_name`. Prefetch first honors dynamic inode lists, otherwise dispatches to v5 or v6 static prefetch tables. Shared `prefetch_data` recursively expands directories, skips empty regular files, deduplicates hardlinks, allocates IO vectors, appends them to `BlobIoMerge`, and calls the fetcher for ready descriptors. Directory walking is DFS over `get_child_by_index`.

## State And Persistence
`RafsSuperMeta` caches persistent superblock values such as version, magic, chunk size, flags, table offsets and sizes, inode count, v6 root nid, chunk table, timeouts, and chunk-dictionary state. `RafsSuper` owns runtime mode, validation flag, metadata cache, and an `Arc<dyn RafsSuperBlock>`. Persistent writes are not performed here, except through trait objects' update/store implementations elsewhere. `load_from_file` may create/extract an alternate metadata file through `TocEntryList::extract_rafs_meta`.

## Dependencies And Integration Points
The module ties together `md_v5`, `md_v6`, `noop`, `cached_v5`, `direct_v5`, `direct_v6`, `inode`, and `layout`. It integrates with FUSE ABI types, `nydus_api` config, `nydus_storage` blob devices, TOC extraction, digest/compress/crypt utilities, and crate-level `RafsError`/reader/writer types. Image-building code uses `RafsStore`, `RafsInodeExt`, `path_from_ino`, and `walk_directory`; runtime nydusd uses loading, lookup, prefetch, and blob-device creation.

## Risks
The facade hides sharp version differences: v5 supports cached and direct modes, while v6 supports direct only. Default conversions from flag sets choose Blake3/LZ4 when no flag matches, so validation paths must ensure flags are sane before conversion. `destroy` requires exclusive ownership of the superblock `Arc` and will panic if inodes are still referenced. Path resolution accepts `.` and `..` components as names and relies on underlying metadata semantics. Dynamic and static prefetch can issue large IO if directory trees are broad. Compatibility checks intentionally reject v5 digest mismatches and tarfs/uidgid/chunk-size differences.

## Test Signals
Tests cover `RafsMode` parsing/display, compressor/digester/cipher conversions, `RafsSuperMeta` helpers and config creation, `RafsSuper::new` plus destroy on the default noop superblock, and multiple `RafsSuperConfig::check_compatibility` failure modes.
