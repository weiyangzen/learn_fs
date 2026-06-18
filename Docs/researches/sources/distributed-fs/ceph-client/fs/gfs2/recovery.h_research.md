<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/recovery.h -->
# sources/distributed-fs/ceph-client/fs/gfs2/recovery.h

## Purpose
`recovery.h` declares GFS2 journal recovery and replay helpers shared by recovery, lops, mount, sysfs, and lock-manager code.

## Important APIs, types, and functions
It declares the global `gfs2_recovery_wq`, inline `gfs2_replay_incr_blk`, block read helper `gfs2_replay_read_block`, revoke replay helpers, `gfs2_recover_journal`, worker `gfs2_recover_func`, log header parser `__get_log_header`, and `gfs2_log_pointers_init`.

## Control Flow
The inline `gfs2_replay_incr_blk` advances a journal block number and wraps to zero at `jd_blocks`. Recovery code uses it when scanning descriptors, payload blocks, and writing clean headers. Other declarations support queuing recovery work, waiting for completion, parsing journal headers, and initializing local log pointers after replay.

## State and Persistence
The header itself stores no state. Its APIs operate on `gfs2_jdesc` replay lists, journal block positions, log header host structures, and superblock log pointers.

## Dependencies and Integration Points
Includes `incore.h` for GFS2 core structures. `lops.c` uses revoke and replay block helpers; `ops_fstype.c` and sysfs code call `gfs2_recover_journal`; `lock_dlm.c` receives recovery results indirectly through lock operations; `main.c` allocates the declared recovery workqueue.

## Risks
The wraparound helper is tiny but central; incorrect journal block advancement would corrupt replay boundaries. Callers must respect `JDF_RECOVERY` serialization in `gfs2_recover_journal` and must not parse untrusted log headers without checking the return value from `__get_log_header`.

## Test Signals
Compile coverage, journal wraparound replay, asynchronous and synchronous recovery callers, log header validation tests, and recovery workqueue lifetime across module load/unload are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/recovery.h -->
