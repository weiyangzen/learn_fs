# sources/distributed-fs/lustre-release/lustre/llite/pcc.h

## Purpose

`pcc.h` is the interface and data model for llite Persistent Client Cache. It defines dataset policy structures, superblock and inode/file runtime state, mmap wrapper state, attach context, I/O operation classification, user command representation, and the exported PCC functions consumed by llite open, close, I/O, mmap, ioctl, create, and inode cleanup paths.

## Important APIs, types, and functions

Policy parsing and matching types are `struct pcc_match_id`, `struct pcc_match_size`, `struct pcc_match_fname`, `enum pcc_field`, `enum pcc_field_op`, `struct pcc_expression`, `struct pcc_conjunction`, `struct pcc_match_rule`, and `struct pcc_matcher`. They model a disjunction of conjunctions over UID, GID, project ID, filename wildcard, file size, and modification age.

Dataset and global state are represented by `enum pcc_dataset_flags`, `struct pcc_dataset`, and `struct pcc_super`. Important flags include `PCC_DATASET_OPEN_ATTACH`, `PCC_DATASET_IO_ATTACH`, `PCC_DATASET_STAT_ATTACH`, `PCC_DATASET_PCCRW`, `PCC_DATASET_PCCRO`, `PCC_DATASET_MMAP_CONV`, `PCC_DATASET_PROJ_QUOTA`, and `PCC_DATASET_NONE`. `struct pcc_super` owns the dataset list, credentials, generation, async attach threshold, affinity flag, and mode bits used by `pcc_inode_permission()`.

Per-object runtime state is split across `struct pcc_inode`, `struct pcc_file`, and `struct pcc_vma`. `pcc_inode` is tied to `ll_inode_info` and stores the backend path, refcount, PCC type, layout generation, active I/O count, waitqueue, and detach/unlink state. `pcc_file` stores the opened backend file and whether a specific open file must fall back. `pcc_vma` wraps backend vm ops and original Lustre file state for mmap.

The exported API covers superblock lifecycle, command handling, dataset matching, attach/detach/state ioctls, file open/release, read/write/splice/fsync, getattr/setattr, mmap vm hooks, create-time RW attach, dataset refcounting, inode cleanup, and layout invalidation.

## Control flow

Most llite call sites treat these APIs as optional front-end hooks. File open initializes `struct pcc_file` with `pcc_file_init()`, calls `pcc_file_open()`, and later calls `pcc_file_release()`. Read/write-like paths call the corresponding `pcc_*` function with a `bool *cached`; if it returns with `cached == false`, normal Lustre I/O continues. Mmap paths use `pcc_file_mmap()` at mmap setup and `pcc_vm_open()`, `pcc_vm_close()`, `pcc_fault()`, and `pcc_page_mkwrite()` from vm operations. Create paths can use `pcc_inode_create()` and `pcc_inode_create_fini()` to make and attach a local RW PCC copy.

## State and persistence behavior

The header defines in-memory ownership and persistence boundaries. Dataset configuration is live in `pcc_super`, protected by `pccs_rw_sem`, and versioned by `pccs_generation`. `pcc_inode` stores the backend `struct path` and layout generation that `pcc.c` also persists in local xattrs. `pcc_file` is per-open state and tracks local file handles plus fallback. `pcc_vma` reference counts mmap wrappers and preserves backend vm operations. No code in the header itself persists state, but the structures are designed around the `user.PCC.layout` and `user.PCC.encsize` persistence in `pcc.c`.

## Dependencies and integration points

The header depends on Linux VFS/MM types, Lustre user ABI types from `lustre_user.h`, HSM tool type enums, `struct ll_inode_info`, `struct ll_sb_info`, `struct cl_layout`, `struct lu_fid`, VM fault types, pipe splice types, and Lustre PCC user ioctl structs. It is included by `pcc.c` and llite implementation files that need to call PCC hooks.

## Risks and edge cases

The key risk is that many fields encode locking and reference-count assumptions not enforced by the type system. `pcci_refcount == 0` means uninitialized and `1` means attached with no user, so callers must use the helper lifecycle. `pcci_active_ios` and `pcci_waitq` must bracket every redirected operation. `pccf_fallback` interacts with inode-level mmap-negative counters, so missed reset paths can suppress PCC use. `pcc_vma_file()` depends on `vm_private_data` containing a valid `struct pcc_vma`, but falls back to `vma->vm_file` when absent.

## Test signals

Compile coverage across kernel feature macros is important because declarations include folio/page, mmap, splice, and ioctl-facing APIs. Runtime tests should observe `cached` booleans, per-open fallback reset, mmap open/close refcounts, attach/detach state reporting, and generation-driven auto attach eligibility.
