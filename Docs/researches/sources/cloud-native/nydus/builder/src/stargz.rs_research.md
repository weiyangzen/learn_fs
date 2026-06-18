# sources/cloud-native/nydus/builder/src/stargz.rs

## Purpose
`stargz.rs` implements `StargzBuilder`, which builds a RAFS v6 bootstrap from an eStargz TOC while reusing the stargz/tar gzip layer as the data blob. It parses TOC entries, builds a tree, converts eStargz chunk records into RAFS chunk metadata, handles symlinks, hardlinks, xattrs, and then emits bootstrap/blob metadata without rewriting original layer payload bytes.

## Important APIs, types, and functions
`TocEntry` models eStargz JSON entries, including path/type, size, link target, mode/uid/gid, device numbers, xattrs, digests, compressed offsets, chunk offsets/sizes, and inner offset. It exposes type predicates, `is_supported()`, `has_xattr()`, `mode()`, `rdev()`, `size()`, `name()`, `path()`, link helpers, `block_id()`, and `normalize()`. `TocIndex::load()` reads and normalizes a version-1 TOC.

`StargzBuilder` stores blob size, a `TarBuilder`, `file_chunk_map`, `hardlink_map`, and running uncompressed offset. Key methods are `new()`, `build_tree()`, `get_content_size()`, `parse_entry()`, `sort_and_validate_chunks()`, `fix_chunk_info()`, `fix_nodes()`, and `Builder::build()`.

## Control flow, state, and persistence
`build()` validates v6, gzip compression, and sha256 digester, creates writers/context, builds a tree from the TOC, runs shared `build_bootstrap()`, fixes chunk info and nodes, dumps blob metadata, and then finalizes bootstrap/blob in inline or separate order. `build_tree()` loads TOC entries, skips unsupported/special eStargz entries, derives chunk sizes from regular/chunk records, creates `NodeChunk`s with compressed offsets and chunk digests, tracks uncompressed offsets with optional 4 KiB alignment, parses non-chunk entries into nodes, then validates each file's chunk list.

`parse_entry()` creates `Node` objects directly from TOC metadata. It resolves hardlink targets already present in the tree, records hardlink node references, decodes base64 xattrs, sets symlink target and flags, and inserts the node through `TarBuilder`. `fix_chunk_info()` sorts all chunks by uncompressed offset, computes compressed sizes from adjacent compressed offsets or blob size using gzip-size estimation, allocates chunk indices, records blob metadata, and updates blob sizes. `fix_nodes()` copies chunk lists and sizes from `file_chunk_map` into tree nodes and mirrors target chunks/xattrs into hardlink nodes.

## Dependencies and integration points
The module integrates `TarBuilder`, `Tree`, `Node`, `NodeInfo`, `NodeChunk`, common `build_bootstrap/dump_bootstrap/finalize_blob`, `Blob`, `BlobManager`, and `BootstrapManager`. It depends on eStargz TOC JSON via `serde`, base64 xattrs, gzip compression helpers, RAFS v6 inode/chunk types, and Nydus blob limits. It is exported from `lib.rs` as `StargzBuilder`.

## Risks and test signals
Hardlinks require target entries to appear earlier in the TOC; missing or non-regular targets fail. Chunk alignment and size validation are strict. The chunk validation loop may skip checking the final adjacent pair for files with multiple chunks; the final size check catches some but not all hole/overlap patterns. Tests cover building from a fixture eStargz TOC, expected blob id/blob size/bootstrap path, `TocEntry` predicates/mode/rdev/name/block id/normalize behavior, and error paths; multi-chunk holes and hardlink failures need more coverage.
