# sources/distributed-fs/glusterfs/xlators/features/simple-quota/src/simple-quota.h

Purpose: declares private state used by the simple-quota translator.

Important types: `sq_private_t` contains a translator lock, an unused/thread placeholder `quota_set_thread`, the `ns_list` of namespace quota contexts, and booleans controlling distribute/backend behavior, command acceptance, and fop allowance. `sq_inode_t` is stored in inode context; it links into the private list, points to the namespace inode, tracks atomic pending updates, xattr-backed size, hard limit, total size, and backend file-count usage.

Control flow/state: the C implementation allocates `sq_inode_t` on lookup/setxattr/statfs paths, attaches it to an inode, and links it into `sq_private_t.ns_list` for later flush. `pending_update` is the hot update path; `xattr_size` is the last persisted base. `hard_lim` controls enforcement, and `total_size` is used for statfs/check comparisons.

Dependencies/integration: relies on GlusterFS `gf_lock_t`, `list_head`, `inode_t`, and `gf_atomic_t` definitions from included project headers. It is intentionally not a public library header; it is consumed by `simple-quota.c`.

Risks/test signals: ownership of `ns` is subtle because the struct stores raw inode pointers while fops also take refs in `frame->local`. Tests should look for forget/flush races, list integrity, and correct pending_update behavior after failures.
