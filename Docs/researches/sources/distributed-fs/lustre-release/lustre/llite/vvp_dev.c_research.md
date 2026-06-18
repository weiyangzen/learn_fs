<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_dev.c -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_dev.c

## Purpose
`vvp_dev.c` implements VVP (`Vfs Vm Posix`) cl-device type registration, per-context storage allocation, superblock cl-stack setup, and the debugfs `dump_page_cache` walker for llite mounts.

## Important APIs, Types, And Functions
The file defines kmem descriptors for `ll_thread_info`, `vvp_object`, `vvp_session`, and `vvp_thread_info`; context keys `ll_thread_key`, `vvp_session_key`, and `vvp_thread_key`; `vvp_device_type`; and lifecycle functions `vvp_global_init()`, `vvp_global_fini()`, `cl_sb_init()`, and `cl_sb_fini()`. Debugfs support is exposed through `vvp_dump_pgcache_file_ops`.

## Control Flow
Global init creates caches and registers the VVP lu device type. Superblock init obtains a cl environment and builds a VVP cl-device over the data target lu device, saving `ll_cl` and `ll_site` in the superblock. Device allocation creates a `vvp_device`, initializes a cl site, and wires the lower device into the same lu site. The page-cache dump opens a seq file, grabs a cl environment, walks the lu-site object hash, finds each object's page-cache pages, maps them back to `cl_page`, and prints FID, index, writeback state, page count, and page flags.

## State And Persistence
Persistent state includes global slabs, context-key allocations, the `vvp_device_type`, per-superblock cl-device/site pointers, and temporary seq-file state in `struct vvp_seq_private`. Device teardown unwinds lower lu stack state and clears superblock pointers.

## Dependencies And Integration Points
This file sits between llite superblock setup and the cl/lov/osc stack. It depends on lu/cl context APIs, `lu_kmem_init()`, `lu_device_type_init()`, `cl_type_setup()`, rhashtable object storage, page-cache helpers, and `vvp_object_inode()` from the VVP object layer.

## Risks And Edge Cases
Device init and cleanup require a usable cl environment; memory pressure can make `cl_sb_fini()` fail loudly. The seq walker must handle rhashtable `-EAGAIN`, object references, page references, and mount teardown. `dump_page_cache` returns `-ENODATA` until common client fill-super succeeded.

## Test Signals
Exercise module init/fini, mount/unmount cl stack creation, failure injection for cache and site allocation, debugfs page-cache dumps while pages are dirty/writeback/evicted, rhashtable iteration during object churn, and cleanup under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_dev.c -->
