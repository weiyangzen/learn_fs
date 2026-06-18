<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm.h -->
# sources/distributed-fs/ceph-client/security/lsm.h

## Purpose

`lsm.h` is the private header for the generic Linux Security Module framework implementation. It centralizes debug helpers, global LSM ordering state, blob-size/cache declarations, allocator prototypes, and securityfs initialization glue.

## Important APIs, Types, and Functions

- `lsm_debug`, `lsm_pr()`, `lsm_pr_cont()`, and `lsm_pr_dbg()` support optional initialization logging.
- `lsm_active_cnt` and `lsm_idlist[]` describe enabled LSMs.
- `blob_sizes`, `lsm_file_cache`, `lsm_backing_file_cache`, and `lsm_inode_cache` expose blob layout and caches.
- `lsm_cred_alloc()` and `lsm_task_alloc()` allocate LSM security blobs for credentials and tasks.
- `securityfs_init()` is declared or stubbed depending on `CONFIG_SECURITYFS`.

## Control Flow

The header defines macros and declarations only. `lsm_init.c` consumes these declarations during early and normal LSM initialization, blob cache setup, and initcall sequencing.

## State and Persistence Behavior

All state is external. Blob sizes persist after initialization and define offsets for each enabled LSM's per-object storage. The active LSM list persists as the runtime source for syscalls such as `lsm_list_modules()`.

## Dependencies and Integration Points

It depends on `<linux/lsm_hooks.h>` and `<linux/lsm_count.h>`. It is shared by LSM initialization, syscalls, blob allocators, and securityfs setup code in the security subsystem.

## Risks and Edge Cases

The declarations must stay synchronized with actual globals and allocator implementations. Blob cache globals are used only when sizes are nonzero; consumers must tolerate absent caches for object classes no enabled LSM uses.

## Test Signals

Build coverage across securityfs-enabled and disabled configs, plus boot `lsm.debug` output and `lsm_list_modules()` results, validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/lsm.h -->
