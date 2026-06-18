# sources/cloud-native/nydus/builder/src/core/prefetch.rs

## Purpose
`prefetch.rs` manages filesystem/blob prefetch configuration for the builder. It parses prefetch path patterns, tracks which tree nodes match those patterns, orders selected regular files near the front of blob layout, and emits RAFS v5/v6 prefetch tables for filesystem-level prefetch.

## Important APIs, types, and functions
`PrefetchPolicy` supports `None`, `Fs`, and `Blob` and is parsed from strings. `Prefetch` stores the policy, a disabled flag, an ordered `IndexMap<PathBuf, Option<TreeNode>>` of patterns, a list of prefetch regular files tagged by pattern index, and a BFS-ordered non-prefetch node list. `Prefetch::new()` reads path patterns from stdin unless policy is `None`. `generate_patterns()` normalizes user input by requiring absolute paths and dropping redundant child paths already covered by an earlier parent pattern.

`Prefetch::insert()` classifies a tree node against exact or parent-directory pattern matches. `get_file_nodes()` returns prefetch files sorted by pattern order plus non-prefetch files in traversal order. `fs_prefetch_rule_count()` counts matched filesystem prefetch patterns. `get_v5_prefetch_table()` emits inode numbers, while `get_v6_prefetch_table(meta_addr)` emits calculated v6 nids based on `node.v6_offset` and the final metadata address. `disable()` and `clear()` control transient state.

## Control flow, state, and persistence
The normal flow is: construct `Prefetch`, traverse the tree, call `insert()` for each node, then use `get_file_nodes()` to affect blob write order and call version-specific table generation during bootstrap dumping. `insert()` stores exact matched nodes in the pattern table only for exact path hits, but it marks regular files under matched directories as prefetch files using the parent pattern index. Empty regular files and disabled/no-policy cases go to non-prefetch.

State is in-memory only until bootstrap dumping. For v5, selected pattern nodes are persisted as inode numbers in `RafsV5PrefetchTable`. For v6, table entries are nids; this depends on v6 layout having already assigned and possibly adjusted `v6_offset`, so `v6.rs` intentionally asks for the v6 prefetch table after node dump offsets are finalized.

## Dependencies and integration points
The module uses `indexmap` to preserve user pattern order and RAFS layout table types from `nydus_rafs`. It integrates with tree traversal/build order and bootstrap dumping in `v5.rs` and `v6.rs`. `DirectoryBuilder` resets prefetch to `None` for the separate external-tree build. Blob-level prefetch is represented by policy but its physical optimization is handled elsewhere, notably `optimize_prefetch.rs`.

## Risks and test signals
Reading patterns directly from stdin means builder invocations using `Fs` policy can block if no input is piped. Parent coverage pruning is order-sensitive. `get_v5_prefetch_table()` and `get_v6_prefetch_table()` assert ids fit in `u32`. Tests cover pattern generation, policy parsing, insertion/classification, ordering, rule counts, and clearing; they do not serialize actual prefetch table bytes.
