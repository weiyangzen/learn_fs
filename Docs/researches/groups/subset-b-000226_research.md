# subset-b-000226 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/cached_v5.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/cached_v5.rs

## Purpose
`cached_v5.rs` implements the fully cached RAFS v5 metadata backend. It loads the v5 bootstrap inode table, blob tables, names, symlinks, xattrs, and chunk arrays into owned Rust structures during mount/load time, then serves the common `RafsSuperBlock`, `RafsSuperInodes`, `RafsInode`, `RafsInodeExt`, and v5 chunk traits from memory. The file is read-only at runtime; `update()` is unsupported and `destroy()` drops the in-memory inode map.

## Important APIs, Types, and Functions
- `CachedSuperBlockV5` owns `RafsSuperMeta`, a `RafsV5BlobTable`, a `BTreeMap<Inode, Arc<CachedInodeV5>>`, a max inode cursor, and the inode-digest validation flag.
- `CachedSuperBlockV5::load()` seeks through the bootstrap, loads blob and extended-blob tables, computes the first inode offset from the inode table entry, calls `load_all_inodes()`, and optionally validates the root digest tree with `rafsv5_validate_inode()`.
- `load_all_inodes()` relies on the v5 BFS layout: it loads inodes in table order, hashes them by inode number, immediately links non-directory children, delays directory parent insertion, then links directories in reverse order to preserve child readiness.
- `hash_inode()` maintains `max_inode` and contains hardlink-specific replacement behavior: a hardlink may not replace an existing inode that already carries chunk data because directory digest calculation depends on that data.
- `CachedInodeV5` stores copied inode scalar fields, name, symlink target, xattr map, chunk list, sorted child list, blob table reference, and super metadata reference.
- `CachedInodeV5::load()` parses the on-disk sequence `RafsV5Inode | name | symlink | xattrs | chunks`, aligns variable-length fields to `RAFSV5_ALIGNMENT`, copies scalar fields, loads chunk/xattr state, records chunk size, and validates the result.
- `CachedChunkInfoV5` is the owned in-memory chunk representation and implements both `BlobChunkInfo` and `BlobV5ChunkInfo`.

## Control Flow
Mount/load flow starts in `CachedSuperBlockV5::load()`: read the inode table offset, load extended blob table if present, load the main blob table, seek to the first inode body, and call `load_all_inodes()`. Each `CachedInodeV5::load()` reads the fixed inode, then conditionally reads name bytes, symlink bytes, xattr table/data, and regular-file chunk records. Parent-child reconstruction happens after hashing: files are inserted into their parents immediately, directories are linked after all inodes are seen. Lookup flow is then purely in-memory: superblock inode lookups index the `BTreeMap`; directory lookups binary-search the sorted `i_child`; readdir synthesizes `"."` and `".."` before iterating children.

## State and Persistence Behavior
All metadata state is copied out of the bootstrap into owned memory. Persistence is one-way: this backend reads from `RafsIoReader`, but does not write back and does not support runtime update. The state layout is stable under `Arc` sharing; mutability is intentionally limited to load-time when `Arc::get_mut()` is still valid. Xattrs are cached in a `HashMap<OsString, Vec<u8>>`; chunk metadata is cached in `Vec<Arc<CachedChunkInfoV5>>`; children are cached as `Vec<Arc<CachedInodeV5>>` sorted once the expected child count is reached.

## Dependencies and Integration Points
This file integrates tightly with `metadata/layout/v5` for on-disk structures, alignment, chunk IO allocation, blob tables, and digest validation. It uses `metadata/layout/mod.rs` helpers for byte-to-`OsStr` conversion and xattr parsing. It implements the central RAFS metadata traits consumed by the filesystem layer and storage IO layer: `RafsSuperBlock`, `RafsSuperInodes`, `RafsInode`, `RafsInodeExt`, `RafsV5InodeOps`, `RafsV5InodeChunkOps`, `BlobChunkInfo`, and `BlobV5ChunkInfo`. Blob IO allocation delegates to `rafsv5_alloc_bio_vecs()`, which consumes the v5 inode/chunk trait surface.

## Risks and Edge Cases
- `Arc::get_mut(parent_inode).unwrap()` in `add_into_parent()` assumes no external clones during load. The delayed directory-linking strategy is designed to uphold this, but future load-time sharing would make it panic.
- `CachedInodeV5::get_chunk_count()` returns `get_child_count()`, reflecting v5's overloaded child count field. Tests note this can diverge from `i_data.len()` in manually constructed inodes.
- Name validation requires non-empty names, including root, so callers must ensure bootstrap root naming matches this invariant.
- The hardlink replacement rule is subtle and digest-sensitive; changing it can alter directory digest validation or data ownership for hardlinked regular files.
- `CachedChunkInfoV5::copy_from_ondisk()` copies `flags` and offsets but the cached `crc32` field is not assigned there in the current code, so CRC-bearing on-disk chunks risk reporting zero unless populated through another path.
- Because the backend eagerly loads all metadata, very large bootstraps trade faster lookup for higher memory use.

## Test Signals
The file has broad unit coverage. Tests construct temporary v5 bootstrap fragments for inode, symlink, xattr, chunk, and bio-vector allocation behavior; cover superblock load/destroy/getters; validate inode error cases for zero inode, bad parent, empty name, invalid chunk/block counts, invalid directory child indexes, and empty symlink targets; exercise child sorting, binary lookup, readdir offsets, descendant collection, hardlink handling, boundary values, special names, and chunk accessors. The coverage is strong for owned-object behavior, but direct integration with real full bootstrap images and CRC propagation should be watched.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/cached_v5.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/chunk.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/chunk.rs

## Purpose
`chunk.rs` provides `ChunkWrapper`, a version-erasing and ownership-normalizing adapter for RAFS chunk metadata. It lets builder and conversion code manipulate chunk fields through one API whether the backing data is an owned v5 `RafsV5ChunkInfo`, an owned v6 intermediate chunk, or a reference to an existing `BlobChunkInfo` implementation.

## Important APIs, Types, and Functions
- `ChunkWrapper::{V5,V6,Ref}` distinguishes owned v5, owned v6-as-v5-intermediate, and borrowed trait-object chunk metadata.
- `new(RafsVersion)` creates an owned default wrapper for v5 or v6.
- Getter/setter methods expose digest, blob index, compressed/uncompressed offsets and sizes, v5 chunk index, file offset, compression/encryption/batch flags, and CRC fields.
- `set_chunk_info()` bulk-populates chunk location/size/flag fields. It honors encryption only for the v6 variant; v5 records compression and CRC flags.
- `copy_from()` copies data across owned v5/v6 wrappers and converts supported reference wrappers into owned data first.
- `store()` serializes the effective chunk as a `RafsV5ChunkInfo` through `RafsStore`, including v6 and reference cases.
- `ensure_owned()` converts supported `Ref` variants into `V5` or `V6` by downcasting to `BlobMetaChunk`, `DirectChunkInfoV6`, `TarfsChunkInfoV6`, `CachedChunkInfoV5`, or `DirectChunkInfoV5`.
- `as_blob_v5_chunk_info()` and `to_rafs_v5_chunk_info()` bridge generic `BlobChunkInfo` trait objects to the v5-compatible field set required by RAFS metadata.

## Control Flow
Read-only operations dispatch directly by enum variant. Mutating operations first call `ensure_owned()`; if the wrapper is a supported reference type, it is converted into an owned `RafsV5ChunkInfo` payload and the mutation proceeds. Unsupported references panic. Serialization follows the same conversion path for `Ref`, constructing a temporary `RafsV5ChunkInfo` and storing it.

## State and Persistence Behavior
Owned variants store chunk metadata in memory until written with `store()`. `Ref` variants share external chunk metadata through `Arc<dyn BlobChunkInfo>` and are immutable until converted. Persistence format is v5 chunk layout even for v6 intermediate data, matching the rest of RAFS v6 code that reuses `RafsV5ChunkInfo` as an intermediate representation for chunk tables and conversion.

## Dependencies and Integration Points
The wrapper depends on storage traits from `nydus_storage::device`, the v5 chunk layout type, direct and cached chunk implementations from sibling modules, and `BlobMetaChunk` from storage metadata. It is an integration point between image-building/conversion code and runtime chunk providers. It also participates in `InodeWrapper::create_chunk()` and any code that needs to serialize chunk metadata without caring whether it came from cached v5, direct v5, direct v6, tarfs, or blob metadata.

## Risks and Edge Cases
- Unsupported `Ref` trait objects panic rather than returning `Result`, so callers must only wrap known chunk implementations before calling v5-specific accessors or mutations.
- `set_chunk_info()` ignores the `is_encrypted` argument for v5 by design; using it with a v5 target loses encryption state.
- `is_compressed()`, `is_batch()`, `crc32()`, and similar `Ref` accessors call `as_blob_v5_chunk_info()` and therefore require the reference to implement the v5 extension trait by downcast.
- `Display` and `Debug` for references can panic on unsupported reference types.
- The conversion funnel assumes v6 chunk metadata can be represented in `RafsV5ChunkInfo`; future v6-only fields would need explicit extension.

## Test Signals
Tests cover v5 and v6 wrappers, supported cached/tarfs references, setter/getter round trips, `copy_from()` between versioned wrappers, expected panics for unsupported `MockChunkInfo` references and forbidden direct mutation of unknown references, and formatting output. Coverage validates the panic contract but does not cover `store()` error propagation or `DirectChunkInfoV6`/`BlobMetaChunk` reference conversions directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/chunk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/direct_v5.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/direct_v5.rs

## Purpose
`direct_v5.rs` implements the direct-mapped RAFS v5 metadata backend. Instead of copying all metadata into Rust-owned inode structures, it memory maps the bootstrap and wraps offsets into the mapped file. This lowers initialization cost and memory footprint while still implementing the standard RAFS superblock, inode, and chunk traits.

## Important APIs, Types, and Functions
- `DirectMappingState` owns the current `RafsSuperMeta`, mapped inode table, loaded blob table, `FileMapState`, and validation flags. It is the only structure allowed to hold mapping-backed raw state.
- `DirectSuperBlockV5` wraps `ArcSwap<DirectMappingState>` to provide RCU-like metadata replacement for `load()` and `update()`.
- `update_state()` validates bootstrap size/alignment, validates metadata ranges for inode table, blob table, and extended blob table, prefetches the file, maps it, loads blob tables, constructs an inode table from the mapped region, and atomically swaps the state.
- `get_inode_wrapper()` resolves inode number through the mapped inode table, validates the mapped inode wrapper, and optionally runs digest validation.
- `OndiskInodeWrapper` stores the superblock clone plus byte offset. It reconstructs `RafsV5Inode`, name, xattr data, symlink target, child references, and chunks from the current mapping state on demand.
- `_get_chunk_info()` computes the offset of a chunk record after fixed inode data, xattrs, and preceding chunks, then returns `DirectChunkInfoV5`.
- `DirectChunkInfoV5` stores mapping plus chunk offset and cached digest, implementing `BlobChunkInfo` and `BlobV5ChunkInfo`.

## Control Flow
Load/update flow is file-backed: clone the reader fd, validate metadata ranges against the file, call `readahead()`, map the file, load blob tables through the reader, build an inode table view into the mapping, then swap the active state. Lookup flow resolves inode number to an offset in the mapped inode table and returns an `OndiskInodeWrapper`. Directory lookup binary-searches child inode names using `i_child_index` and `i_child_count`. Readdir synthesizes `"."` and `".."`, then resolves children by index. File IO uses `rafsv5_alloc_bio_vecs()` through the v5 inode/chunk trait methods, with chunk metadata read from mapped records on demand.

## State and Persistence Behavior
The persistent source of truth is the bootstrap file. Runtime state holds a memory mapping, a mapped inode table `Vec` wrapped in `ManuallyDrop`, and a loaded blob table. `ArcSwap` allows existing wrappers to keep old mappings alive while new callers see updated state after `update()`. `destroy()` swaps in an empty default state. The backend does not mutate mapped metadata; it rebuilds state from a supplied reader on update.

## Dependencies and Integration Points
This file depends on `nydus_utils::filemap` for mapping and range validation, `arc_swap` for state replacement, `nydus_storage` for blob traits and readahead, and `metadata/layout/v5` for on-disk types, alignment, blob tables, inode table, chunk allocation, and digest validation. It implements the same external traits as the cached v5 backend, so higher filesystem layers can choose cached or direct mode without changing lookup/IO code.

## Risks and Edge Cases
- The mapped inode table is built with `Vec::from_raw_parts()` over mmap memory and protected with `ManuallyDrop`; incorrect `mmapped_inode_table` handling would cause invalid free or leak behavior.
- Several methods use `unwrap()` after earlier validation. Any missed range validation can become a panic in direct mode because the code dereferences mapped records on demand.
- `validate()` returns `EOPNOTSUPP` for chunk-dict regular files, and `get_inode_wrapper()` ignores that specific error. Consumers must understand that some validation checks are skipped for chunk-dict images.
- Directory lookup assumes children are sorted by name in bootstrap order.
- File size, range, and intersection checks are central security boundaries because the bootstrap may be untrusted.
- `get_max_ino()` uses inode table length rather than superblock inode count, which is consistent with direct lookup but can differ from malformed metadata.

## Test Signals
This file does not contain its own test module in the inspected source. Behavior is indirectly covered by shared v5 layout, cached v5, inode wrapper, and allocation tests elsewhere, but direct mmap-specific paths such as range rejection, `ArcSwap` update lifetime, extended blob table overlap, mapped xattr parsing, and `DirectChunkInfoV5` field access deserve targeted integration tests with synthetic bootstrap files.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/direct_v5.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/direct_v6.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/direct_v6.rs

## Purpose
`direct_v6.rs` implements the direct-mapped RAFS v6 metadata backend, including EROFS-style inode and directory handling, v6 blob/chunk table access, tarfs mode handling, and blob-device-backed chunk resolution. Like direct v5, it maps the bootstrap and wraps offsets, but v6 differs in inode numbering, directory entry layout, inline xattrs, chunk-address storage, and chunk table lookup.

## Important APIs, Types, and Functions
- `DirectMappingState` stores `Arc<RafsSuperMeta>`, `RafsV6BlobTable`, blob extra info, and `FileMapState`; it also computes tarfs mode and block size.
- `DirectCachedInfo` stores immutable mount-time derived values: metadata offset, root inode, chunk size, lazy chunk map, and FUSE timeouts.
- `DirectSuperBlockV6` owns cached info, `ArcSwap<DirectMappingState>`, and a mutable `BlobDevice` handle used when chunk digests/device metadata are available.
- `update_state()` validates blob table range, prefetches and maps the bootstrap, loads the v6 blob table and blob extra info, and atomically swaps the state.
- `disk_inode()` chooses compact or extended v6 inode layout from inode format bits.
- `inode_wrapper()` converts nid to offset using `meta_offset + nid * EROFS_INODE_SLOT_SIZE`; `inode_wrapper_with_info()` also attaches parent/name context needed for non-root extended inode APIs.
- `OndiskInodeWrapper` implements inode operations, directory traversal, xattr access, symlink access, and chunk IO allocation.
- `data_block_offset()`, `flat_data_block_offset()`, `get_entry()`, `entry_name()`, `get_entry_count()`, and `find_target_block()` implement EROFS flat directory data navigation and binary search.
- `chunk_addresses()` reads inline v6 chunk-address arrays; `make_chunk_io()` converts a chunk address to a `BlobIoDesc` using tarfs fake chunks or `BlobDevice`.
- `DirectChunkInfoV6` wraps chunk table entries stored as `RafsV5ChunkInfo`; `TarfsChunkInfoV6` synthesizes uncompressed chunk info for tarfs mode.

## Control Flow
Load/update maps the bootstrap and loads v6 blob metadata. Inode lookup computes the inode offset from nid and constructs an `OndiskInodeWrapper`. Extended lookup can return root with explicit name/parent, can enrich directories by locating their parent and name, but rejects non-directory non-root inodes because v6 on-disk inode records do not store parent/name. Directory traversal iterates data blocks, determines entries per block from the first dirent name offset, derives each name from adjacent name offsets or last-entry bounds, and calls the handler with a child wrapper carrying parent/name context. Name lookup first binary-searches directory blocks by first/last names, then binary-searches the target block. Regular-file IO starts from the requested offset, reads chunk-address records, creates blob descriptors, groups contiguous descriptors by blob, and handles tail chunks specially for tarfs.

## State and Persistence Behavior
The bootstrap mapping and blob table are immutable within a `DirectMappingState`; updates swap a whole new state. A `Mutex<Option<HashMap<RafsV6InodeChunkAddr, usize>>>` lazily caches a map from inline chunk addresses to chunk-table indexes for images that need table lookup. `BlobDevice` is stored behind a mutex and can be set after load; when present and inline chunk digests are enabled, chunk lookup delegates to the device. Tarfs mode uses 512-byte block addressing and synthesized chunk info rather than compressed blob chunk metadata.

## Dependencies and Integration Points
The module depends on `layout/v6` for EROFS-compatible inode, dirent, xattr, chunk-address, namespace, blob-table, and block-size constants. It reuses `layout/v5::RafsV5ChunkInfo` for chunk table entries and implements `BlobV5ChunkInfo` for compatibility with common chunk wrappers. It integrates with `BlobDevice` for chunk IO construction and with higher metadata traits through `RafsSuperBlock`, `RafsSuperInodes`, `RafsInode`, and `RafsInodeExt`.

## Risks and Edge Cases
- `ino()` asserts that `offset > meta_offset`; root or malformed offset handling must preserve that invariant.
- Many directory parsing operations convert invalid mapped data into `InvalidImageData`, but some counting paths use `unwrap_or(0)`, which can hide malformed block entries in `get_child_count()`.
- `get_xattr()` and `get_xattrs()` walk inline xattr entries with manual size accounting. Off-by-one or alignment mistakes can skip the last entry or reject boundary-sized attributes.
- `alloc_bio_vecs()` asserts all requested bytes are consumed; malformed chunk address arrays or blob-device misses become errors before the assertion, but arithmetic invariants are critical.
- `get_chunk_info()` has three different resolution paths: blob device with inlined digest, tarfs synthesis, or lazy chunk-map lookup. Differences in chunk address equality or block size can break fallback lookup.
- The module comment still mentions v5 layout in places; maintainers need to distinguish copied direct-v5 design notes from v6-specific behavior.

## Test Signals
Local tests cover tarfs/non-tarfs block-size selection and `TarfsChunkInfoV6` getter behavior, including zero and large values, fixed digest, v5-compatible interface, and CRC defaults. There is no local test coverage for mapped v6 directory parsing, xattr walking, inode validation, chunk-address IO vector assembly, lazy chunk-map construction, blob-device-backed chunk lookup, or state update range validation; these are the highest-value future test areas.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/direct_v6.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/inode.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/inode.rs

## Purpose
`inode.rs` provides version-neutral inode wrappers and an in-memory RAFS v6 inode intermediate representation. It is used by builder, converter, and metadata code that needs to inspect or mutate inode fields without committing to cached v5, direct v5, direct v6, or owned v5/v6 structures.

## Important APIs, Types, and Functions
- `InodeWrapper::{V5,V6,Ref}` wraps owned `RafsV5Inode`, owned `RafsV6Inode`, or `Arc<dyn RafsInodeExt>`.
- `new(RafsVersion)` constructs an owned default wrapper for v5 or v6.
- `from_inode_info()` wraps runtime inode trait objects.
- `is_v5()` and `is_v6()` classify owned or referenced implementations by enum variant/downcast.
- Field accessors and setters cover mode, type checks, inode number, parent, size, uid/gid, mtime, blocks, rdev, project id, nlink, digest, name size, symlink size, child index, child/chunk count, xattr/hardlink flags, and chunk creation.
- `ensure_owned()` converts a `Ref` into an owned v5 or v6 IR by using `RafsV5Inode::from(&dyn RafsInodeExt)` or `RafsV6Inode::from(&dyn RafsInodeExt)`.
- `RafsV6Inode` is a compact builder-side structure with RAFS common fields and helpers for file type, hardlink, xattr, hole, uid/gid, and mtime.
- `RafsInodeFlags` defines v5-style flags: `SYMLINK`, `HARDLINK`, `XATTR`, and `HAS_HOLE`.

## Control Flow
Most methods dispatch by wrapper variant. Read methods either read owned fields or proxy to `RafsInodeExt`/`RafsInode` for references. Mutating methods call `ensure_owned()` first; after conversion, they mutate owned fields and panic if a reference unexpectedly remains. Some APIs are intentionally version-specific: v6 parent access is unimplemented, v5-only digest access is unimplemented for v6, and some special-file methods on `Ref` are unimplemented if the common trait surface is insufficient.

## State and Persistence Behavior
`InodeWrapper` is an in-memory adapter and does not directly persist metadata. Owned variants can later be serialized by layout/store code. `Ref` variants share runtime metadata objects until mutation, at which point they snapshot into owned IR. `RafsV6Inode::from(&dyn RafsInodeExt)` copies FUSE-style attributes plus RAFS extension fields, so it is a lossy but practical bridge for builder/converter workflows.

## Dependencies and Integration Points
The wrapper bridges `cached_v5::CachedInodeV5`, `direct_v5::OndiskInodeWrapper`, `direct_v6::OndiskInodeWrapper`, `layout/v5::RafsV5Inode`, `layout/v6::{RafsV6InodeCompact,RafsV6InodeExtended}`, `RafsXAttrs`, `ChunkWrapper`, and `RafsVersion`. It is a central compatibility layer between metadata readers and metadata writers.

## Risks and Edge Cases
- Several methods use `unimplemented!()` or `panic!()` for unsupported variant/version combinations. Callers must branch on `is_v5()`/`is_v6()` before using version-specific methods.
- `ensure_owned()` calls `self.is_v6()` while holding a cloned reference path; unsupported reference types or incomplete downcasts can lead to assertions or incorrect ownership conversion.
- `name_size()` for `Ref` depends on runtime inode name context. Direct v6 non-root non-directory references often cannot provide extended name/parent information.
- `set_symlink_size()` sets the symlink flag but not target data; callers must maintain the associated variable-length symlink payload elsewhere.
- `RafsV6Inode` reuses `RafsInodeFlags`, even though v6 runtime direct wrappers return zero flags; builder-side and runtime-side flag semantics differ.

## Test Signals
Tests exercise wrapper classification, field setters/getters for owned v5/v6, conversion from cached/direct refs, expected panics for unsupported ref mutations or version-specific access, v6 inode helper methods, size calculation with xattrs, and default flag behavior. The tests are broad for adapter panic contracts but do not verify serialization round trips for owned v6 IR.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/inode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/layout/mod.rs -->
# sources/cloud-native/nydus/rafs/src/metadata/layout/mod.rs

## Purpose
`layout/mod.rs` is the shared metadata layout utility module for RAFS. It defines RAFS version constants, root inode identity, xattr type aliases and validation helpers, unsafe byte-structure conversion macros, common xattr parsing/storage utilities, and `MetaRange` range validation used by direct-mapped metadata loaders.

## Important APIs, Types, and Functions
- Version constants: `RAFS_SUPER_VERSION_V4`, `RAFS_SUPER_VERSION_V5`, `RAFS_SUPER_VERSION_V6`, `RAFS_SUPER_MIN_VERSION`, and `RAFS_V5_ROOT_INODE`.
- `XattrName` and `XattrValue` are byte-vector aliases used by inode APIs.
- `pub mod v5` and `pub mod v6` expose version-specific on-disk layout structures.
- `RafsBlobTable` is a simple enum over v5 and v6 blob table implementations.
- `impl_bootstrap_converter!` generates checked `TryFrom<&[u8]>`, `TryFrom<&mut [u8]>`, `AsRef<[u8]>`, and `AsMut<[u8]>` for fixed-size layout structs, enforcing exact size and alignment before unsafe casting.
- `impl_pub_getter_setter!` generates little-endian public getters/setters for on-disk fields.
- `parse_string()` parses UTF-8 data into a leading string and trailing remainder split at the first NUL.
- `bytes_to_os_str()` converts raw bytes to Unix `OsStr` without UTF-8 validation.
- `parse_xattr()`, `parse_xattr_names()`, and `parse_xattr_value()` parse v5-style xattr records encoded as little-endian pair length plus `name\0value`.
- `RafsXAttrs` owns xattr pairs and validates allowed prefixes and key/value sizes.
- `MetaRange` validates aligned metadata regions, overflow, containment, and intersection.

## Control Flow
Fixed layout conversion starts with macro-generated size/alignment checks before any unsafe cast. Xattr parsing walks a bounded byte slice, repeatedly reading a pair length, validating that enough bytes remain, splitting the pair at the first NUL, and invoking a callback. `parse_xattr_names()` and `parse_xattr_value()` are thin callback specializations. `RafsXAttrs::add()` validates key length, value length, and namespace prefix before inserting. `MetaRange::new()` rejects unaligned or overflowing ranges; direct metadata loaders compose `is_subrange_of()` and `intersect_with()` to reject malformed bootstrap sections.

## State and Persistence Behavior
This module mostly defines stateless helpers. `RafsXAttrs` is the owned stateful piece; it stores pairs in a `HashMap<OsString, Vec<u8>>` and computes serialized v5 size from key/value lengths. It does not itself write xattrs in this file, but version-specific layout modules use it for storage sizing and serialization. `MetaRange` is an immutable validation value.

## Dependencies and Integration Points
The module is imported by cached and direct metadata backends for root inode constants, xattr parsing, byte-to-name conversion, and metadata range validation. Version-specific modules `layout/v5` and `layout/v6` depend on the macros and shared xattr concepts. `MetaRange` is a security boundary for direct mmap backends, while `parse_xattr*` is the shared parser for cached and direct v5 xattr access.

## Risks and Edge Cases
- `impl_bootstrap_converter!` uses unsafe casts after checks; all callers rely on exact length and alignment validation being correct.
- `parse_xattr()` silently ignores a pair with no NUL separator rather than returning an error, which may hide malformed xattr records.
- `parse_string()` requires UTF-8, while many filesystem names are handled as raw `OsStr`; callers must choose the correct helper.
- `RafsXAttrs::add()` allows only predefined prefixes and caps key/value sizes. That is good for consistency but can reject future namespaces unless the prefix list is updated with v6 namespace constants.
- `MetaRange` alignment uses `RAFSV5_ALIGNMENT` even though it is also used by v6 direct validation; this is currently compatible with the code's assumptions but should be revisited if v6 alignment constraints diverge.

## Test Signals
Tests cover unsafe converter rejection for misalignment and wrong length, mutable conversion and byte views, UTF-8/NUL parsing, invalid and valid xattr records, and `MetaRange` overflow, alignment, containment, and intersection behavior. There is no test for xattr pairs without NUL separators or for all allowed `RafsXAttrs::add()` prefixes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/metadata/layout/mod.rs -->
