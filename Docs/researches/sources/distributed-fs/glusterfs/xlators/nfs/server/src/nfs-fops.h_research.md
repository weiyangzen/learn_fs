<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.h -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.h

## Purpose

`nfs-fops.h` declares the low-level fop bridge used by GlusterFS NFS protocol code and defines `struct nfs_fop_local`, the hidden per-call state used to connect fop wrappers to protocol callbacks. Source read: complete 241-line file.

## Important APIs, Types, and Functions

The central type is `struct nfs_fop_local`, carrying protocol local/callback pointers, iobref, inode refs, root inode normalization flags, path buffers, NFS xlator pointer, gfid dict, fd, lock command, and `gf_flock`. Important macros are `nfs_state`, `nfs_fop_mempool`, `prog_data_to_nfl`, `nfl_to_prog_data`, and `nfs_fop_handle_local_init`. The header declares all `nfs_fop_*` wrappers implemented in `nfs-fops.c`.

## Control Flow

The macros define the callback wrapping pattern: allocate a fop local, move the protocol local and callback into it, install it as `frame->local`, and later restore the original protocol local before invoking the protocol callback.

## State and Persistence Behavior

State is per-call and allocated from the NFS fop mempool. The header does not persist data but encodes ownership expectations for refs and allocated dictionaries that `nfs_fop_local_wipe` releases.

## Dependencies and Integration Points

It depends on Gluster dict/iobuf/call-stub APIs, `nfs.h`, `nfs-common.h`, NFS messages, and semaphores. It is included by `nfs-generics.c`, `nfs-common.c`, NFS inode helpers, and protocol handlers.

## Risks and Edge Cases

Callback pointers are stored through a generic void-pointer cast macro, so type mismatches are compile-light and runtime-sensitive. Any new fop wrapper must keep `struct nfs_fop_local` cleanup in sync with new owned fields. Path buffers are limited to `NFS_NAME_MAX + 1`.

## Test Signals

Compile-time coverage of every declared wrapper, plus callback smoke tests for fop success and failure paths, are the main signals. Memory instrumentation should show no leaked refs after each wrapper callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.h -->
