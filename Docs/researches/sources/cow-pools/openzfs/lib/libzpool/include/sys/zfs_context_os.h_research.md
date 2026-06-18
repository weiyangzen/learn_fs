# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/zfs_context_os.h

Minimal libzpool OS context header. It defines:
- `HAVE_LARGE_STACKS 1`

This informs common ZFS code that the userland/libzpool environment has large stacks compared with constrained kernel stacks.
