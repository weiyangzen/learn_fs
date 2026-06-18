# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/syncop-utils.h

Purpose: `syncop-utils.h` declares higher-level synchronous traversal and lookup helpers built on the syncop framework.

Important APIs and types: `syncop_dir_scan_fn_t` is a callback for directory entries. APIs include `syncop_ftw`, `syncop_mt_dir_scan`, `syncop_dir_scan`, `syncop_dirfd`, `syncop_is_subvol_local`, `syncop_gfid_to_path`, throttled file-tree walk, inode find, and hard/soft GFID-to-path resolution.

Control flow and state: these helpers issue syncop fops against a subvolume and invoke caller callbacks for directory entries or path resolution. `syncop_mt_dir_scan` adds bounded parallelism via `max_jobs` and `max_qlen`.

Dependencies and integration: depends on `xlator_t`, `call_frame_t`, `loc_t`, `gf_dirent_t`, `inode_table_t`, dictionaries, and syncop primitives. Used by heal, rebalance, quota, or management code needing blocking traversal semantics.

Risks: traversal callbacks can mutate state and need clear ownership of `gf_dirent_t` and loc data. Multi-threaded scans risk queue growth and callback reentrancy. GFID-to-path hard resolution can be expensive and must handle stale inode state.

Test signals: directory traversal over empty/deep/wide trees, callback error propagation, throttling sleep/count behavior, local-subvol detection, GFID lookup misses, and queue bounds for multi-threaded scan should be verified.
