## sources/distributed-fs/ceph-client/fs/orangefs/orangefs-mod.c

### Purpose
This file is the OrangeFS module entry point. It owns global module parameters, operation queues, filesystem registration, device/debugfs/sysfs initialization, and shutdown checks.

### Important APIs, types, and functions
- Globals include `orangefs_stats`, `hash_table_size`, `orangefs_gossip_debug_mask`, operation/slot/cache timeout parameters, `orangefs_request_mutex`, in-progress hash table, request list, locks, and waitqueue.
- `orangefs_fs_type` registers filesystem name `pvfs2`.
- `orangefs_init()` initializes op and inode caches, op hash table, fsid key table, debug help/debugfs/sysfs, request device, and filesystem registration with cleanup unwinds.
- `orangefs_exit()` unregisters the filesystem, cleans debugfs/sysfs/device/key/cache resources, asserts queues empty, and frees the hash table.
- `purge_inprogress_ops()` marks all in-progress operations purged when the daemon exits.

### Control flow
Module load normalizes negative timeout parameters to zero, sets up all global state before exposing the filesystem, then registers `/dev/pvfs2-req` and finally `pvfs2`. Failure unwinds in reverse order. Module exit unregisters first, then destroys observability/device/key/cache state. Device release calls `purge_inprogress_ops()` to wake operations that were already handed to the daemon.

### State and persistence behavior
All state is runtime kernel module state. Mounted superblocks and server data persist elsewhere, but daemon loss marks operations purged and superblocks pending remount through device release logic. Stats counters are volatile.

### Dependencies and integration points
Coordinates `orangefs-cache.c`, `super.c`, `orangefs-debugfs.c`, `orangefs-sysfs.c`, `devorangefs-req.c`, `waitqueue.c`, and VFS filesystem registration. Module parameters expose debug and timeout tuning.

### Risks
Initialization order matters because VFS calls can start after filesystem registration. Shutdown uses `BUG_ON()` if request lists are not empty, which makes leaked operations fatal. Hash table size is a module parameter with no explicit lower-bound validation, so invalid values could break hashing if set badly.

### Test signals
Test module load/unload repeatedly, failure injection at each init step, nondefault module parameters, daemon crash while operations are in progress, and queue-empty assertions after forced unmounts.
