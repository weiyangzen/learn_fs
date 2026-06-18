# File Research: sources/block-storage/kvdo/vdo/read-only-rebuild.h

Read completely: 14 lines.

This header declares the single read-only rebuild entry point, `vdo_launch_rebuild(struct vdo *vdo, struct vdo_completion *parent)`.

Dependencies: VDO completion and `struct vdo`.

Research notes: implementation details are intentionally private to `read-only-rebuild.c`; callers only launch the asynchronous rebuild and wait on the supplied completion.
