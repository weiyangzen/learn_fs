<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_internal.h -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_internal.h

## Purpose
`vvp_internal.h` is the private contract for the llite VVP layer. It defines per-I/O, per-session, per-thread, object, and device structures plus helper accessors used by VVP device, object, page, and I/O implementations.

## Important APIs, Types, And Functions
Important types are `struct vvp_io`, `struct vvp_fault_io`, `struct vvp_thread_info`, `struct vvp_session`, `struct vvp_object`, and `struct vvp_device`. Helper APIs include `vvp_env_info()`, `vvp_env_new_lock()`, `vvp_env_new_attr()`, `vvp_env_new_io()`, `vvp_env_session()`, `vvp_env_io()`, `vvp2lu_dev()`, `lu2vvp_dev()`, `cl2vvp_dev()`, `cl2vvp()`, `lu2vvp()`, and `vvp_object_inode()`. It declares `vvp_io_init()`, `vvp_io_write_commit()`, `vvp_page_init()`, `vvp_object_alloc()`, `vvp_global_init()`, and `vvp_global_fini()`.

## Control Flow
The header has no standalone runtime flow, but it determines how VVP code obtains scratch objects from `lu_env`, attaches a `vvp_io` slice to each `cl_io`, locates the VVP object from a cl/lu object, and routes page/object/device allocation through the lower cl stack.

## State And Persistence
`struct vvp_io` persists for one cl I/O session and stores iterator, total bytes, file/iocb pointers, layout generation, readahead window state, and read/write or fault-specific queues. `struct vvp_object` persists with a Lustre inode and tracks mmap count plus one-shot discard warning state. `struct vvp_device` holds the VVP cl device and next lower cl device.

## Dependencies And Integration Points
The header depends on cl-object infrastructure, lu contexts, Linux VM/file types, and llite inode ownership. It is included by VVP device, object, page, and I/O source files and by llite superblock setup for VVP initialization.

## Risks And Edge Cases
Incorrect context-key use causes per-thread/session storage corruption. The `CLOBINVRNT` macro becomes a no-op unless expensive checks are enabled, so invariant coverage varies by build. Structure layout changes affect slab sizes declared in `vvp_dev.c` and assumptions in I/O and page callbacks.

## Test Signals
Build all supported kernel-compat configurations, run cl I/O paths for reads/writes/faults/setattr/lseek, enable expensive invariant checks, validate mmap count transitions, and exercise module load/unload to ensure declared sizes match allocated slabs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_internal.h -->
