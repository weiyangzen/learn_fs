# sources/distributed-fs/ceph-client/fs/jffs2/readinode.c

## Purpose

`readinode.c` reconstructs a live JFFS2 inode from raw node references discovered during mount/scan. It reads all non-obsolete nodes for an inode, validates headers and data as needed, resolves overlapping data nodes by version, builds the final fragment tree, reconstructs directory entries and metadata nodes, caches symlink targets, and clears inode state on eviction or CRC-check passes.

## Important APIs, Types, And Functions

The exported functions are `jffs2_do_read_inode()`, `jffs2_do_crccheck_inode()`, and `jffs2_do_clear_inode()`. Internal helpers include `check_node_data()`, `check_tn_node()`, `jffs2_add_tn_to_tree()`, `jffs2_build_inode_fragtree()`, `read_direntry()`, `read_dnode()`, `read_unknown()`, `read_more()`, `jffs2_get_inode_nodes()`, and `jffs2_do_read_inode_internal()`.

The central transient state is `struct jffs2_readinode_info`, which holds a temporary dnode rbtree, directory-entry list, metadata candidate, highest version, latest valid raw ref, and latest directory mctime. Temporary data nodes are represented as `struct jffs2_tmp_dnode_info`, while final state is stored in `f->fragtree`, `f->metadata`, `f->dents`, and `f->target`.

## Control Flow

`jffs2_do_read_inode()` locates the inode cache under `inocache_lock`, transitions unchecked/absent state to `INO_STATE_READING`, waits if the inode is checking or in GC, and creates a root inode cache if inode 1 is missing. It then delegates to `jffs2_do_read_inode_internal()`.

The internal read first calls `jffs2_get_inode_nodes()`. That function walks the inode's raw-ref chain while carefully choosing the next non-obsolete ref before dropping `erase_completion_lock`, because obsolete refs may disappear after erase. It reads enough bytes for the node header, expanding reads to write-buffer page boundaries when useful, validates header CRC and magic, and dispatches to dirent, inode, or unknown-node handling.

`read_dnode()` validates raw inode node CRCs, performs partial data CRC precomputation for unchecked write-buffered nodes, accounts zero-length unchecked nodes immediately, constructs a temporary dnode, and inserts it into the temporary rbtree. `jffs2_add_tn_to_tree()` discards fully overlapped older nodes when newer nodes pass CRC checks, handles version collisions, records overlap markers, and preserves metadata-only zero-size nodes separately.

`jffs2_build_inode_fragtree()` consumes the temporary rbtree from the end, groups overlapping nodes into a version-ordered tree, checks only nodes that survive overlap resolution, and calls `jffs2_add_full_dnode_to_inode()` for valid data. Finally `jffs2_do_read_inode_internal()` reads the latest raw inode header, validates its CRC, applies inode-type-specific fixups, truncates regular-file fragments to `isize`, caches symlink targets, and converts special-file data into `f->metadata`.

## State And Persistence Behavior

This file changes in-core inode state and also changes flash/accounting state for nodes whose CRCs fail or whose unchecked status is resolved. `check_node_data()` moves bytes from unchecked to used and marks refs `REF_PRISTINE`; bad nodes are marked obsolete through `jffs2_mark_node_obsolete()`. Dirent reads similarly move unchecked dirents to used and set `dirent_node_state(rd)`.

For symlinks, the target payload is read from flash and cached in `f->target`. On clear, `jffs2_do_clear_inode()` deletes xattrs, marks metadata and fragment nodes obsolete if the inode is deleted, frees dirents, kills the fragment tree, and returns the inode cache to `INO_STATE_CHECKEDABSENT` or removes it if empty.

## Dependencies And Integration Points

The code depends on flash reads, CRC32, write-buffer page sizing, rbtree helpers, node-ref accounting, inode-cache state management, xattr CRC/delete hooks, fragment tree manipulation, and VFS inode mode semantics. It is invoked from Linux inode instantiation (`jffs2_iget()` in other files), GC CRC-checking, and eviction.

## Risks And Edge Cases

This is one of the highest-risk correctness files. Overlap resolution must avoid trusting obsolete or corrupt newer nodes while not retaining old data hidden by valid newer data. The code intentionally defers full data CRC checks for unchecked write-buffered nodes to avoid checking nodes that will later be discarded. Raw refs can disappear when obsolete blocks are erased, so lock dropping around ref traversal is delicate. Special inodes must have exactly one data fragment; otherwise errors are returned. Missing latest refs are tolerated only for root or directories with children, where fake metadata is constructed.

## Test Signals

High-value tests include overlapping writes with increasing versions, version collisions from GC, corrupt data in newer versus older nodes, unchecked NAND nodes, corrupt dirent names, unknown feature-node compatibility classes, symlink target caching, regular-file truncation to latest `isize`, special-file metadata conversion, concurrent read/clear/GC states, and CRC-check-only inode passes. Fault injection for MTD short reads and allocation failures should verify cleanup of temporary rbtrees and dirent lists.
