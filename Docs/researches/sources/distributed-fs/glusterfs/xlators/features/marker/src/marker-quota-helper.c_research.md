# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota-helper.c

## Purpose
`marker-quota-helper.c` owns helper routines for quota inode contexts, contribution nodes, and loc reconstruction. These utilities support the quota transaction engine in `marker-quota.c`.

## Important APIs, Types, And Functions
Key APIs are `mq_loc_fill`, `mq_inode_loc_fill`, `mq_alloc_inode_ctx`, `mq_contri_init`, `mq_get_contribution_node`, `mq_add_new_contribution_node`, `mq_dict_set_contribution`, `mq_inode_ctx_get`, and `mq_inode_ctx_new`. Internals include `mq_contri_fini` and `__mq_add_new_contribution_node`.

## Control Flow
`mq_inode_loc_fill` resolves an inode's parent and path, fills a `loc_t`, and ensures a quota context exists. Root inodes are handled without a parent. `mq_alloc_inode_ctx` initializes quota totals, dirty/update flags, a lock, and an empty contribution list. `mq_contri_init` creates refcounted contribution nodes keyed by a parent inode gfid. `mq_add_new_contribution_node` skips root paths, locks the quota context, finds or creates a contribution node for the current parent, and returns a ref. `mq_dict_set_contribution` builds the correct trusted quota contribution xattr key, including volume-version suffixes through `GET_CONTRI_KEY`.

## State And Persistence Behavior
In-memory state lives in `quota_inode_ctx_t` under `marker_inode_ctx_t->quota_ctx`; it tracks size, file count, directory count, dirty status, update/create status, and a list of `inode_contribution_t` entries. Persistent state is addressed by trusted xattr keys built here, but actual reads/writes are performed in `marker-quota.c`.

## Dependencies And Integration Points
This file depends on inode tables, path resolution, marker common context helpers, quota key macros from `marker-quota.h`, GlusterFS refcounts, and memory accounting. `marker-quota.c` relies on these helpers before every quota xattr transaction.

## Risks And Test Signals
Parent resolution is a fragile area for hard links, root entries, and stale inodes. Contribution nodes are refcounted and also list-linked, so missing `GF_REF_PUT` or failing to delete from lists can leak or use freed nodes. Tests should cover root, nameless lookups, hard-link parents, repeated contribution insertion, context racing, and long key generation near `QUOTA_KEY_MAX`.
