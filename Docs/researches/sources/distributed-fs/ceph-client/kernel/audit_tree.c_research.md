# sources/distributed-fs/ceph-client/kernel/audit_tree.c

## Purpose
`audit_tree.c` implements recursive directory audit watches. It tracks audit rules bound to directory trees by tagging all relevant mount path inodes with fsnotify marks and maintaining an RCU-visible mapping from inodes to `audit_chunk` ownership records. It supports trimming stale tags, mount equivalence updates, asynchronous pruning, and delayed tree killing during syscall audit processing.

## Important APIs, types, and functions
`struct audit_tree` represents a watched path, rule list, tagged chunks, root chunk, same-root links, goner state, refcount, and pathname. `struct audit_chunk` represents one inode mark and a variable set of owning trees through embedded `audit_node` entries. `struct audit_tree_mark` embeds `fsnotify_mark` and points to the active chunk. Global state includes `tree_list`, `prune_list`, `prune_thread`, `audit_tree_group`, a mark slab cache, a 128-bucket chunk hash table, and `hash_lock`.

External APIs include `audit_make_tree()`, `audit_add_tree_rule()`, `audit_remove_tree_rule()`, `audit_trim_trees()`, `audit_tag_tree()`, `audit_tree_lookup()`, `audit_tree_match()`, `audit_put_chunk()`, `audit_tree_path()`, `audit_put_tree()`, and `audit_kill_trees()`.

## Control flow
Rule parsing creates a temporary tree with `audit_make_tree()`. Rule insertion under `audit_filter_mutex` calls `audit_add_tree_rule()`, which reuses an existing tree with the same path or adds a new tree, launches the prune thread if needed, resolves the path, collects related mount paths, and tags each inode through `tag_chunk()`. Tagging either creates a new mark/chunk or replaces an existing chunk with a larger owner set. Once tagging succeeds, temporary high-bit markers in `audit_node.index` are cleared and the rule is attached to the tree.

Removal via `audit_remove_tree_rule()` detaches the rule. If it was the last rule on a tree, the tree is marked goner, moved to `prune_list`, and the prune thread later calls `prune_one()` to untag chunks and drop references. `audit_trim_trees()` recomputes which collected paths still belong to each tree and prunes uncommitted/stale chunks. `audit_tag_tree(old,new)` handles mount equivalence by tagging trees under an old path with inodes collected from a new path. Fsnotify mark freeing calls `audit_tree_freeing_mark()`, which detaches the mark's chunk, evicts root-owning trees, and schedules or postpones pruning.

## State and persistence behavior
The watched tree rules are in audit filter lists; tree/chunk/mark state is in-memory. RCU readers in syscall audit can call `audit_tree_lookup()` on inodes and later match chunks to trees without taking the heavy filter mutex. Refcounts on trees and chunks maintain lifetime across RCU and fsnotify callbacks. No on-disk persistence is provided; userspace must reload audit rules after boot.

## Dependencies and integration points
This file depends on fsnotify internals, VFS path resolution, mount path collection, kthreads, audit rule/filter locking, RCU, spinlocks, refcounts, syscall audit tree reference collection, and audit config logging. It cooperates with `auditfilter.c` for rule insertion/removal and `auditsc.c` for `audit_killed_trees()` and inode filtering.

## Risks and invariants
The data structure is concurrency-heavy. Chunk replacement must fully initialize new chunks before RCU publication; comments explicitly pair `smp_wmb()` with data dependency reads. `hash_lock` and `audit_tree_group` mark mutex together stabilize mark-to-chunk associations. The high bit of `audit_node.index` is used as a temporary prune marker and must be preserved/cleared correctly. Error cleanup during partial tagging is complex and must not leave rules referencing goner trees or leaked chunk references.

## Test signals
Exercise recursive directory audit rules across mount points, bind mounts, path equivalence updates, deletion/unmount of watched roots, concurrent rule removal during tagging, trim operations, and syscall audit matching under rename/unmount churn. Lockdep, KCSAN, RCU stall detection, and allocation-failure injection are high-value for this file.
