# sources/cloud-native/nydus/builder/src/core/tree.rs

## Purpose
`tree.rs` defines the in-memory filesystem topology used by the builder. A `Tree` wraps a `TreeNode` (`Rc<RefCell<Node>>`), caches the base name for sorted lookup, and owns children. It also loads trees from existing RAFS bootstraps and applies upper-layer changes to lower-layer trees using overlay whiteout rules.

## Important APIs, types, and functions
`Tree::new()` wraps a `Node`. `from_bootstrap()` loads a root inode from `RafsSuper`, parses it into `Node`, then recursively loads children through `MetadataTreeBuilder`. Traversal helpers include `walk_dfs()`, `walk_dfs_pre()`, `walk_dfs_post()`, and `walk_bfs()`. Mutation and lookup helpers include `insert_child()`, `get_child_idx()`, `get_node()`, `get_node_mut()`, `set_node()`, and `borrow_mut_node()`.

`merge_overaly()` replaces the root node with the upper root and calls `merge_children()`. `merge_children()` first applies whiteout markers (`OciRemoval`, `OciOpaque`, `OverlayFsRemoval`, `OverlayFsOpaque`) and then applies non-whiteout additions/modifications. `MetadataTreeBuilder::load_children()` recursively reads child inodes and chunk metadata from a bootstrap, and `parse_node()` converts `RafsInodeExt` into `Node` with chunks, symlink data, xattrs, and lower-layer overlay state.

## Control flow, state, and persistence
Tree children are kept sorted by byte name; insertions use binary search and path lookup depends on this invariant. DFS is used for digest/layout passes; BFS is used where RAFS/EROFS layout or output order needs breadth-first traversal. During merge, whiteouts are processed before real upper nodes so deletion/opacity affects the lower child list before replacements and additions occur.

When loading from bootstrap, regular-file chunks are added to the caller-provided `ChunkDict` using the blob digester. This seeds deduplication against parent or dictionary data. Parsed nodes use source `/`, target derived from bootstrap path, `Overlay::Lower`, invalid source device to avoid hardlink confusion, and `ChunkSource::Parent` for chunks.

## Dependencies and integration points
`tree.rs` depends on `node.rs`, `overlay.rs`, `nydus_rafs` metadata readers, RAFS xattr helpers, and builder `ChunkDict`. It is central to `Bootstrap::new/build/dump`, `DirectoryBuilder`, `StargzBuilder`, `TarBuilder`, `Merger`, and `OptimizePrefetch`. `overlay.rs` supplies the whiteout classification, while `v5.rs`/`v6.rs` consume the resulting tree for serialization.

## Risks and test signals
The function name `merge_overaly` is misspelled but used consistently. Path lookup assumes absolute paths with root plus normal components. `insert_child()` ignores duplicate child names, so replacement must use `set_node()` paths. Tests cover creation, node replacement, BFS traversal counts/error propagation, sorted insertion, and child lookup; merger/builder tests cover bootstrap loading and overlay behavior indirectly.
