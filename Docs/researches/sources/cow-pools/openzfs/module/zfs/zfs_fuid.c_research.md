# File Research: sources/cow-pools/openzfs/module/zfs/zfs_fuid.c

## Summary
Implements ZFS FUID domain tables and ID translation support. It maps domain/RID identities to compact filesystem IDs, persists domain tables, and supports ACL/owner/group logging.

## Main Responsibilities
- Loads packed FUID domain tables from disk into AVL trees.
- Maintains AVL trees keyed by domain string and index.
- Syncs dirty FUID tables back to a packed nvlist object.
- Allocates new domain indexes when adding FUIDs.
- Maps FUIDs back to platform IDs.
- Tracks FUID domains and IDs created during ACL or ownership changes.
- Supports replay-time FUID reconstruction.
- Holds transaction reservations for FUID table updates.

## Key APIs
- `zfs_fuid_avl_tree_create()`
- `zfs_fuid_table_load()`
- `zfs_fuid_table_destroy()`
- `zfs_fuid_idx_domain()`
- Kernel APIs: `zfs_fuid_sync()`, `zfs_fuid_find_by_idx()`, `zfs_fuid_map_ids()`, `zfs_fuid_map_id()`, `zfs_fuid_node_add()`, `zfs_fuid_create()`, `zfs_fuid_destroy()`, `zfs_fuid_info_alloc()`, `zfs_fuid_info_free()`, `zfs_groupmember()`, `zfs_fuid_txhold()`, `zfs_id_to_fuidstr()`

## Important Behavior
The on-disk FUID table is a packed nvlist containing an array of domain records with index, domain, and offset. Loading creates two AVL indexes over the same `fuid_domain_t` nodes.

Domain index zero is the empty domain and represents ordinary POSIX IDs. New nonempty domains are added only when `addok` is true, marking `z_fuid_dirty` for later sync.

On Linux, FUID mapping is simplified: the port only supports POSIX IDs and returns the passed ID. Other platforms can use SID/kidmap support.

## State and Synchronization
Kernel state is guarded by `z_fuid_lock`. FUID tables are lazily loaded into `zfsvfs`, never remove nodes while active, and are destroyed at filesystem teardown. Temporary `zfs_fuid_info_t` structures own lists of domains and FUID log entries.

## Risks
Replay paths depend on logged FUID info matching the operations being replayed. Domain AVL nodes share ownership between two trees, so destruction releases domains from one traversal and frees nodes from the other. Non-Linux ID mapping behavior depends on platform SID/kidmap availability.
