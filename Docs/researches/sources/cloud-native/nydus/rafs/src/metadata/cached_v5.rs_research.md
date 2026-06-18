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
