# sources/distributed-fs/ceph-client/fs/zonefs/sysfs.c

## Purpose
`zonefs/sysfs.c` exposes per-mounted-zonefs counters under the global `fs/zonefs` sysfs directory.

## Important APIs, types, and functions
Public functions are `zonefs_sysfs_register`, `zonefs_sysfs_unregister`, `zonefs_sysfs_init`, and `zonefs_sysfs_exit`. The read-only attributes are `max_wro_seq_files`, `nr_wro_seq_files`, `max_active_seq_files`, and `nr_active_seq_files`.

## Control flow
Module init creates the global `zonefs` kobject under `fs_kobj`. Mount registration names the superblock, initializes a per-superblock kobject with the attribute group, and records registration success. Unmount deletes and puts the kobject and waits for release completion. Attribute reads recover `zonefs_sb_info` from the kobject and emit stored limits or atomic counters.

## State and persistence
Sysfs state is runtime-only. It mirrors open and active sequential file accounting from `zonefs_sb_info` and disappears on unmount or module exit.

## Dependencies and integration points
It depends on kobjects, sysfs attributes, superblock sysfs naming, completions, atomics, and zonefs mount state. It is called from zonefs module init/exit and fill/kill super.

## Risks and test signals
Risks include kobject lifetime races, double unregister, missing release completion after failed init, and stale counter reads during concurrent file open/close. Test signals include mount/unmount loops, failed sysfs registration injection, concurrent reads while closing files, and module unload with mounted filesystems rejected elsewhere.
