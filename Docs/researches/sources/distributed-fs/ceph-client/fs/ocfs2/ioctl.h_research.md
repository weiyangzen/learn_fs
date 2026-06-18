# sources/distributed-fs/ceph-client/fs/ocfs2/ioctl.h

## Purpose
`ioctl.h` publishes the OCFS2 ioctl and file attribute entry points used by file operation tables and VFS inode operation setup.

## Important APIs, types, and functions
The header declares `ocfs2_fileattr_get()`, `ocfs2_fileattr_set()`, `ocfs2_ioctl()`, and `ocfs2_compat_ioctl()`. These prototypes expose the implementation in `ioctl.c` without exporting ioctl internals such as info request parsing.

## Control flow
Callers enter through VFS fileattr or ioctl hooks. `ocfs2_compat_ioctl()` is compiled only when the implementation side is under `CONFIG_COMPAT`, but the prototype is always visible to code that wires operation tables in matching build contexts.

## State and persistence behavior
The header has no state. Its declared functions may mutate persistent inode flags, filesystem geometry, extents, or allocation state depending on the ioctl command.

## Dependencies and integration points
It depends on kernel type declarations for `struct dentry`, `struct file_kattr`, `struct mnt_idmap`, and `struct file` supplied by including compilation units. It is an integration shim between OCFS2 VFS operation tables and the ioctl implementation.

## Risks and edge cases
Prototype drift between this header and `ioctl.c` would break VFS table wiring. Build coverage with and without compat support is important because the compat implementation is conditional.

## Test signals
Compile tests should cover ioctl table assignment, fileattr hooks, and compat builds. Runtime signals live in `ioctl.c` tests.
