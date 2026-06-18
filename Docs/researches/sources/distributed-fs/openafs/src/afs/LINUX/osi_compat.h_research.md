# sources/distributed-fs/openafs/src/afs/LINUX/osi_compat.h

## Purpose
This header centralizes Linux kernel API compatibility for OpenAFS. It hides version and configuration differences in dentry/file/inode/proc/export/keyring/page/folio/socket/freezer/path APIs so the rest of the Linux AFS tree can call stable `afs_*` wrappers.

## Important APIs, types, and functions
- Type and field shims: `afs_linux_path_t`, `file_dentry`, `d_alias`, `d_child`, `afs_kmem_cache_t`, `KALLOC_TYPE`.
- Lock and file-lock wrappers: `flock_lock_file_wait`, `afs_posix_lock_file`, `afs_posix_test_lock`, `afs_linux_lock_inode`, `afs_linux_unlock_inode`, dentry alias lock/iteration macros.
- Keyring wrappers: `afs_linux_key_alloc`, `afs_session_keyring`, `afs_linux_search_keyring`, `afs_set_session_keyring`, and `afs_linux_cred_is_current`.
- Page/folio wrappers: `afs_page_index`, `zero_user_segment(s)`, `afs_page_wait_locked`, `afs_put_page`, `afs_FolioLocked`, `afs_unlock_folio`, `afs_readahead_folio`.
- Export/cache wrappers: `afs_get_dentry_from_fh`, `afs_get_fh_from_dentry`, `afs_init_sb_export_ops`.
- Path/proc wrappers: `afs_kern_path`, `afs_get_dentry_ref`, `afs_proc_create`, `afs_d_path`, `afs_lookup_noperm`.
- File I/O and setattr wrappers: `afs_dentry_open`, `afs_truncate`, `afs_file_read`, `afs_file_write`, `afs_setattr_prepare`, `afs_inode_setattr`.
- Freezer/socket helpers: `afs_try_to_freeze`, `freezing`, `wait_event_freezable`, `wait_event_freezable_timeout`, `afs_linux_sock_set_mtu_discover`, and `afs_linux_sock_set_recverr`.

## Control flow and behavior
The header is almost entirely compile-time dispatch. Each wrapper selects the correct Linux API signature or fallback based on configure-derived macros. For example, export helpers switch between modern `fh_to_dentry`/`encode_fh` and older `decode_fh`/`export_op_default`; file I/O selects `__vfs_read`, `kernel_read`, or file operation pointers; setattr selects idmap, user namespace, current `setattr_prepare`, or legacy `inode_change_ok`; proc entries select `proc_create` or `create_proc_entry`.

The keyring path adapts `key_alloc` signatures and session-keyring storage across credential models. Page helpers translate page-oriented OpenAFS code to folio-aware APIs on newer kernels. The custom `wait_event_freezable` fallbacks reproduce old AFS freezer semantics when the kernel does not provide them.

## State and persistence
As a header, it owns no standalone runtime state, but several helpers mutate kernel objects: dentry flags, session keyrings, inode attributes, socket options, page flags, and dcache state. It references globals such as `afs_ns` and `afs_mnt_idmap` populated by module init.

## Dependencies and integration points
This header is included by Linux AFS files such as `osi_file.c`, `osi_groups.c`, `osi_misc.c`, `osi_proc.c`, `osi_pagecopy.c`, and vnode/vfs code elsewhere. It depends on Linux kernel headers selected by configuration (`freezer.h`, `filelock.h`, key headers, `uaccess`, exportfs, folio APIs) and OpenAFS types such as `afs_ucred_t`, `afs_dcache_id_t`, and `struct osi_file`.

## Risks
Compatibility headers carry high regression risk because many branches are rarely compiled together. Some fallback code uses old primitives such as `set_fs`, direct dentry flag mutation, legacy proc APIs, and old page-index fields. Mistakes in wrapper signatures can compile on one kernel family and fail or corrupt state on another. The `hlist_unhashed` fallback appears suspicious because it returns `(!h->pprev == NULL)`, which is easy to misread and may not match Linux semantics. Keyring and credential wrappers are especially sensitive to reference ownership and RCU/session-keyring lifetime.

## Test signals
The primary signal is a kernel build matrix across supported Linux releases and architectures, covering keyring/non-keyring, old/new export ops, folio and non-folio APIs, idmapped/user-namespace setattr APIs, proc_ops/file_operations, and `kernel_read`/legacy read paths. Runtime smoke tests should exercise cache file handle encode/decode, proc creation, cache reads/writes, socket option setup, freezer waits, dentry invalidation, and PAG keyring lookup.
