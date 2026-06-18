# sources/distributed-fs/ceph-client/scripts/gdb/linux/vfs.py

## Purpose
`vfs.py` provides GDB functions for VFS object naming: full dentry path reconstruction and inode-to-dentry lookup.

## Important APIs, Types, and Functions
`dentry_name()` recursively walks `d_parent` and concatenates `d_name.name`. `$lx_dentry_name()` returns that path. `$lx_i_dentry()` returns the dentry containing an inode's first `i_dentry` hlist node via `container_of()`.

## Control Flow
Dentry naming stops at self-parented or null parents. Inode lookup checks `i_dentry.first`; empty lists return an empty string, otherwise it computes the enclosing `struct dentry`.

## State and Persistence Behavior
Read-only and stateless. It samples live VFS objects without taking locks.

## Dependencies and Integration Points
`proc.py` uses `dentry_name()` for mount path reconstruction. The file depends on `utils.container_of()` and `struct dentry` layout.

## Risks and Test Signals
Recursive path building can loop on corrupt parent pointers and does not escape names like `/proc` output does. Inodes with multiple dentries only return the first. Test with root dentries, nested paths, deleted dentries, and inodes with no dentry.
