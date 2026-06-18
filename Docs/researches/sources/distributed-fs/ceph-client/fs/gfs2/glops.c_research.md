## sources/distributed-fs/ceph-client/fs/gfs2/glops.c

### Purpose
`glops.c` defines the per-glock-type policy hooks used by the generic glock engine. It decides how inode and resource-group glocks sync dirty metadata, invalidate caches, instantiate in-core objects from disk, react to freeze and iopen callbacks, and expose debug details.

### Important APIs, Types, and Functions
The externally visible functions and data are `gfs2_ail_flush`, `gfs2_inode_metasync`, `gfs2_glock2rgrp`, `gfs2_freeze_wq`, the glock operation tables (`gfs2_meta_glops`, `gfs2_inode_glops`, `gfs2_rgrp_glops`, `gfs2_freeze_glops`, `gfs2_iopen_glops`, `gfs2_flock_glops`, `gfs2_nondisk_glops`, `gfs2_quota_glops`, `gfs2_journal_glops`), and `gfs2_glops_list`. Key static hooks include `rgrp_go_sync`, `rgrp_go_inval`, `inode_go_sync`, `inode_go_inval`, `inode_go_instantiate`, `inode_go_held`, `freeze_go_callback`, `freeze_go_xmote_bh`, and `iopen_go_callback`.

### Control Flow
AIL flushing starts with `gfs2_ail_flush` or `gfs2_ail_empty_gl`. The latter can create a revoke-only transaction to remove all buffers for a glock from the AIL, flush the log, and wait for revokes/log I/O. If unexpected dirty, pinned, or locked buffers remain outside fsync-tolerated paths, `gfs2_ail_error` logs details and withdraws the filesystem.

Resource-group demotion uses `rgrp_go_sync`: if the rgrp is dirty and held exclusive, flush the journal for that glock, write/wait metadata pages covering the rgrp blocks, empty the AIL, and free clone bitmaps. `rgrp_go_inval` releases rgrp buffers, asserts the AIL is empty, and truncates the metadata mapping range. Inode demotion is similar but also handles regular file data: `inode_go_sync` unmaps shared mappings for mmap-write pages, waits for direct I/O, flushes the log, writes metadata and data mappings, waits, empties AIL, and clears dirty state. `inode_go_inval` truncates glock metadata, refreshes instantiate requirements, invalidates ACL/security/dir-hash caches, marks rindex stale if needed, and truncates regular file page cache.

Instantiation uses `inode_go_instantiate` to refresh the dinode from disk through `gfs2_inode_refresh`; `gfs2_dinode_in` validates disk block identity, type stability, height/depth bounds, exhash constraints, stuffed size bounds, timestamps, block counts, disk flags, xattr pointers, and address-space operations. `inode_go_held` waits for direct I/O unless the holder requested deferred state and resumes interrupted truncation when the holder and glock are exclusive.

### State and Persistence Behavior
This file is the bridge between in-core glock state and durable storage. It flushes journals, writes metadata/data mappings, adds revokes, empties AIL lists, invalidates cache state when locks are demoted, and reloads dinodes when glocks are instantiated. Freeze hooks validate journal heads before resuming a live journal. Iopen callbacks schedule eviction when a remote node wants an iopen lock unlocked.

### Dependencies and Integration Points
`glops.c` depends on `glock.c` for hook invocation, `log`/`lops`/`trans` for journal and revoke mechanics, `meta_io` for dinode buffers, `rgrp` for resource-group state, `dir` for hash invalidation, `recovery` for journal-head reads, security and ACL APIs for cache invalidation, and Linux writeback/page-cache APIs. Operation table indices must match `LM_TYPE_*` values from `glock.h`.

### Risks and Edge Cases
The main risks are returning from demotion before data or metadata is durable, invalidating cache while dirty AIL entries remain, mishandling filesystem withdraw, stale rindex cache after metadata invalidation, and accepting corrupt dinode fields. Freeze callback paths are race-sensitive with unmount/remount because they try to take an active superblock reference.

### Test Signals
Useful tests include multi-node cache coherency under inode/rgrp demotion, journal replay and AIL revoke tests, fsync and truncate-in-progress recovery, freeze/thaw across cluster nodes, resource group allocation/free stress, dinode corruption detection, and remote unlink/iopen eviction behavior.
