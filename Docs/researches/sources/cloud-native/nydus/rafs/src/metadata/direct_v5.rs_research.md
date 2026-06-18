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
