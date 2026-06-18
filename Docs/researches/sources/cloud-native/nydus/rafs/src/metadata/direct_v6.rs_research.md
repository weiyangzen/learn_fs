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
