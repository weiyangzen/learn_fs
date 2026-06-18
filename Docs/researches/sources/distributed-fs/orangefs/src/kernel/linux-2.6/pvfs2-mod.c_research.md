# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-mod.c

## Purpose
`pvfs2-mod.c` is the load/unload entry point for the OrangeFS kernel module. It declares core globals, registers the VFS filesystem type, initializes caches, device communication, request tracking, fskey tracking, proc/sysctl controls, and tears all of them down on module exit.

## Important APIs and globals
Module parameters include `hash_table_size`, `module_parm_debug_mask`, `op_timeout_secs`, and `slot_timeout_secs`. Global synchronization and queues defined here include `devreq_semaphore`, `request_semaphore`, `htable_ops_in_progress`, `pvfs2_request_list`, `pvfs2_request_list_lock`, and `pvfs2_request_list_waitq`. `pvfs2_fs_type` binds the filesystem name `pvfs2` to mount/get_sb and kill_sb callbacks. `purge_inprogress_ops` marks active operations as purged after daemon shutdown.

## Control flow
`pvfs2_init` normalizes the module debug mask, builds the debug-help string, initializes optional backing-dev info, clamps negative timeouts to zero, creates all slab caches, initializes the device subsystem, initializes semaphores and the in-progress qhash table, initializes the fskey table, registers proc/sysctl entries, and finally registers the filesystem. Error labels unwind in reverse order. `pvfs2_exit` unregisters the filesystem and proc entries, finalizes fskey/device state, releases pending request-list ops, releases all qhash in-progress ops, destroys caches, finalizes qhash, destroys backing-dev info, and logs unload.

## State and persistence behavior
State is module-global and volatile. Operation hash buckets index in-progress operations by tag. The request list queues operations waiting for the daemon to read from `/dev/pvfs2-req`. Debug strings and masks persist until module unload or proc/ioctl changes.

## Dependencies and integration points
This file depends on cache routines in `pvfs2-cache.c`, proc routines in `pvfs2-proc.c`, fskey and mount helpers in `super.c`, device setup in `devpvfs2-req.c`, and debug conversion in `pvfs2-utils.c`. Device and waitqueue code depend on the globals defined here.

## Risks and edge cases
`purge_inprogress_ops` iterates `hash_table_size`, not the live `htable_ops_in_progress->table_size`; if qhash initialization adjusts size, iteration could diverge. Module exit releases in-progress operations without first synchronizing all possible waiters visible in this file, relying on teardown ordering elsewhere. Debug-help string construction manually tracks an index into a fixed 4096-byte buffer and checks individual keyword lengths, not total remaining capacity. Failure unwinding is dense and should be checked whenever a new subsystem is added.

## Test signals
Tests should cover module load with valid and invalid debug masks, negative timeout parameters, cache/device/qhash failure injection and unwind, filesystem registration failure, daemon-close purge waking waiters, module unload with queued and in-progress operations, and proc/sysctl availability after successful load.
