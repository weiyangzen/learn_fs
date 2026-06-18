# sources/distributed-fs/ceph-client/fs/jffs2/nodelist.c

## Purpose
`nodelist.c` implements core in-core node bookkeeping: directory entry replacement, fragment-tree mutation, inode-cache hash operations, raw-node-ref linking/freeing, dirty-space scanning, and raw-node total-length calculation. It is the main consistency layer between append-only flash nodes and current file/directory state.

## Important APIs, Types, And Functions
Key public functions are `jffs2_add_fd_to_list()`, `jffs2_truncate_fragtree()`, `jffs2_add_full_dnode_to_inode()`, `jffs2_set_inocache_state()`, `jffs2_get_ino_cache()`, `jffs2_add_ino_cache()`, `jffs2_del_ino_cache()`, `jffs2_free_ino_caches()`, `jffs2_free_raw_node_refs()`, `jffs2_lookup_node_frag()`, `jffs2_kill_fragtree()`, `jffs2_link_node_ref()`, `jffs2_scan_dirty_space()`, and `__jffs2_ref_totlen()`.

## Control Flow
Dirents are kept sorted by name hash; duplicate names are resolved by version, with obsolete raw nodes marked dirty. Fragment insertion handles non-overlap, holes, partial overlap, splitting, replacement, and total obsoletion, updating raw-ref flags from pristine to normal when GC must inspect shared pages. Inode-cache helpers maintain sorted per-bucket lists under `inocache_lock`. Raw-node refs are appended in physical order to eraseblock ref blocks and linked into inode caches.

## State And Persistence Behavior
This file mutates volatile state that mirrors persistent nodes: `f->dents`, `f->fragtree`, `fn->frags`, inode-cache lists/states, eraseblock `first_node`/`last_node`, node ref flags, and superblock/eraseblock used/dirty/free/unchecked counters. Marking obsolete changes JFFS2's logical persistence by invalidating older flash nodes.

## Dependencies And Integration Points
It depends on rbtrees, MTD geometry macros, CRC-related structures, debug checks, allocation wrappers from `malloc.c`, and obsolete marking/reservation functions from nodemgmt/write code. Readinode, write, dir, fs, erase, and GC all rely on these invariants.

## Risks And Test Signals
Fragment overlap logic is intricate and can lose data if split/replace cases mishandle sizes or ref counts. Raw-node refs must remain physically ordered for `ref_totlen()`. Tests should cover random overlapping writes/truncates, sparse holes, same-page node merging flags, dirent version replacement/deletion markers, inode-cache add/delete races, eraseblock ref-block chaining, and accounting sanity under scan and live writes.
