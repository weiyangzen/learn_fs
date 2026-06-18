# sources/distributed-fs/ceph-client/fs/ocfs2/move_extents.h

## Purpose
`move_extents.h` declares the OCFS2 move-extents ioctl entry point.

## Important APIs, types, and functions
It exposes `ocfs2_ioctl_move_extents(struct file *filp, void __user *argp)`, the dispatcher target for `OCFS2_IOC_MOVE_EXT`.

## Control flow
`ioctl.c` calls this function when userspace requests extent movement. The implementation validates the request, performs movement or defrag, and copies the updated range back to userspace.

## State and persistence behavior
The header has no state. The declared function can persist extent tree, allocation bitmap, truncate-log/refcount, and inode timestamp changes.

## Dependencies and integration points
It integrates ioctl dispatch with the extent movement implementation and depends on kernel `struct file` and user pointer annotations.

## Risks and edge cases
The main header-level risk is prototype drift from ioctl dispatch. Behavioral risk is in `move_extents.c`, especially partial completion and refcounted extents.

## Test signals
Build coverage should verify `OCFS2_IOC_MOVE_EXT` dispatch links to this prototype. Runtime tests should exercise move-extents behavior through ioctl.
