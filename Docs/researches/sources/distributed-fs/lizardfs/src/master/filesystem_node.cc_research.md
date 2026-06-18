# sources/distributed-fs/lizardfs/src/master/filesystem_node.cc

## Purpose
`filesystem_node.cc` implements the low-level metadata invariants for filesystem nodes. It creates and destroys typed nodes, maintains directory entries, parent vectors, subtree statistics, quotas, chunks, ACLs, checksums, paths, detached trash/reserved state, permission checks, and recursive property changes.

## Important APIs and functions
Creation and ownership functions include `FSNode::create`, `FSNode::destroy`, `fsnodes_create_node`, `fsnodes_link`, `fsnodes_remove_edge`, `fsnodes_unlink`, `fsnodes_remove_node`, `fsnodes_purge`, and `fsnodes_undel`. Statistics and size helpers include `fsnodes_get_stats`, `fsnodes_add_stats`, `fsnodes_add_sub_stats`, file chunk/size/realsize helpers, and `fsnodes_get_size`. Directory and path APIs include `fsnodes_lookup`, `fsnodes_getpath_size`, `fsnodes_getpath_data`, `fsnodes_getdirsize`, legacy and current `fsnodes_getdir`, and detached trash/reserved listing helpers. Attribute and security APIs include `fsnodes_fill_attr`, `fsnodes_access`, `fsnodes_sticky_access`, `verify_session`, `fsnodes_get_node_for_operation`, ACL setters/getters/deleters, `fsnodes_namecheck`, and recursive goal/trashtime/eattr functions.

## Control flow and state behavior
Node creation allocates an inode, inherits goal/trash time/mode/eattrs from parent, optionally inherits RichACL/default ACL, inserts into the global node hash, updates checksums, links into the parent directory, propagates stats, and charges inode/file quota. Link and unlink paths update directory `entries_hash`, parent vectors, stats, nlink, timestamps, and checksums. Last unlink of a file moves it to trash if `trashtime > 0`, reserved if still open, or deletes it; purge moves trash to reserved when sessions remain or frees it fully. Length and append operations update chunk ownership, detached space counters, stats, quotas, and checksums.

## Dependencies and integration points
The file depends on chunk metadata, datacache invalidation, quota helpers, checksum helpers, metadata globals, periodic defective-node cleanup, FsContext/session flags, ACL storage, goals, tape server enqueueing, and personality assertions. Higher-level `filesystem_operations.cc` calls these primitives after validating protocol semantics.

## Risks and test signals
This is a high-risk invariant hub. Missed stat, quota, checksum, or parent-vector updates cause persistent metadata divergence. Tests should cover create/unlink/rename/link across directories, hard links, recursive stats after file size changes, quota deltas after chown and truncate, directory hash changes, ACL inheritance and equivalent-mode collapse, trash/reserved/undel/purge paths, session-scoped reserved deletion, permission checks with rootinode and meta sessions, current versus legacy readdir indexes, and chunk reference counts on append/truncate/delete.
