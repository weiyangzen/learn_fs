# sources/distributed-fs/ceph-client/fs/qnx6/namei.c

## Purpose
`namei.c` implements the QNX6 dentry lookup bridge from VFS to directory scanning.

## Important APIs, types, and functions
The file provides `qnx6_lookup`, which calls `qnx6_find_ino` and then `qnx6_iget`.

## Control flow
Lookup rejects names longer than `QNX6_LONG_NAME_MAX`, asks `dir.c` to find the inode number, instantiates the inode when found, and returns it through `d_splice_alias`.

## State and persistence
No persistent state is changed. Dcache aliases and the directory's lookup hint are managed by VFS and `qnx6_find_ino`.

## Dependencies and integration points
It depends on QNX6 directory scanning, VFS dentry aliasing, and inode construction in `qnx6_iget`.

## Risks and test signals
Risks include name length boundary errors, propagating `qnx6_iget` errors only through debug logging, and stale lookup cache in the directory. Test signals include missing names, max-length long names, overlong names, inode read errors, and aliasing hard-linked entries.
