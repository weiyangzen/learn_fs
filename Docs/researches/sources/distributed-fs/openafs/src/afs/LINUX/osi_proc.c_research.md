# sources/distributed-fs/openafs/src/afs/LINUX/osi_proc.c

## Purpose
This file creates Linux procfs reporting entries for OpenAFS cell database and unixuser/token state. It supports both modern `seq_file` proc operations and older `create_proc_info_entry` style output.

## Important APIs, types, and functions
- Global `openafs_procfs` stores the `/proc/fs/openafs` directory.
- CellServDB seq functions `c_start`, `c_next`, `c_stop`, and `c_show` iterate `CellLRU`.
- `afs_csdb_open` and `afs_csdb_operations` expose the cell database proc file.
- Unixuser seq functions `uu_start`, `uu_next`, `uu_stop`, and `uu_show` iterate `afs_users` and print token/exporter details.
- Legacy `csdbproc_info` renders CellServDB output without `seq_file`.
- `osi_proc_init` creates the proc directory and entries.
- `osi_proc_clean` removes entries and the proc directory.

## Control flow and behavior
Modern cell iteration locks `AFS_GLOCK` and `afs_xcell`, walks `CellLRU` to the requested sequence position, unlocks global lock while preserving the read lock until stop, and prints cell names, ids, indexes, and server IPs. Unixuser iteration locks `afs_xuser`, emits a header at position zero, walks all hash buckets, increments the user refcount while switching from global user-list lock to per-user lock, prints uid/PAG, refs, states, cell, vice id, token timestamps/auth handle, and NFS exporter/sysname details, then releases the user and reacquires list locking.

`osi_proc_init` creates `/proc/fs/openafs` using either `proc_root_fs` or a string path, then creates `unixusers` and CellServDB entries with `afs_proc_create` or legacy `create_proc_info_entry`. Cleanup removes CellServDB, optional unixusers, and the directory.

## State and persistence
Proc entries are runtime kernel objects. Output is derived from in-memory cell/user/token/exporter state; no state is stored by this file.

## Dependencies and integration points
It depends on Linux procfs/seq_file APIs, OpenAFS cell and unixuser tables, token structures, NFS client exporter data, locks `afs_xcell`/`afs_xuser`, and compatibility wrappers from `osi_compat.h`.

## Risks
Seq iteration lock choreography is delicate: start/next/stop manipulate `AFS_GLOCK` and AFS read locks across callbacks. User output touches token structures and exporter data while locks are intentionally switched, so stale references are possible if refcounting is wrong. Proc creation failure is not strongly surfaced. The legacy `csdbproc_info` does fixed-width offset accounting that can be fragile.

## Test signals
Read `/proc/fs/openafs/CellServDB` and `/proc/fs/openafs/unixusers` under populated and empty cell/user tables, concurrent token/cell updates, large user counts, NFS exporter users, proc creation/removal on load/unload, and both `seq_file` and legacy proc builds.
