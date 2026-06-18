## sources/distributed-fs/ceph-client/fs/gfs2/incore.h

### Purpose
`incore.h` is the central definition file for GFS2 in-memory state. It defines host-side versions of log, bitmap, resource-group, glock, holder, inode, quota, transaction, journal, mount-argument, lockspace, superblock, statfs, and tuning structures used by the implementation.

### Important APIs, Types, and Functions
Important structures include `gfs2_log_header_host`, `gfs2_log_operations`, `gfs2_bitmap`, `gfs2_rgrpd`, `gfs2_bufdata`, `lm_lockname`, `gfs2_glock_operations`, `gfs2_holder`, `gfs2_qadata`, `gfs2_blkreserv`, `gfs2_alloc_parms`, `gfs2_glock`, `gfs2_inode`, `gfs2_file`, `gfs2_quota_data`, `gfs2_trans`, `gfs2_jdesc`, `gfs2_args`, `gfs2_tune`, `lm_lockstruct`, and `gfs2_sbd`. Inline helpers include `GFS2_I`, `GFS2_SB`, `glock_type`, `glock_number`, `gfs2_aspace`, `gfs2_glstats_inc`, `gfs2_sbstats_inc`, and `gfs2_max_stuffed_size`.

### Control Flow
The header itself has only inline helper flow. Its real role is data-flow: glock state in `struct gfs2_glock` drives `glock.c`; `struct gfs2_inode` ties VFS inodes to inode and iopen glocks, quota data, reservations, and disk metadata; `struct gfs2_sbd` aggregates mount-wide constants, lockspace state, journal state, workqueues, statfs, resource groups, quota state, and debugfs state.

### State and Persistence Behavior
The file separates in-core-only state from disk-backed or journal-mediated state. Resource-group clone bitmaps are explicitly in-core and prevent freed blocks from being reallocated in the same transaction. `gfs2_bufdata` tracks buffers through transactions and AIL lists. `gfs2_trans` records transaction block/revoke reservations and buffer lists. `gfs2_inode` caches dinode fields such as address, generation, xattr block, disk flags, height/depth, entries, and allocation goal. `gfs2_sbd` tracks log heads/tails, in-flight log I/O, AIL lists, local and master statfs deltas, quota bitmaps, rgrp indexes, journal descriptors, and filesystem lifecycle flags.

### Dependencies and Integration Points
Nearly every GFS2 source includes `incore.h`. It integrates Linux `super_block`, `inode`, `address_space`, `buffer_head`, workqueues, completions, rhashtable, lockref, DLM lockspace, per-cpu stats, rbtrees, and kobjects with GFS2-specific on-disk structures from `linux/gfs2_ondisk.h`.

### Risks and Edge Cases
Structure layout and flag semantics are high impact. `lm_lockname` is used as an rhashtable key and intentionally avoids interior holes. Bit numbers in `GLF_*`, `HIF_*`, `SDF_*`, and other enums are shared across asynchronous code; changing them incorrectly breaks waits and state transitions. `gfs2_sbd` has many fields with different locking disciplines, so readers must respect the owning locks described by call sites. In-core clone bitmap behavior is essential for transaction allocation correctness.

### Test Signals
Coverage comes from broad filesystem testing: mount/unmount, DLM recovery, journal replay, allocation/free stress, quota accounting, statfs sync, glock stats/debugfs, memory pressure, and transaction abort/withdraw tests. Static analysis can catch struct field misuse, but most risks need concurrency and fault-injection tests.
