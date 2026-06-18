# subset-b-000221 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/node.rs -->
## sources/cloud-native/nydus/builder/src/core/node.rs

### Purpose
`node.rs` defines the in-memory file metadata and chunk model used by the Nydus RAFS builder. It is the bridge between filesystem or archive input and RAFS bootstrap/blob output: a `Node` owns an `InodeWrapper`, source/target path information, xattrs, symlink state, overlay state, v6 layout state, and the `NodeChunk` list used for regular-file data. The file also contains the main data dumping path that reads file bytes, computes chunk digests/CRC, performs deduplication, writes compressed/encrypted blob data, and records blob metadata.

### Important APIs, types, and functions
`ChunkSource` identifies whether a chunk was produced in the current build, referenced from a chunk dictionary, or inherited from a parent image. `NodeChunk` wraps an `Arc<ChunkWrapper>` and provides copy-on-write setters for index, blob index, compressed size, and file offset. `NodeInfo` stores sharable, mostly immutable attributes such as source inode/device, source and target paths, symlink target, xattrs, and v6 compact/extended hints. `Node` is the mutable build unit: it holds inode state, chunk vector, layer index, overlay status, and v6-specific offsets and dirents.

`Node::from_fs_object()` builds a node from a local filesystem object, using `generate_target()` and `generate_target_vec()` to derive RAFS paths, then calls `build_inode()`. `build_inode_xattr()` reads host xattrs and marks the inode when xattrs exist. `build_inode_stat()` copies stat metadata, with explicit UID/GID controlled by `NodeInfo`, ignores root mtime for repeatable builds, and calculates regular-file size/blocks. `dump_node_data()` opens the local file for regular nodes and delegates to `dump_node_data_with_reader()`. The reader variant covers directories, symlinks, special files, external blobs, tar-ref/zran readers, deduplication, blob writes, blob-cache output, and inode digest finalization. `read_file_chunk()`, `dump_file_chunk()`, `write_chunk_data()`, `deduplicate_chunk()`, and `set_external_chunk_crc32()` are the main internal data-path helpers. Accessors such as `is_reg()`, `is_dir()`, `chunk_count()`, `name()`, `target()`, `set_symlink()`, `set_xattr()`, and `remove_xattr()` are used throughout the builder.

### Control flow and state behavior
For a normal regular file, `dump_node_data_with_reader()` iterates `inode.child_count()` chunks, reads the chunk from either the local reader, zran generator, or tar reader, calculates IDs and CRCs unless running tarfs/external mode, deduplicates against global and layered chunk dictionaries, allocates a blob and chunk index, writes or references data, appends chunk metadata, and pushes a `NodeChunk` into `self.chunks`. For directories, symlinks, and special files it returns without blob writes, but v5 symlinks and special files still get inode digests. For external blobs, it reads chunk layout from `ctx.attributes`, creates chunk references without writing data, and optionally copies CRCs from attributes.

The module mutates both local node state and shared build state. It updates `BlobContext` offsets, sizes, hash state, chunk count, batch metadata, and optional cache artifacts. It updates `BlobManager` by creating blobs, adding chunk metadata, and registering referenced dictionary blobs only when actually used. `NodeInfo` is stored behind `Arc`; setter methods clone and replace it to preserve cheap cloning of nodes. Persistence happens indirectly through blob writers, blob cache generators, `BlobContext` metadata, and later bootstrap dumping in `v5.rs`/`v6.rs`.

### Dependencies and integration points
This file depends heavily on `nydus_rafs` inode/chunk/layout wrappers, `nydus_storage` blob metadata structures, `nydus_utils` compression, encryption, digest, crc32, tracing, and alignment helpers, and `parse_size` for external blob attributes. It is called by directory, tarball, stargz, bootstrap, and prefetch optimization builders. `Tree` owns `Node` values; `overlay.rs` extends `Node` with whiteout methods; `v5.rs` and `v6.rs` extend `Node` with serialization/layout methods.

### Risks and edge cases
The data path is sensitive to chunk count/size consistency and offset accounting. External mode trusts attributes such as `blob_index`, `blob_id`, `chunk_size`, compressed offsets, and file size; bad attributes surface as parse errors or incorrect metadata. `deduplicate_chunk()` must correctly remap dictionary blob indices into real blob-table indices, or bootstrap chunk references will point at the wrong blob. `dump_file_chunk()` has several mutually exclusive modes (`SEPARATE`, batch generation, cache generation, tar-ref), so feature combinations need regression coverage. Root mtime normalization and directory block synthesis are repeatability-critical. The xattr path must handle unsupported filesystems gracefully but fail on other xattr read errors.

### Test signals
Unit tests cover `NodeChunk` copy-on-write setters, `dump_node_data()` for directory/symlink/special/regular cases with tar-reader and cache generator setup, chunk-count overflow behavior, file type/name/target-vector helpers, xattr removal behavior, and external chunk CRC selection/error handling. The tests exercise important branches but do not exhaust external attribute combinations, encryption plus compression output bytes, or chunk-dictionary remapping across multiple blobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/overlay.rs -->
## sources/cloud-native/nydus/builder/src/core/overlay.rs

### Purpose
`overlay.rs` centralizes whiteout and overlay-state semantics for merging multiple RAFS filesystem trees. It supports OCI image whiteouts, Linux overlayfs whiteouts, and a mode that disables whiteout handling. The module is intentionally small but critical: `Tree::merge_overaly()` relies on these classifications to decide which lower-layer nodes are removed, replaced, retained, or marked opaque.

### Important APIs, types, and functions
The public constants are `OCISPEC_WHITEOUT_PREFIX` (`.wh.`), `OCISPEC_WHITEOUT_OPAQUE` (`.wh..wh..opq`), and `OVERLAYFS_WHITEOUT_OPAQUE` (`trusted.overlay.opaque`). `WhiteoutSpec` is a parseable/displayable enum with `Oci`, `Overlayfs`, and `None`. `WhiteoutType` distinguishes OCI opaque/removal and overlayfs opaque/removal; `is_removal()` groups the removal variants. `Overlay` marks a node as `Lower`, `UpperAddition`, or `UpperModification` and exposes `is_lower_layer()`.

The module implements methods on `Node`: `is_overlayfs_whiteout()` detects character-device 0/0 whiteouts under overlayfs mode, `is_overlayfs_opaque()` detects directory xattr `trusted.overlay.opaque=y`, `whiteout_type()` combines spec and node state into a whiteout classification while ignoring lower-layer nodes, and `origin_name()` maps whiteout nodes back to the original lower-layer name to remove.

### Control flow and state behavior
`whiteout_type()` returns `None` for lower-layer nodes and when `WhiteoutSpec::None` is active. Under OCI mode it inspects the node name for `.wh..wh..opq` or `.wh.` prefix. Under overlayfs mode it checks device number and opaque xattr. `origin_name()` strips `.wh.` for OCI removals and returns the node name for overlayfs device whiteouts.

The module does not persist state directly; its output controls tree mutation in `tree.rs`. Overlayfs opaque handling also affects persistence indirectly because `Tree::merge_children()` removes the `trusted.overlay.opaque` xattr after applying opacity so the marker does not leak into the merged image.

### Dependencies and integration points
It depends on `Node`, unix `OsStrExt`, and `nydus_utils::compact::{major_dev, minor_dev}` through fully-qualified calls. `DirectoryBuilder` uses `Node::whiteout_type()` to skip upper-layer whiteout markers in single-layer builds. `Tree::merge_children()` uses all four `WhiteoutType` values. CLI/config parsing can use `WhiteoutSpec::from_str()`.

### Risks and edge cases
OCI whiteouts require UTF-8 names because `whiteout_type()` uses `to_str()`; non-UTF-8 `.wh.` byte sequences would not be treated as whiteouts. Overlayfs whiteout detection depends on the source inode being a character device and `NodeInfo.rdev` being accurate. `WhiteoutSpec::None` deliberately leaves markers visible, which is useful for some modes but dangerous if enabled accidentally. Because lower-layer nodes are ignored by `whiteout_type()`, callers must set overlay state correctly before merging.

### Test signals
Tests cover `WhiteoutSpec` parsing/display, `WhiteoutType::is_removal()`, and overlay lower-layer checks. The visible test block starts broader node-whiteout tests after the shown section; the main integration signal remains `Tree::merge_children()` behavior in tree/merge builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/overlay.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/prefetch.rs -->
## sources/cloud-native/nydus/builder/src/core/prefetch.rs

### Purpose
`prefetch.rs` manages filesystem/blob prefetch configuration for the builder. It parses prefetch path patterns, tracks which tree nodes match those patterns, orders selected regular files near the front of blob layout, and emits RAFS v5/v6 prefetch tables for filesystem-level prefetch.

### Important APIs, types, and functions
`PrefetchPolicy` supports `None`, `Fs`, and `Blob` and is parsed from strings. `Prefetch` stores the policy, a disabled flag, an ordered `IndexMap<PathBuf, Option<TreeNode>>` of patterns, a list of prefetch regular files tagged by pattern index, and a BFS-ordered non-prefetch node list. `Prefetch::new()` reads path patterns from stdin unless policy is `None`. `generate_patterns()` normalizes user input by requiring absolute paths and dropping redundant child paths already covered by an earlier parent pattern.

`Prefetch::insert()` classifies a tree node against exact or parent-directory pattern matches. `get_file_nodes()` returns prefetch files sorted by pattern order plus non-prefetch files in traversal order. `fs_prefetch_rule_count()` counts matched filesystem prefetch patterns. `get_v5_prefetch_table()` emits inode numbers, while `get_v6_prefetch_table(meta_addr)` emits calculated v6 nids based on `node.v6_offset` and the final metadata address. `disable()` and `clear()` control transient state.

### Control flow and state behavior
The normal flow is: construct `Prefetch`, traverse the tree, call `insert()` for each node, then use `get_file_nodes()` to affect blob write order and call version-specific table generation during bootstrap dumping. `insert()` stores exact matched nodes in the pattern table only for exact path hits, but it marks regular files under matched directories as prefetch files using the parent pattern index. Empty regular files and disabled/no-policy cases go to non-prefetch.

State is in-memory only until bootstrap dumping. For v5, selected pattern nodes are persisted as inode numbers in `RafsV5PrefetchTable`. For v6, table entries are nids; this depends on v6 layout having already assigned and possibly adjusted `v6_offset`, so `v6.rs` intentionally asks for the v6 prefetch table after node dump offsets are finalized.

### Dependencies and integration points
The module uses `indexmap` to preserve user pattern order and RAFS layout table types from `nydus_rafs`. It integrates with tree traversal/build order and bootstrap dumping in `v5.rs` and `v6.rs`. `DirectoryBuilder` resets prefetch to `None` for the separate external-tree build. Blob-level prefetch is represented by policy but its physical optimization is handled elsewhere, notably `optimize_prefetch.rs`.

### Risks and edge cases
Reading patterns directly from stdin means builder invocations using `Fs` policy can block if no input is piped. Non-absolute paths are silently skipped with warnings. Parent coverage pruning is order-sensitive: an earlier parent suppresses later children, but a later parent does not retroactively remove earlier child patterns. `get_v5_prefetch_table()` asserts inode numbers fit in `u32`; `get_v6_prefetch_table()` asserts calculated nids fit in `u32`. `clear()` also clears patterns, so it resets more than transient matches.

### Test signals
Tests cover redundant pattern generation, policy parsing, insertion/classification for exact and parent matches, ordering of prefetch files, non-prefetch fallback, `fs_prefetch_rule_count()`, and `clear()`. Tests do not cover stdin blocking behavior or actual serialized v5/v6 table bytes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/prefetch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/tree.rs -->
## sources/cloud-native/nydus/builder/src/core/tree.rs

### Purpose
`tree.rs` defines the in-memory filesystem topology used by the builder. A `Tree` wraps a `TreeNode` (`Rc<RefCell<Node>>`), caches the base name for sorted lookup, and owns children. It also loads trees from existing RAFS bootstraps and applies upper-layer changes to lower-layer trees using overlay whiteout rules.

### Important APIs, types, and functions
`Tree::new()` wraps a `Node`. `from_bootstrap()` loads a root inode from `RafsSuper`, parses it into `Node`, then recursively loads children through `MetadataTreeBuilder`. Traversal helpers include `walk_dfs()`, `walk_dfs_pre()`, `walk_dfs_post()`, and `walk_bfs()`. Mutation and lookup helpers include `insert_child()`, `get_child_idx()`, `get_node()`, `get_node_mut()`, `set_node()`, and `borrow_mut_node()`.

`merge_overaly()` replaces the root node with the upper root and calls `merge_children()`. `merge_children()` first applies whiteout markers (`OciRemoval`, `OciOpaque`, `OverlayFsRemoval`, `OverlayFsOpaque`) and then applies non-whiteout additions/modifications. `MetadataTreeBuilder::load_children()` recursively reads child inodes and chunk metadata from a bootstrap, and `parse_node()` converts `RafsInodeExt` into `Node` with chunks, symlink data, xattrs, and lower-layer overlay state.

### Control flow and state behavior
Tree children are kept sorted by byte name; insertions use binary search and path lookup depends on this invariant. DFS is used for digest/layout passes; BFS is used where RAFS/EROFS layout or output order needs breadth-first traversal. During merge, whiteouts are processed before real upper nodes so deletion/opacity affects the lower child list before replacements and additions occur. Directory additions are inserted as shallow nodes first and then recursively merged.

When loading from bootstrap, regular-file chunks are added to the caller-provided `ChunkDict` using the blob digester. This seeds deduplication against parent or dictionary data. Parsed nodes use source `/`, target derived from bootstrap path, `Overlay::Lower`, invalid source device to avoid hardlink confusion, and `ChunkSource::Parent` for chunks.

### Dependencies and integration points
`tree.rs` depends on `node.rs`, `overlay.rs`, `nydus_rafs` metadata readers, RAFS xattr helpers, and builder `ChunkDict`. It is central to `Bootstrap::new/build/dump`, `DirectoryBuilder`, `StargzBuilder`, `TarBuilder`, `Merger`, and `OptimizePrefetch`. `overlay.rs` supplies the whiteout classification, while `v5.rs`/`v6.rs` consume the resulting tree for serialization.

### Risks and edge cases
The function name `merge_overaly` is misspelled but used consistently. Path lookup assumes absolute paths whose generated target vector has root plus normal components; invalid components panic in `Node::generate_target_vec()`. `insert_child()` ignores duplicate child names, while some callers replace nodes explicitly; misuse could silently drop an addition. Whiteout behavior depends on overlay state, whiteout spec, and xattr cleanup. Bootstrap loading validates digest through `get_extended_inode(..., true)` by default, so malformed metadata can fail before tree construction.

### Test signals
Tests cover tree creation, node replacement under borrow discipline, BFS traversal counts and error propagation, sorted child insertion, and child lookup. Integration with metadata parsing and overlay merge is indirectly covered by merger and builder tests that load bootstraps.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/tree.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/v5.rs -->
## sources/cloud-native/nydus/builder/src/core/v5.rs

### Purpose
`v5.rs` contains RAFS v5-specific inode sizing, digest, and bootstrap serialization logic. It extends `Node` with v5 metadata output and repeatability helpers, and extends `Bootstrap` with the v5 dump pipeline.

### Important APIs, types, and functions
`Node::dump_bootstrap_v5()` writes a v5 inode wrapper, optional xattr table, and chunk records to the bootstrap writer. It validates that regular-file child count matches `self.chunks.len()`. `Node::v5_set_dir_size()` calculates deterministic synthetic directory sizes using child name lengths plus `RAFS_V5_VIRTUAL_ENTRY_SIZE`, rounded to 4 KiB, instead of trusting source filesystem directory sizes. `Node::v5_set_inode_blocks()` calculates stable 512-byte block counts including aligned v5 xattr size.

`Bootstrap::v5_digest_node()` computes directory digests from child inode digests in postorder. `Bootstrap::v5_dump()` constructs the v5 superblock, inode table, prefetch table, blob table, extended blob table, and serialized inodes/chunks.

### Control flow and state behavior
Before writing, `v5_dump()` walks the tree in postorder to calculate directory digests after child digests are available. It then computes table sizes and offsets: superblock, inode table, prefetch table, blob table, extended blob table, then variable inode/chunk/xattr records. A preorder walk fills inode table offsets and advances `inode_offset` based on inode size, xattr table size, and chunk count. Finally it stores all tables and dumps every node in preorder.

The module persists all v5 bootstrap metadata through `RafsIoWrite`. It mutates `ctx.has_xattr`, superblock flags, node directory sizes/blocks (from earlier builder calls), and inode digests. Blob data itself is not written here; `node.rs` and blob code produce the chunks that this file serializes.

### Dependencies and integration points
It depends on v5 layout types from `nydus_rafs`, digest helpers, alignment helpers, `BuildContext`, `BootstrapContext`, and `Tree`. It is selected by the generic `Bootstrap::dump()` path when `ctx.fs_version` is v5. `prefetch.rs` supplies optional v5 prefetch tables; `directory.rs` calls `v5_set_dir_size()` during tree construction.

### Risks and edge cases
Repeatable build behavior relies on all directory sizes/blocks being recalculated before dump. If chunk vectors are stale relative to inode child counts, dump fails. Offset arithmetic uses `u32` for inode offsets; very large bootstraps may exceed v5 format limits. `get_v5_prefetch_table()` is called once for sizing and again for storing, so the function must remain deterministic. Xattr flag handling distinguishes inode `has_xattr` from non-empty xattr payloads.

### Test signals
This file has no local test module, but it is exercised through builder tests that dump v5 bootstraps and through node/directory tests that trigger v5 size and block calculations. Coverage is strongest for helper behavior via integration, weaker for exact binary layout offsets.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/v5.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/v6.rs -->
## sources/cloud-native/nydus/builder/src/core/v6.rs

### Purpose
`v6.rs` implements RAFS v6/EROFS-style metadata layout and serialization. It assigns metadata offsets, chooses compact versus extended inodes, lays out directories and symlink tails, writes file chunk address arrays, builds prefetch and chunk tables, and writes superblock, extended superblock, device slots, and blob table.

### Important APIs, types, and functions
On `Node`, `dump_bootstrap_v6()` writes one node after adjusting offsets from original to final metadata address. `v6_set_inode_compact()` selects compact inode eligibility based on UID/GID/nlink/size/force flag and disables compact mode for `.pyc` files. `v6_set_offset()` handles regular, symlink, and special inode layout. `v6_set_dir_offset()` sets directory size and delegates to `v6_set_offset_with_tail()`. `v6_dirent_size()` computes block-constrained dirent/name bytes. Internal helpers include `v6_set_offset_with_tail()`, `v6_store_xattrs()`, `v6_dump_dir()`, `v6_dump_file()`, `v6_dump_symlink()`, and `v6_dump_inode()`.

On `BuildContext`, `v6_block_size()` chooses 512-byte blocks for tarfs and 4096-byte blocks otherwise; `v6_block_addr()` bounds-checks block addresses. On `Bootstrap`, `v6_update_dirents()` materializes `.`, `..`, and child dirent records; `v6_dump()` writes the full v6 bootstrap; `v6_align_to_4k()` pads output; and `v6_align_mapped_blkaddr()` aligns device mapping blocks.

### Control flow and state behavior
The v6 build process first assigns offsets during `Bootstrap::build()` (outside this file) using the node helpers. `v6_dump()` then computes device/blob table placement, prefetch table placement, final `meta_addr`, root nid, and extended superblock metadata. It walks the tree in BFS order and calls `dump_bootstrap_v6()` for each node. Node dumping updates `v6_offset` and `v6_dirents_offset` by `meta_offset`, sets inode number to calculated nid, and writes type-specific bodies.

Directories write an inode with block address to dirents, then serialize dirent records and names block by block, placing tail data inline or plain depending on layout. Regular files write chunk address entries after the inode and cache unique chunks in a `BTreeMap<DigestWithBlobIndex, Arc<ChunkWrapper>>` for the later chunk info table. Symlinks write target bytes inline or at `v6_dirents_offset`. After inodes, `v6_dump()` writes optional prefetch table, chunk table, device slots, superblock, extended superblock, and blob table.

### Dependencies and integration points
This file uses many `nydus_rafs::metadata::layout::v6` constants and structs, `BlobInfo` feature flags, `BuildContext`, `BootstrapContext`, `Tree`, and chunk dictionary digest keys. It consumes `Prefetch` state from `prefetch.rs`, chunk lists from `node.rs`, and blob tables from `BlobManager`. It is central to `DirectoryBuilder`, `StargzBuilder`, `TarBuilder`, `Merger`, and `OptimizePrefetch` whenever v6 is selected.

### Risks and edge cases
Offset arithmetic is the main risk. Inline tail layout tries to reuse available block fragments, so off-by-one alignment mistakes can corrupt directories or symlinks. `dump_bootstrap_v6()` mutates node offsets during dumping; repeated dumps on the same tree would need care. Device slot and block count calculations enforce `u32` limits and blob id length <= 64. The chunk cache key includes external chunk index for external blobs; changing this could collapse distinct chunks incorrectly. `v6_dump_dir()` must handle multibyte names by byte length, not character count.

### Test signals
Tests cover regular, symlink, and directory offset layout across many boundary cases, compact inode decisions including `.pyc`, and block-size constants in assertions. Integration tests in builders and merger exercise full v6 dump/load paths, but exact binary layout remains high-risk and best protected by mount/load regression fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/core/v6.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/directory.rs -->
## sources/cloud-native/nydus/builder/src/directory.rs

### Purpose
`directory.rs` implements `DirectoryBuilder`, the builder that scans a local filesystem directory and produces RAFS bootstrap/blob output. It constructs a `Tree` of `Node`s from `fs::read_dir()`, handles whiteout filtering, supports external blob attributes by building a parallel external tree, and runs the common bootstrap/blob dump sequence.

### Important APIs, types, and functions
`FilesystemTreeBuilder::load_children()` recursively builds child trees from the source directory. It reads external file size from `ctx.attributes`, creates nodes through `Node::from_fs_object()`, skips single-layer whiteout marker files, recurses into directories, calculates v5 directory size, and divides results between the normal tree and external tree. `DirectoryBuilder::build_tree()` creates root nodes and delegates recursion. `DirectoryBuilder::one_build()` performs one complete build for a provided tree. `impl Builder for DirectoryBuilder::build()` orchestrates normal and external builds.

### Control flow and state behavior
The public `build()` computes layer index from parent-bootstrap presence, scans the source into `(tree, external_tree)`, creates a blob writer, and runs `one_build()` for the normal tree. Then it disables prefetch by replacing `ctx.prefetch` with `PrefetchPolicy::None`, creates a separate external `BlobManager` and cloned `BootstrapManager` with `external` suffix, and runs `one_build()` on `external_tree`. The final `BuildOutput` combines normal bootstrap/blob data with external bootstrap path and external blob list.

`one_build()` creates a bootstrap context, calls shared `build_bootstrap()` (which may merge with parent), dumps blob data through `Blob::dump()`, optionally dumps blob metadata, and orders `dump_bootstrap()`/`finalize_blob()` depending on whether metadata is inlined into the blob. It drops the bootstrap context with `lazy_drop()` before building output.

### Dependencies and integration points
The module integrates `Node`, `Tree`, `Blob`, `BuildContext`, `BootstrapManager`, `BlobManager`, `ArtifactWriter`, `NoopArtifactWriter`, `Overlay`, and common helpers from `lib.rs`. It depends on `attributes` behavior through `ctx.attributes.is_external()`, `is_prefix_external()`, and value lookups. It is one of the main implementations of the crate-level `Builder` trait.

### Risks and edge cases
Directory traversal uses `read_dir()` and then sorts tree children, so source filesystem order is normalized. Whiteout markers are skipped only for layer index 0 and only when not overlayfs opaque; layered builds preserve markers for merge logic. External tree construction is subtle: fully external paths are excluded from normal tree but included in external tree, while prefix-external paths can appear in both. `load_children()` clones nodes/trees, so later mutations must not assume shared identity between normal and external trees. Resetting `ctx.prefetch` before external build mutates caller context.

### Test signals
Local tests cover zero-sized constructors/defaults for `DirectoryBuilder` and `FilesystemTreeBuilder`. Behavioral coverage for scanning, whiteouts, external mode, and dump ordering is primarily through higher-level integration tests rather than direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/directory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/lib.rs -->
## sources/cloud-native/nydus/builder/src/lib.rs

### Purpose
`lib.rs` is the crate root for the Nydus builder library. It re-exports the public builder API, defines the shared `Builder` trait, provides common bootstrap/blob finalization helpers, and implements `TarBuilder`, a helper used by tarball and stargz builders to construct tree nodes from archive paths.

### Important APIs, types, and functions
Public exports include `Bootstrap`, chunk dictionary types, `ArtifactStorage`, `ArtifactWriter`, `BlobCacheGenerator`, `BlobContext`, `BlobManager`, `BootstrapContext`, `BootstrapManager`, `BuildContext`, `BuildOutput`, `ConversionType`, `Feature/Features`, `ChunkSource`, `NodeChunk`, `Overlay`, `WhiteoutSpec`, `Prefetch`, `Tree`, `DirectoryBuilder`, `Merger`, `OptimizePrefetch`, `StargzBuilder`, and `TarballBuilder`. `Builder::build()` is the common trait implemented by source-specific builders.

Shared helpers are `mode_bits()`, `build_bootstrap()`, `dump_bootstrap()`, `dump_toc()`, and `finalize_blob()`. `TarBuilder` exposes `new()`, `next_ino()`, `insert_into_tree()`, `create_directory()`, and `is_stargz_special_files()`.

### Control flow and state behavior
`build_bootstrap()` optionally loads and merges a parent bootstrap when the bootstrap context is layered, then creates a `Bootstrap` and calls `build()`. `dump_bootstrap()` finalizes the current blob id/size, converts the blob manager to a blob table, dumps bootstrap metadata, and optionally appends compressed or raw bootstrap bytes into the data blob when `blob_inline_meta` is enabled. `dump_toc()` writes a blob TOC entry and records its digest/size. `finalize_blob()` resolves blob ids and metadata digests for normal, ref, tarfs, and inline-meta modes, finalizes the writer, and finalizes optional blob cache data.

`TarBuilder::insert_into_tree()` walks target path components, replacing existing terminal nodes, creating missing intermediate directories, and preserving sorted insertion via `Tree::insert_child()`. `create_directory()` creates synthetic directory nodes with new inode numbers, default mode/nlink/rdev, and target/source paths rooted at `/`.

### Dependencies and integration points
This file ties together all internal modules (`attributes`, `chunkdict_generator`, `compact`, `core`, `directory`, `merge`, `optimize_prefetch`, `stargz`, `tarball`). It depends on `nydus_rafs`, `nydus_storage::meta::toc`, compression/digest utilities, and `sha2::Digest`. Source builders call its shared functions to avoid duplicating bootstrap/blob finalization logic.

### Risks and edge cases
Blob id resolution has several mode-specific branches. Ref conversions may derive ids from tar/zran readers, inline metadata temporarily uses `"x".repeat(64)`, and tarfs skips data blob finalization. Ordering of `dump_bootstrap()` versus `finalize_blob()` changes when metadata is inlined. `TarBuilder::insert_into_tree()` assumes path vectors include root and uses the last child index after insertion; because children are sorted, this can be fragile if insertion position is not at the end. Stargz special-file filtering is centralized here and must stay aligned with eStargz conventions.

### Test signals
Tests cover stargz special-file recognition and synthetic directory creation/inode allocation. Higher-level builder tests exercise shared finalization helpers through directory, tarball, stargz, and merge paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/merge.rs -->
## sources/cloud-native/nydus/builder/src/merge.rs

### Purpose
`merge.rs` implements image-level RAFS bootstrap merging. Given per-layer RAFS bootstraps, optional parent bootstrap, optional chunk dictionary bootstrap, and replacement blob metadata, it overlays trees using whiteout rules, remaps chunk blob indices, prunes dereferenced blobs, and writes a new merged bootstrap.

### Important APIs, types, and functions
`Merger` is a zero-sized public struct. Helper methods `get_string_from_list()`, `get_digest_from_list()`, and `get_size_from_list()` safely fetch optional per-layer metadata by index. `Merger::merge()` is the main entry point and accepts `BuildContext`, optional parent path, source bootstrap paths, optional blob digests/original ids/sizes/TOC metadata, target artifact storage, optional chunk dictionary path, and runtime config.

### Control flow and state behavior
`merge()` validates that optional metadata vectors match source count, then initializes a `BlobManager`, blob id-to-index map, and optional base tree. A parent bootstrap, if supplied, is loaded first; its blobs are added as `ChunkSource::Parent`, and its tree becomes the lower tree. A chunk dictionary bootstrap, if supplied, contributes a set of blob ids to ignore when identifying each layer's new data blob and provides compatibility config.

For each source layer, the bootstrap is loaded, metadata compatibility is checked, context compressor/digester/cipher/UID mode/tarfs flags are updated, blob contexts are created/remapped, and optional digest/size/original-id overrides are applied. The layer tree is loaded, all chunk blob indices are remapped into the merged blob manager's indices, layer indices are assigned, overlay state is set to `UpperAddition`, and the tree is merged into the accumulated tree. After all layers, tarfs conflicts with parent/chunk-dict are rejected. The code then walks the final tree to build a new used-blob manager containing only referenced blobs and rewrites chunk blob indices again to compact the blob table. Finally it builds and dumps a new bootstrap and returns `BuildOutput`.

### Dependencies and integration points
The module uses `RafsSuper::load_from_file()`, `ConfigV2`, `BlobContext`, `BlobManager`, `Bootstrap`, `BootstrapContext`, `Tree`, `Overlay`, `ChunkSource`, `BlobFeatures`, and crypto metadata. It relies on `Tree::from_bootstrap()` and `Tree::merge_overaly()` for topology and whiteouts, and on `Bootstrap::build/dump()` for output. It is likely invoked by CLI merge commands.

### Risks and edge cases
Layer metadata must be consistent: chunk size mismatches, incompatible configs, unsupported cipher algorithms, too many layers, and multiple non-dictionary blobs per layer all fail. Blob id remapping is subtle because bootstrap blob ids may differ from runtime original tar ids depending on accessibility and conversion mode. `blob_idx_map` keys use blob ids, so duplicate ids intentionally share entries. Pruning unused blobs after overlay merge is necessary; skipping it would retain blobs deleted by whiteouts. Tarfs mode forbids parent and chunk dictionary, enforced after layer processing.

### Test signals
Unit tests cover helper accessors, mismatched optional vector validation, empty source rejection, and a successful merge using fixture v6 bootstraps with metadata overrides. This gives useful coverage for validation and the happy path, but not all conflict branches such as chunk dictionary interactions, tarfs parent rejection, or cipher variants.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/merge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/optimize_prefetch.rs -->
## sources/cloud-native/nydus/builder/src/optimize_prefetch.rs

### Purpose
`optimize_prefetch.rs` generates an optimized prefetch blob from an existing RAFS tree/blob set and rewrites selected file chunks to point to that new blob. It is intended to improve startup or hot-path reads by copying configured chunks into a separate blob marked with prefetch-related features, then dumping an updated bootstrap.

### Important APIs, types, and functions
`OptimizePrefetch` is a zero-sized public struct. `PrefetchBlobState` groups the new `BlobInfo`, `BlobContext`, and writer. `PrefetchFileInfo` stores an absolute path and optional byte ranges parsed from JSON. `generate_prefetch()` is the main entry point. Important helpers are `PrefetchBlobState::new()`, `process_prefetch_node()`, `dump_blob()`, `build_dump_bootstrap()`, `rewrite_blob_id()`, `update_ctx_from_bootstrap()`, `generate_prefetch_file_info()`, and `range_overlap()`.

### Control flow and state behavior
`generate_prefetch()` creates a new blob index at the end of the existing blob table, initializes a `PrefetchBlobState`, and processes each configured file. `process_prefetch_node()` finds the tree node, skips missing paths, filters chunks by optional ranges, reads compressed bytes from the backend using the original blob id and compressed offset, writes those bytes to the prefetch blob, and mutates each selected `NodeChunk` to the new blob index, chunk index, compressed/uncompressed offsets, and metadata. For v6 it also generates chunk-info metadata through `BatchContextGenerator`.

After all chunks are copied, `dump_blob()` appends the placeholder `prefetch-blob` info into the blob table, finalizes blob data/meta, calculates the real blob id, and rewrites the placeholder in the table. `build_dump_bootstrap()` rebuilds/dumps the bootstrap using the extended blob table and adjusts hardlink sibling chunk vectors in `bootstrap_ctx.inode_map` so hardlinks point to the rewritten chunks. `generate_prefetch_file_info()` reads a v1 JSON file and keeps only absolute paths.

### Dependencies and integration points
The module depends on `RafsBlobTable`, `RafsSuper`, `BlobBackend`, `BlobInfo`, `BlobContext`, `BlobManager`, `BootstrapManager`, `Bootstrap`, `Tree`, and shared finalization from `lib.rs`. It consumes backend readers for source blob bytes and writes output through `ArtifactWriter`. `update_ctx_from_bootstrap()` initializes build context from an existing bootstrap before optimization.

### Risks and edge cases
`process_prefetch_node()` uses `expect()` on backend `get_reader()` and `read()`, so backend failures can panic instead of returning `Result`. The `encrypted` variable is derived from `blob_compressor != None`, which looks suspiciously named and may not reflect encryption state. `range_overlap()` treats touching boundaries as overlap because it uses `<=`; for half-open byte ranges this includes zero-byte intersection at edges. The prefetch blob placeholder must be rewritten exactly once; duplicate placeholder ids assert. Context `ctx.blob_id` is temporarily cleared and restored, which is stateful.

### Test signals
Tests cover JSON parsing for empty, invalid, unsupported, absolute, and relative inputs; zero-sized struct; clone behavior; range overlap cases including boundary-touch behavior; and blob id rewriting for matching, nonmatching, and multiple entries. There is no direct unit test for `process_prefetch_node()` backend IO or full `generate_prefetch()` output.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/optimize_prefetch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/stargz.rs -->
## sources/cloud-native/nydus/builder/src/stargz.rs

### Purpose
`stargz.rs` implements `StargzBuilder`, which builds a RAFS v6 bootstrap from an eStargz TOC while reusing the stargz/tar gzip layer as the data blob. It parses TOC entries, builds a tree, converts eStargz chunk records into RAFS chunk metadata, handles symlinks, hardlinks, xattrs, and then emits bootstrap/blob metadata without rewriting original layer payload bytes.

### Important APIs, types, and functions
`TocEntry` models eStargz JSON entries, including path/type, size, link target, mode/uid/gid, device numbers, xattrs, digests, compressed offsets, chunk offsets/sizes, and inner offset. It exposes type predicates, `is_supported()`, `has_xattr()`, `mode()`, `rdev()`, `size()`, `name()`, `path()`, link helpers, `block_id()`, and `normalize()`. `TocIndex::load()` reads and normalizes a version-1 TOC.

`StargzBuilder` stores blob size, a `TarBuilder`, `file_chunk_map`, `hardlink_map`, and running uncompressed offset. Key methods are `new()`, `build_tree()`, `get_content_size()`, `parse_entry()`, `sort_and_validate_chunks()`, `fix_chunk_info()`, `fix_nodes()`, and `Builder::build()`.

### Control flow and state behavior
`build()` validates v6, gzip compression, and sha256 digester, creates writers/context, builds a tree from the TOC, runs shared `build_bootstrap()`, fixes chunk info and nodes, dumps blob metadata, and then finalizes bootstrap/blob in inline or separate order. `build_tree()` loads TOC entries, skips unsupported/special eStargz entries, derives chunk sizes from regular/chunk records, creates `NodeChunk`s with compressed offsets and chunk digests, tracks uncompressed offsets with optional 4 KiB alignment, parses non-chunk entries into nodes, then validates each file's chunk list.

`parse_entry()` creates `Node` objects directly from TOC metadata. It resolves hardlink targets already present in the tree, records hardlink node references, decodes base64 xattrs, sets symlink target and flags, and inserts the node through `TarBuilder`. `fix_chunk_info()` sorts all chunks by uncompressed offset, computes compressed sizes from adjacent compressed offsets or blob size using gzip-size estimation, allocates chunk indices, records blob metadata, and updates blob sizes. `fix_nodes()` copies chunk lists and sizes from `file_chunk_map` into tree nodes and mirrors target chunks/xattrs into hardlink nodes.

### Dependencies and integration points
The module integrates `TarBuilder`, `Tree`, `Node`, `NodeInfo`, `NodeChunk`, common `build_bootstrap/dump_bootstrap/finalize_blob`, `Blob`, `BlobManager`, and `BootstrapManager`. It depends on eStargz TOC JSON via `serde`, base64 xattrs, gzip compression helpers, RAFS v6 inode/chunk types, and Nydus blob limits. It is exported from `lib.rs` as `StargzBuilder`.

### Risks and edge cases
Hardlinks require target entries to appear earlier in the TOC; missing or non-regular targets fail. Chunk alignment and size validation are strict and assume chunk offsets align to `ctx.chunk_size`. The chunk validation loop uses `0..chunks.len() - 2`, which may skip checking the final adjacent pair for files with multiple chunks; the final size check catches some but not all hole/overlap patterns. `fix_chunk_info()` assumes compressed offsets are globally increasing after sorting by uncompressed offset. Unsupported char/block/fifo entries are warned and skipped even though `TocEntry` can model them. Only RAFS v6 + gzip + sha256 is accepted.

### Test signals
Tests cover building from a fixture eStargz TOC, expected blob id/blob size/bootstrap path, `TocEntry` type predicates/mode/rdev/name/block id/normalize behavior, and block digest/normalize error paths. The tests give good parser coverage and one integration path, but do not deeply test hardlink ordering failures, multi-chunk hole detection, unsupported special entries, or compressed-size boundary errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/builder/src/stargz.rs -->
