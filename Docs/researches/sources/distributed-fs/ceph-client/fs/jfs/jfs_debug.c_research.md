# sources/distributed-fs/ceph-client/fs/jfs/jfs_debug.c

## Purpose
Creates and removes optional `/proc/fs/jfs` debug/statistics entries.

## Important APIs, types, and functions
`jfs_loglevel_proc_show/open/write()` expose `jfsloglevel`. `jfs_proc_init()` creates optional `lmstats`, `txstats`, `xtstat`, `mpstat`, `TxAnchor`, and `loglevel`. `jfs_proc_clean()` removes the subtree.

## Control flow
When procfs plus debug/statistics are configured, initialization creates the proc directory and entries. Loglevel write accepts one ASCII digit and stores it in the global.

## State and persistence behavior
Runtime-only procfs state and `jfsloglevel`; no on-disk persistence.

## Dependencies and integration points
Depends on procfs, seq_file, user copy helpers, and show functions from JFS log/transaction/extent/metapage code.

## Risks and test signals
Test load/unload or mount/unmount cleanup, all debug/statistics config combinations, proc reads, and valid/invalid loglevel writes.
