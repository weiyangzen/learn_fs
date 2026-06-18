<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/ops_fstype.c -->
# sources/distributed-fs/ceph-client/fs/gfs2/ops_fstype.c

## Purpose
`ops_fstype.c` implements GFS2 and GFS2 meta-filesystem mount, reconfigure, and kill-superblock operations. It allocates and initializes `struct gfs2_sbd`, parses mount options, joins the selected lock manager, reads and validates the on-disk superblock, initializes journals/statfs/rgrp/quota/per-node state, starts per-mount threads, and unwinds those resources on mount failure or unmount.

## Important APIs, types, and functions
External symbols include `free_sbd`, `gfs2_lm_unmount`, `gfs2_online_uevent`, `gfs2_destroy_threads`, `gfs2_fs_type`, and `gfs2meta_fs_type`. Major internal functions are `gfs2_tune_init`, `init_sbd`, `gfs2_check_sb`, `gfs2_sb_in`, `gfs2_read_super`, `gfs2_read_sb`, `init_names`, `init_locking`, `init_sb`, `gfs2_jindex_hold`, `init_statfs`, `init_journal`, `init_inodes`, `init_per_node`, `gfs2_lm_mount`, `wait_on_journal`, `init_threads`, `gfs2_fill_super`, `gfs2_get_tree`, `gfs2_parse_param`, `gfs2_reconfigure`, `gfs2_meta_get_tree`, `gfs2_evict_inodes`, and `gfs2_kill_sb`.

## Control Flow
Mount starts through fs-context parsing. `gfs2_init_fs_context` allocates default `gfs2_args`; `gfs2_parse_param` fills lock protocol/table/hostdata, spectator mode, ACL, quota, data mode, discard, barrier, error, commit, statfs, and quota timing options. `gfs2_get_tree` calls `get_tree_bdev`, which invokes `gfs2_fill_super`. Fill-super initializes `sdp`, applies spectator/read-only and feature flags, sets VFS operations, creates the metadata inode/address space, auto-detects lock names from the on-disk superblock if needed, creates per-mount workqueues/debugfs/sysfs, joins the lock manager, acquires nondisk mount/live/rename/freeze glocks, rereads the superblock under the superblock glock, waits for DLM journal id assignment when needed, initializes journals and hidden inodes, loads rgrps, initializes per-node quota-change inode state, starts `logd` and `quotad` for writable mounts, takes the freeze lock, and makes the filesystem writable if requested.

Journal initialization loads the `jindex` directory entries into `gfs2_jdesc` objects, validates the selected journal, maps its extents, initializes statfs inodes, and runs first-mount or local journal recovery. First mounter recovery replays or checks every journal and then calls `gfs2_others_may_mount`. Failure labels undo each initialized subsystem in reverse order. Reconfigure forbids changing cluster identity, hostdata, spectator mode, localflocks, or gfs2/meta role, allows read-only toggles through `gfs2_make_fs_ro/rw`, updates ACL/barrier/tuning flags, and emits an online uevent. The `gfs2meta` filesystem does not mount independently; it locates an existing GFS2 mount by block device and returns its master directory.

## State and Persistence
The file initializes most per-mount runtime state in `gfs2_sbd`: tune values, waitqueues, completions, glock stats, jindex list, quota list and bitmap controls, statfs state, log counters and AIL lists, journal descriptors, hidden inode dentries, workqueues, sysfs/debugfs state, and mount arguments. Persistent reads include the superblock, master/root inode numbers, jindex, statfs, per-node files, quota file, and rindex. Persistent writes can occur during journal recovery, statfs initialization/recovery, quota changes, and make-rw transitions.

## Dependencies and Integration Points
This file is the integration point between VFS/fs_context, block devices, locking (`lock_nolock` or `lock_dlm`), glocks, recovery, log, quota, statfs, rgrp, superblock operations, sysfs/debugfs, kthreads, freeze handling, export operations, quota control, and the hidden meta filesystem. `main.c` registers the `gfs2_fs_type` and `gfs2meta_fs_type` defined here.

## Risks
Mount ordering is fragile: locking must be live before trusted superblock reread, journal recovery needs statfs inodes, per-node quota files need a selected journal, and writable transition must happen after recovery. Failure unwind must not double-drop dentries, glocks, or workqueues. Spectator mounts are forced read-only and cannot perform first-mounter recovery. DLM journal-id assignment can be interrupted. Reconfigure must keep cluster identity immutable. `gfs2_kill_sb` flushes the log and uses cooperative inode eviction to avoid cluster iopen deadlocks.

## Test Signals
Signals include lock_nolock and lock_dlm mounts, missing or invalid locktable/protocol, spectator and meta mounts, first mounter and non-first mounter recovery, invalid superblock format/block size, no journals, bad selected journal id, mount failure injection at every initialization stage, remount ro/rw and tuning changes, disallowed reconfigure changes, quota/statfs/rgrp initialization, kill-superblock with unlinked inodes, and uevents for online and first-mount completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/gfs2/ops_fstype.c -->
