# sources/distributed-fs/ceph-client/fs/ocfs2/locks.h

## Purpose
`locks.h` declares OCFS2 VFS lock handlers for BSD flock and POSIX locks.

## Important APIs, types, and functions
It declares `ocfs2_flock(struct file *, int, struct file_lock *)` and `ocfs2_lock(struct file *, int, struct file_lock *)`.

## Control flow
The functions are called from OCFS2 file operation tables when userspace requests file locks. The implementation determines whether to use local VFS locks, OCFS2 file locks, or cluster plocks.

## State and persistence behavior
The header has no state. Declared functions affect runtime lock state only, not disk metadata.

## Dependencies and integration points
It integrates OCFS2 file operations with Linux `struct file_lock` and cluster lock management.

## Risks and edge cases
The main risk is mismatched prototypes or incorrect table wiring that bypasses cluster lock semantics. Runtime behavioral risk is in `locks.c`.

## Test signals
Build tests should cover operation table assignment. Runtime tests should cover flock/plock behavior in clustered and local mount modes.
