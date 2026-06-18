# subset-b-000227 research

This grouped report covers the RAFS metadata v5/v6 layout, version loaders, shared metadata facade, noop placeholder, and local mock implementations under `sources/cloud-native/nydus/rafs/src`. Each section is wrapped with source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/layout/v5.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/layout/v5.rs

## Purpose
`v5.rs` defines the RAFS v5 on-disk metadata layout and the helper logic that turns v5 inode chunk records into storage-layer IO descriptors. RAFS v5 is designed for direct mapping of metadata so runtime code can parse inode, blob, xattr, and prefetch structures on demand instead of eagerly building a separate in-memory tree. The file also preserves v4/v5 compatibility assumptions around inode numbers, child indexes, hardlinks, and the inode offset table.

## Important APIs, Types, And Functions
The top-level traits are `RafsV5InodeOps` for blob lookup, chunk size, and hole awareness, and `RafsV5InodeChunkOps` for retrieving v5 chunk metadata. `RafsV5SuperBlock` is the 8192-byte superblock with magic/version, flags, inode table, blob table, extended blob table, and prefetch table fields. `RafsV5InodeTable` maps inode or child index to an 8-byte-aligned metadata offset. `RafsV5PrefetchTable` stores inode hints used during mount-time prefetch. `RafsV5BlobTable`, `RafsV5ExtBlobEntry`, and `RafsV5ExtBlobTable` load/store blob IDs, readahead information, chunk counts, sizes, and feature flags into `BlobInfo`.

`RafsV5Inode` is the fixed 128-byte inode header followed by aligned name and optional symlink data. `RafsV5InodeWrapper` writes that variable-sized record. `RafsV5ChunkInfo` is the v5 chunk record consumed through the `BlobV5ChunkInfo` trait. `RafsV5XAttrsTable` and `RafsXAttrs::store_v5` encode v5 xattr payloads. The IO helpers are `rafsv5_alloc_bio_vecs`, `add_chunk_to_bio_desc`, `calculate_bio_chunk_index`, `rafsv5_align`, and `rafsv5_validate_inode`.

## Control Flow
Readers first validate the superblock through `RafsV5SuperBlock::validate`, which checks magic, version, block size, flags, and that all declared metadata tables sit within the bootstrap and do not overlap. Runtime inode lookup uses the inode table to convert an inode or child index into a metadata offset. Blob table loading parses a compact stream of readahead offset, readahead size, and NUL-delimited blob IDs, optionally joining extended entries for chunk counts, compressed/uncompressed sizes, and feature flags. Inode loading reads the fixed record, then separately reads and aligns names and symlink targets.

For file reads, `rafsv5_alloc_bio_vecs` computes the chunk index span from the requested file range, loads each chunk, groups consecutive chunks by blob, and pushes `BlobIoDesc` entries into `BlobIoVec`s. Files with holes force scanning all chunks because chunk index cannot be derived directly from offset. `rafsv5_validate_inode` recursively hashes symlink targets, chunk digests, or child inode digests and compares the computed digest with the inode digest.

## State And Persistence
This file defines persistent v5 bootstrap bytes: superblock, inode offset table, prefetch hints, base and extended blob tables, inode records, chunk records, and xattr records. Endianness is encoded through explicit `to_le`/`from_le` conversions in table and superblock helpers, while `impl_bootstrap_converter!` exposes raw byte views for fixed-layout structs. Runtime state is mostly transient vectors of table entries and `Arc<BlobInfo>` or `Arc<dyn BlobChunkInfo>` objects derived from those bytes.

## Dependencies And Integration Points
The layout integrates with `nydus_storage::device` for `BlobInfo`, `BlobIoVec`, `BlobIoDesc`, `BlobChunkInfo`, `BlobChunkFlags`, and the v5 `BlobV5ChunkInfo` trait. It depends on `nydus_utils` digest/compression helpers, common metadata traits from `metadata/mod.rs`, inode flags from `metadata/inode`, and writer/reader abstractions from the crate. `md_v5.rs`, `cached_v5`, `direct_v5`, and tests consume these structures.

## Risks
The primary risks are unchecked assumptions around raw layout, alignment, and table bounds. A bad offset table entry can point outside metadata unless validation and table `get` checks stay strict. Blob table parsing is sensitive to malformed NUL delimiters and to extended table length mismatches. Unknown blob feature bits are truncated for compatibility, which preserves old images but can hide new semantics from older runtimes. `rafsv5_alloc_bio_vecs` depends on sorted chunk metadata and correct hole flags. Digest validation is recursive and can be expensive on large trees or misleading if callers disable validation.

## Test Signals
Unit tests cover blob table parsing, extended blob table load/store, IO overlap handling in `add_chunk_to_bio_desc`, chunk-index range calculation, v5 alignment, flag conversions, inode table validation, prefetch table load/store, inode wrapper load/store, xattr sizing, and unknown blob feature truncation. There is an explicit TODO for broader `RafsSuper::try_load_v5` and IO amplification tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/layout/v5.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/layout/v6.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/layout/v6.rs

## Purpose
`v6.rs` defines RAFS v6 metadata structures. RAFS v6 is intentionally compatible with the EROFS on-disk superblock and inode model so Linux EROFS tooling and kernel behavior can understand the metadata shape, while RAFS-specific data lives in an extended superblock, blob table, device table, and chunk metadata references.

## Important APIs, Types, And Functions
The file exports EROFS constants for block sizes, superblock offsets, inode layout values, and chunked-file flags. `RafsV6SuperBlock` is the 128-byte EROFS-compatible superblock loaded after a 1024-byte offset. `RafsV6SuperBlockExt` is the RAFS-specific 256-byte extension carrying RAFS flags, chunk size, blob table offset/size, chunk table offset/size, and prefetch table location.

`RafsV6OndiskInode` abstracts the EROFS compact and extended inode formats implemented by `RafsV6InodeCompact` and `RafsV6InodeExtended`. `new_v6_inode` creates either format from an `InodeWrapper`. `RafsV6Dirent` stores sorted directory entries. `RafsV6InodeChunkHeader` encodes EROFS chunk format and chunk size bits. `RafsV6InodeChunkAddr` encodes the blob device id, compression-info index, and block address for chunked files. `RafsV6Device` stores devslot entries. `RafsV6Blob` is the internal 256-byte blob-table record, while `RafsV6BlobTable` exposes public add/load/store/get behavior as `BlobInfo`. Xattr support is implemented through `RafsV6XattrIbodyHeader`, `RafsV6XattrEntry`, namespace prefix helpers, `recover_namespace`, and `RafsXAttrs::{count_v6, aligned_size_v6, store_v6}`. `RafsV6PrefetchTable` mirrors the v5 hint table without v5 padding.

## Control Flow
Loading starts with `RafsV6SuperBlock::load`, which skips `EROFS_SUPER_OFFSET` bytes and reads the EROFS superblock. `validate` enforces bootstrap size alignment, magic, checksum, supported block-size bits, inode count, unsupported shared xattrs, devtable placement, feature bits, and device table bounds. `RafsV6SuperBlockExt::load` seeks to the RAFS extension area, reads it, and then seeks to the first 4 KiB block. Its validation checks exactly one compression flag, exactly one digest flag, power-of-two chunk size, blob table alignment and range, optional chunk table range and non-overlap, and optional prefetch table range and non-overlap.

Blob table loading reads fixed-size `RafsV6Blob` records, validates each record against the expected index, chunk size, RAFS flags, feature combinations, compression-info size, and bounds, and converts the record to `BlobInfo`. Xattr storage maps Linux xattr namespace prefixes to EROFS numeric namespace IDs and writes aligned entries after an ibody header.

## State And Persistence
Persistent v6 state includes EROFS-compatible superblock bytes, RAFS extended superblock bytes, compact or extended inode records, dirents, chunk headers and chunk addresses, device table entries, blob table records, inline xattrs, and prefetch entries. The blob table persists chunk compression/digest/cipher algorithms, data/blob-meta sizes, compression-info offsets, TOC digests, blob meta digest, and encryption material representation. Runtime state is represented by `BlobInfo`, `RafsBlobExtraInfo`, `CipherContext`, and prefetch vectors.

## Dependencies And Integration Points
The file integrates with `nydus_storage::meta` chunk-info on-disk types and compression context headers, `nydus_storage::device::BlobInfo` and `BlobFeatures`, `nydus_utils` digest/compression/crypt helpers, `metadata/mod.rs` flags and super metadata, and `metadata/layout/v5::RafsV5ChunkInfo` for shared chunk-table sizing. `md_v6.rs` uses the superblock and prefetch table loaders; `direct_v6` consumes inode, chunk, blob, and xattr layout pieces.

## Risks
This file has a high compatibility burden because structures must remain EROFS-compatible and RAFS-compatible at once. Validation relies on exact feature bit expectations and block alignment; small changes can make existing images unmountable. `RafsV6Blob::validate` has many feature cross-checks for chunk-info v1/v2, batch, zran, encryption, chunk dictionaries, and tarfs mode. Blob IDs are expected to be UTF-8 SHA256-length strings. `RafsV6InodeChunkAddr` stores blob index as EROFS device id plus one, so off-by-one mistakes can address the bootstrap device or wrong blob. Compact inodes truncate uid/gid and size to 16/32-bit fields. Xattr prefix matching must stay consistent with EROFS namespace IDs.

## Test Signals
Tests cover superblock load/store, extended inode layout and persistence, chunk header bit encoding, chunk address encoding/validation, device slot load/store, v6 xattr count/size/store, invalid zero blob index handling, superblock setters and validation failures, extended superblock flag setters, compact and extended inode accessors, `new_v6_inode`, dirent file type mapping, alignment and nid helpers, blob conversion with cipher handling, blob table add/store, xattr entry accessors, and prefetch table load/store.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/layout/v6.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/md_v5.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/md_v5.rs

## Purpose
`md_v5.rs` wires the version-neutral `RafsSuper` facade to RAFS v5 metadata loading, v5 prefetch, v5 update skipping, IO amplification, and a v5-specific storage chunk adapter. It is the bridge between the raw v5 layout definitions and runtime metadata implementations in `direct_v5` and `cached_v5`.

## Important APIs, Types, And Functions
The main methods are `RafsSuper::try_load_v5`, `prefetch_data_v5`, `skip_v5_superblock`, `amplify_user_io`, and the private `merge_chunks_io`. `V5IoChunk` represents a chunk address passed to the storage layer and implements `BlobChunkInfo` by exposing digest, index, compression status, CRC32, offsets, sizes, and blob index.

## Control Flow
`try_load_v5` seeks to the end to get metadata size, seeks back to offset zero, reads a `RafsV5SuperBlock`, returns `Ok(false)` if the magic/version do not match v5, validates the superblock, copies all relevant fields into `self.meta`, and creates either `DirectSuperBlockV5` or `CachedSuperBlockV5` depending on `self.mode`. The selected implementation loads the remaining metadata and is stored as `self.superblock`.

`prefetch_data_v5` exits early when the v5 prefetch table has no entries. Otherwise it loads inode hints from the prefetch table offset, walks the hinted inode list until a zero padding entry, tracks whether the root inode was included, deduplicates hardlinks, appends file IO into a `BlobIoMerge`, and flushes remaining merged descriptors through the caller's fetch callback. `amplify_user_io` expands an existing user IO descriptor by reading adjacent file content and then nearby regular files with increasing inode numbers, merging only chunks from the same blob and within the configured maximum gap.

## State And Persistence
`try_load_v5` persists no new data; it materializes persistent v5 superblock fields into `RafsSuperMeta`. `prefetch_data_v5` consumes persistent prefetch-table hints but only produces transient `BlobIoVec` fetch requests. `amplify_user_io` is purely runtime behavior that opportunistically enlarges read-ahead based on inode order and chunk continuity. `V5IoChunk` is a runtime wrapper around persistent chunk metadata.

## Dependencies And Integration Points
The file depends on `RafsV5SuperBlock` and `RafsV5PrefetchTable` from `layout/v5.rs`, `DirectSuperBlockV5`, `CachedSuperBlockV5`, `BlobDevice`, `BlobIoVec`, `BlobIoMerge`, `BlobChunkFlags`, and the shared `RafsSuper` API from `metadata/mod.rs`. `V5IoChunk` adapts v5 RAFS chunk records to the storage crate's generic `BlobChunkInfo` interface.

## Risks
`try_load_v5` must leave the reader at the right place for direct/cached loaders and must not partially mutate state for non-v5 images. V5 cached mode is supported but v6 cached mode is not, so version detection order matters. Prefetch assumes the prefetch table is trustworthy after superblock validation and that zero terminates aligned padding. IO amplification has an explicit TODO for unit coverage and depends on inode-number locality, blob continuity, and gap thresholds; overly aggressive merging could over-read while overly conservative merging loses performance.

## Test Signals
Tests focus on `V5IoChunk`: basic field access, compressed flag behavior, CRC32 gating, `as_any` downcast, and combined flags. Comments identify missing unit tests for `try_load_v5`, `amplify_io`, and `amplify_user_io`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/md_v5.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/md_v6.rs -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/md_v6.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/mod.rs -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/noop.rs -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/noop.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/mock/mock_chunk.rs -->
# sources/cloud-native/nydus/rafs/src/mock/mock_chunk.rs

## Purpose
`mock_chunk.rs` defines a test-oriented chunk metadata object that implements both generic `BlobChunkInfo` and v5-specific `BlobV5ChunkInfo`. It lets RAFS metadata and IO-vector tests exercise chunk access without loading a real bootstrap or blob metadata.

## Important APIs, Types, And Functions
`MockChunkInfo` stores digest, blob index, chunk index, file offset, compressed and uncompressed offsets and sizes, flags, and CRC32. `MockChunkInfo::mock` constructs a chunk with caller-provided offsets and sizes while leaving other fields at defaults. The `BlobChunkInfo` implementation exposes digest, id, compression/encryption/batch status, CRC32 behavior, downcast support, blob index, compressed offsets/sizes, and uncompressed offsets/sizes. The `BlobV5ChunkInfo` implementation exposes v5 chunk index, file offset, flags, and a base trait view.

## Control Flow
Tests or mock inodes construct `MockChunkInfo` directly, optionally mutate private fields from the module's tests, and pass it through `MockInode` into `rafsv5_alloc_bio_vecs` or other code that expects trait objects. Calls are simple accessors; no IO or validation is performed.

## State And Persistence
All state is in-memory test data. No persistent metadata is read or written. CRC32 is only reported when the `HAS_CRC32` flag is set. Encryption and batch status always return false regardless of flags other than compression and CRC32.

## Dependencies And Integration Points
The mock depends on `nydus_utils::digest::RafsDigest`, `storage::device::{BlobChunkInfo, BlobChunkFlags}`, and `storage::device::v5::BlobV5ChunkInfo`. It is used by `mock_inode.rs` and tests that need v5 chunk behavior.

## Risks
The mock intentionally under-models production chunks: it never reports encryption or batch chunks, does not validate offsets, and defaults digest/blob/index fields unless tests set them. Tests relying on this mock should not be interpreted as coverage for encrypted, batch, zran, or malformed chunk metadata.

## Test Signals
The unit test builds a chunk, sets digest/blob/index/compression fields, checks base and v5 trait accessors, verifies downcasting, compressed and uncompressed end helpers, and confirms file offset propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/mock/mock_chunk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/mock/mock_inode.rs -->
# sources/cloud-native/nydus/rafs/src/mock/mock_inode.rs

## Purpose
`mock_inode.rs` provides an in-memory inode implementation for tests. It implements `RafsInode`, `RafsInodeExt`, and v5 inode helper traits so shared metadata code can be exercised without real v5/v6 direct or cached superblock implementations.

## Important APIs, Types, And Functions
`MockInode` stores inode number, name, digest, parent, mode, project/user/group IDs, RAFS inode flags, size, blocks, nlink, child index/count, block size, rdev, mtime, symlink target, xattrs, chunk vector, child inode vector, blob table, and metadata. `MockInode::mock` creates a regular file with a given inode number, size, and chunks. The `RafsInode` implementation covers validation, FUSE entry/attr construction, symlink access, directory child lookup by binary-search name or index, xattr access, file-type checks, hardlink detection, recursive descendant collection, IO vector allocation through `rafsv5_alloc_bio_vecs`, and basic accessors. `RafsInodeExt` adds name, flags, digest, name size, chunk info, base inode view, and parent. `RafsV5InodeChunkOps` and `RafsV5InodeOps` provide v5 chunk retrieval, default blob lookup, chunk size, and hole status.

## Control Flow
Tests build a `MockInode`, optionally configure it as a directory with sorted children and xattrs, and call the same trait methods used by production `RafsSuper` paths. `collect_descendants_inodes` recursively visits child directories after collecting non-empty non-directory children. `alloc_bio_vecs` delegates to the real v5 IO allocation helper, making this mock useful for exercising chunk range behavior.

## State And Persistence
All metadata is in-memory. `get_entry` uses the embedded `RafsSuperMeta` timeouts. `get_attr` returns a FUSE attr view from stored inode fields. Xattrs are a `HashMap<OsString, Vec<u8>>`; children and chunks are `Arc` vectors. No persistent metadata is read or written.

## Dependencies And Integration Points
The file depends on FUSE ABI types, `nydus_storage` blob and IO types, `MockChunkInfo`, `mock_super::CHUNK_SIZE`, v5 layout IO helpers and traits, shared metadata traits and constants, inode flags, and crate `RafsInodeExt`. It integrates with `MockSuperBlock` for lookup tests.

## Risks
Several behaviors are simplified. `walk_children_inodes` is `todo!`, `get_blob_by_index` returns a default `BlobInfo` rather than a configured table entry, `has_hole` is always false, child lookup assumes children are sorted by name, and many fields are left at defaults by `mock`. It is suitable for focused trait and IO tests, not complete filesystem semantic tests.

## Test Signals
The unit test configures a directory inode with children, xattrs, digest, parent, and chunks. It checks validation, attr and entry construction, symlink errors, child lookup, child and chunk counts, xattr retrieval, file-type predicates, hardlink status, descendant collection, v5 chunk lookup, blob lookup, chunk size, and hole status.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/mock/mock_inode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/mock/mock_super.rs -->
# sources/cloud-native/nydus/rafs/src/mock/mock_super.rs

## Purpose
`mock_super.rs` defines a minimal in-memory `RafsSuperBlock` implementation for tests. It provides inode lookup through a hash map while leaving operations unrelated to lookup intentionally unimplemented.

## Important APIs, Types, And Functions
`MockSuperBlock` stores `HashMap<Inode, Arc<MockInode>>`. `CHUNK_SIZE` is a test constant used by `MockInode` and v5 IO allocation tests. `MockSuperBlock::new` constructs an empty map. The `RafsSuperInodes` implementation supports `get_inode` and `get_extended_inode` by map lookup and `enoent!` on misses; `get_max_ino` is unimplemented. The `RafsSuperBlock` implementation leaves `load`, `update`, `get_blob_infos`, `root_ino`, `get_chunk_info`, and `set_blob_device` unimplemented while making `destroy` a no-op.

## Control Flow
Tests insert `Arc<MockInode>` values into the map, then exercise lookup through both base and extended inode trait paths. Missing keys return `enoent!`. Any test that calls unimplemented superblock-level operations should panic.

## State And Persistence
State is limited to the in-memory inode map. There is no metadata loading, metadata update, blob table, root inode state, or persistent storage effect. `destroy` does not clear the map.

## Dependencies And Integration Points
The mock depends on `MockInode`, shared metadata traits, RAFS reader/result aliases, and storage blob types required by the trait signatures. It supports tests that need a `RafsSuperBlock` trait object but only care about inode lookup.

## Risks
This mock is deliberately partial. It cannot model max inode, root inode, blob enumeration, update/load, v6 chunk table access, or blob-device injection. Tests using it should not assume production superblock lifecycle or blob behavior is covered. The `CHUNK_SIZE` value is arbitrary and only meaningful in the mock/test context.

## Test Signals
Tests cover successful and failed inode lookups for base and extended traits, expected panics for unimplemented methods, and that `destroy` is callable. Helper code constructs a temporary reader only to invoke panic paths for `load` and `update`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/mock/mock_super.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/mock/mod.rs -->
# sources/cloud-native/nydus/rafs/src/mock/mod.rs

## Purpose
`mock/mod.rs` is the module index and re-export surface for RAFS test mocks.

## Important APIs, Types, And Functions
It declares `pub mod mock_chunk`, `pub mod mock_inode`, and `pub mod mock_super`, then publicly re-exports all items from those modules with `pub use mock_chunk::*`, `pub use mock_inode::*`, and `pub use mock_super::*`.

## Control Flow
There is no runtime control flow. The file controls compile-time module wiring and import ergonomics for tests and other internal code that use `crate::mock::*`.

## State And Persistence
No state is stored and no persistent data is read or written.

## Dependencies And Integration Points
This module integrates the three mock implementations into a single namespace. `mock_inode.rs` references `super::mock_chunk::MockChunkInfo` and `super::mock_super::CHUNK_SIZE`; external tests can import `MockChunkInfo`, `MockInode`, `MockSuperBlock`, and `CHUNK_SIZE` through `crate::mock`.

## Risks
The main risk is namespace churn: changing re-exports or module names can break tests that depend on broad `crate::mock::*` imports. Because the mocks are partial implementations, this convenient export surface can also make it easy to use them in tests that need stronger production fidelity.

## Test Signals
There are no direct tests for this module. Successful compilation and the unit tests in `mock_chunk.rs`, `mock_inode.rs`, and `mock_super.rs` validate the module wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/mock/mod.rs -->
