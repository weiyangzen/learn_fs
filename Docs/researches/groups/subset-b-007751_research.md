# subset-b-007751 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vnodeops.c -->
# sources/distributed-fs/openafs/src/afs/IRIX/osi_vnodeops.c

## Purpose
This SGI IRIX-specific file binds the portable OpenAFS cache manager to the IRIX vnode layer. It defines the AFS vnode operation vector, implements IRIX read/write paging integration, byte-lock handling, vnode inactive/reclaim behavior, vnode read/write serialization, MP wrapper entry points, and helpers used by XFS-backed cache code to derive inode/device/size metadata from vnodes.

## Important APIs, types, and functions
- `Afs_vnodeops` / `afs_lockedvnodeops` map IRIX VOP slots to OpenAFS operations such as `afs_open`, `afs_lookup`, `afs_fsync`, plus local wrappers `afs_xread`, `afs_xwrite`, `afs_xbmap`, `afs_strategy`, `afs_map`, `afs_xinactive`, `afs_rwlock`, and `afs_rwunlock`.
- `afs_frlock` delegates byte-range locks to IRIX `fs_frlock` but falls back to AFS whole-file lock handling through `afs_lockctl` for full-file locks and `F_GETLK`.
- `afs_xread` and `afs_xwrite` validate regular-file access, handle append offsets, take the vnode rwlock unless already locked, and call `afsrwvp`.
- `afsrwvp` is the main read/write engine. It verifies the vcache, flushes stale VM pages, coordinates chunk reads/writes, prefetch, dirty-state updates, NFS translator fake opens, and synchronous storeback.
- `afs_xbmap` builds IRIX `bmapval` mappings for the virtual AFS block/page cache.
- `afs_strategy` is the buffer strategy callback used by `chunkread`/`getchunk` to call portable `afs_read` or `afs_write` with saved credentials.
- `afs_map` handles memory mapping by verifying the vnode, flushing stale pages, and tracking mappings that may require store-on-last-reference.
- `afs_xinactive` performs last-reference cleanup, deferred unlink removal, dirty mmap storeback, credential release, and page tossing.
- `afs_rwlock`, `afs_rwunlock`, and `afs_rwlock_nowait` wrap the IRIX semaphore in per-vcache ownership/trip-count bookkeeping.
- `afs_fid2` supports IRIX checkpoint/restart or R5000 workaround behavior, depending on compile-time options.
- `VnodeToIno`, `VnodeToDev`, and `VnodeToSize` query backing vnode attributes for XFS cache support.

## Control flow and behavior
The VFS calls into the operation vector. Read/write VOPs enter `afs_xread`/`afs_xwrite`, obtain a per-vcache rwlock, and call `afsrwvp`. `afsrwvp` creates an AFS request, verifies cache status, invalidates stale pages, saves credentials for later asynchronous strategy calls, optionally fake-opens NFS-translator writes, marks write vnodes dirty, drops `AFS_GLOCK`, and loops over page-sized `bmapval` ranges. Reads build one or two mappings for normal read and read-ahead, call `chunkread`, optionally trigger `afs_PrefetchChunk`, copy buffer data into the caller `uio`, and release or asynchronously write delayed buffers. Writes use `getchunk` or `chunkread`, copy caller data into buffers, update cached length/time, schedule writes, and periodically call `afs_DoPartialWrite`. After the loop, the code reacquires `AFS_GLOCK`, drains partial writes, performs `afs_fsync` for sync writes when not an NFS translator request, and fake-closes any translator write.

`afs_strategy` is reached from IRIX buffer/page cache code. It guards against recursive dirty-buffer deadlocks, handles EOF reads by zeroing the buffer, skips delayed writes already being written to UFS, uses `avc->cred` for background calls, maps the buffer to a one-element `uio`, calls portable `afs_read`/`afs_write`, stores write errors in `avc->vc_error`, and completes the buffer with `iodone`.

Inactive handling first verifies that the vnode is really inactive, then tries to acquire AFS locks without blocking. It resolves unlinked files immediately or defers deletion with `CUnlinkedDel` if vcache/dcache locks are already held. Dirty or potentially writable mappings call `afs_StoreOnLastReference`; failures warn and invalidate segments. The final path clears saved credentials and tosses pages for link-count-zero vnodes.

## State and persistence
The file mutates vcache runtime state including `f.states` (`CDirty`, `CUnlinked`, `CUnlinkedDel`), `f.m.Length`, `f.m.Date`, `vc_error`, `lastr`, `cred`, `opens`, `execsOrWriters`, and `mapcnt`. Persistent file contents are written through AFS chunk/cache mechanisms and storeback routines, not directly here. Page and buffer cache state is aggressively flushed or written to avoid stale or recursive delayed-write conditions on IRIX. Saved credentials persist in the vcache until inactive cleanup.

## Dependencies and integration points
This code depends on IRIX vnode, buffer, semaphore, VM, lock, and XFS APIs; OpenAFS vcache/dcache/request/chunk/prefetch/storeback APIs; `afs_stats` tracing; and NFS translator globals such as `root_exported`. MP builds wrap almost every operation with `AFS_GLOCK` in `mp_afs_*` functions and install those wrappers in the externally visible `Afs_vnodeops`.

## Risks
Risk is concentrated in lock ordering between `AFS_GLOCK`, vnode rwlocks, vcache locks, IRIX buffer locks, and page-cache operations. `afs_strategy` depends on saved credentials and can be called asynchronously; missing credentials panic. Dirty mmap behavior is handled late at inactive time, so storeback failures can only warn and invalidate. The buffer recursion comments show known deadlock hazards around delayed-write AFS buffers and UFS/EFS cache writes. `afs_fid2` behavior changes by checkpoint/R5000 build options and can affect restart/export users. The implementation is tightly tied to obsolete IRIX kernel structures, so portability regression risk is high.

## Test signals
Useful signals include IRIX kernel module build coverage with MP and non-MP variants; vnode read/write tests across page boundaries, EOF, append, mmap dirty writeback, and sync writes; NFS translator read/write paths that exercise fake open/close and credential retention; byte-range and whole-file lock tests; unlink-while-open cleanup; induced cache write errors to verify `vc_error` and warning behavior; and XFS cache metadata helper tests for vnode attribute extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/IRIX/osi_vnodeops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_alloc.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_alloc.c

## Purpose
This file implements OpenAFS Linux kernel memory allocation wrappers. It chooses `kmalloc` for small allocations and `vmalloc` for larger ones, tracks every returned allocation in an OpenAFS atom-list/hash-table registry, supports global cleanup at module shutdown, and provides optional fixed-size small/large private allocation spaces.

## Important APIs, types, and functions
- `struct osi_linux_mem` stores the original allocation pointer with low-bit allocation type tags.
- `osi_linux_alloc(size, drop_glock)` allocates zeroed memory, lazily initializes tracking structures, records the allocation, and returns the untagged address.
- `osi_linux_free(addr)` removes a tracked allocation from the hash table and frees it with the matching kernel free routine.
- `osi_linux_free_afs_memory()` frees all outstanding tracked chunks and destroys the atom list and hash table.
- `osi_linux_verify_alloced_memory()` iterates tracked chunks and verifies tag sanity/counts.
- `linux_alloc`, `linux_free`, `hash_chunk`, `hash_free`, and `hash_verify` are static helpers for allocation, deallocation, hashing, cleanup, and diagnostics.
- Optional `osi_AllocLargeSpace`, `osi_AllocSmallSpace`, `osi_FreeLargeSpace`, and `osi_FreeSmallSpace` wrap fixed-size `kmalloc`/`kfree` when `AFS_PRIVATE_OSI_ALLOCSPACES` is enabled.

## Control flow and behavior
`osi_linux_alloc` first calls `linux_alloc`, which retries up to ten times. Allocations at or below `PAGE_SIZE` use `kmalloc(GFP_NOFS)` and larger allocations use `vmalloc`; large allocations assert that either the global lock can be dropped or is not held, then temporarily releases `AFS_GLOCK` around `vmalloc` and retry sleeps when requested. Successful allocations are zeroed and tagged in the low two pointer bits as `KM_TYPE` or `VM_TYPE`. Under `afs_linux_alloc_sem`, the public allocator initializes the atom pool/hash table on first use, obtains a tracking node, records the tagged pointer, and enters it into `lh_mem_htab`.

Freeing constructs a lookup key from the untagged address, removes the tracking node, frees the tagged pointer via `linux_free`, returns the tracking node to the atom list, and decrements current allocation counters. Whole-module cleanup iterates the hash table with `hash_free`, then destroys both registry structures and clears `allocator_init`.

## State and persistence
The persistent module state is the allocator registry: `al_mem_pool`, `lh_mem_htab`, `allocator_init`, `afs_linux_cur_allocs`, `afs_linux_total_allocs`, and `afs_linux_hash_verify_count`. Memory survives until individually freed or until `osi_linux_free_afs_memory` runs during module shutdown. There is no disk persistence.

## Dependencies and integration points
The implementation uses Linux `kmalloc`, `kfree`, `vmalloc`, `vfree`, scheduler sleep primitives, and OpenAFS `afs_atomlist`/`afs_lhash` utilities. It is invoked by broader AFS kernel code through prototypes in `osi_prototypes.h` and cleaned from module/PAG-manager shutdown paths.

## Risks
The low-bit pointer tagging assumes kernel allocation alignment and comments mention 32-bit pointers, although the code casts through `unsigned long`. Any untracked pointer passed to `osi_linux_free` panics. Initialization failure after a successful raw allocation is carefully freed but could leak the atom list if hash creation fails before a later cleanup path. `osi_linux_verify_alloced_memory` computes a difference with unsigned counters, so mismatch diagnostics may underflow. Sleeping and dropping `AFS_GLOCK` around `vmalloc` are necessary but sensitive to callers' lock expectations.

## Test signals
Exercise small and large allocation/free cycles, allocation failure injection, shutdown cleanup with outstanding allocations, double/untracked free panic behavior, verify-count diagnostics, and builds with `AFS_PRIVATE_OSI_ALLOCSPACES`. Locking tests should cover calls with and without `AFS_GLOCK` and `drop_glock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_compat.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_cred.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_cred.c

## Purpose
This file provides Linux credential allocation, duplication, reference, and installation routines for OpenAFS kernel code. It abstracts older in-task credential fields and newer `struct cred` reference semantics behind the AFS `cred_t` interface.

## Important APIs, types, and functions
- `crget()` allocates a credential object and initializes its reference state.
- `crfree(cr)` releases a credential and associated group-info references.
- `crdup(cr)` returns an independent duplicate credential.
- `crref()` returns a reference/snapshot of the current task credentials.
- `crset(cr)` installs credential values into the current task.
- `afs_copy_creds(to, from)` copies uid/gid/fsuid/fsgid and group info while maintaining group reference counts.

## Control flow and behavior
On kernels with `STRUCT_TASK_STRUCT_HAS_CRED`, `crref` uses `get_current_cred`, `crfree` uses `put_cred`, and `crset` creates mutable credentials with `prepare_creds`, replaces group info, and commits them with `commit_creds` only if `current->cred == current->real_cred`. Older kernels allocate/free raw `cred_t` with `kmalloc`/`kfree`, maintain `cr_ref`, copy uid/gid fields directly, and update `current` fields under `task_lock` when group info changes.

## State and persistence
Credentials are in-memory kernel objects with reference counts and group-info ownership. There is no disk persistence. `crset` mutates the current task credential state, affecting later permission checks and PAG/group behavior.

## Dependencies and integration points
This layer is used by Linux PAG/keyring, NFS translator, ioctl/syscall, cache I/O, and export code whenever an AFS request needs caller credentials. It depends on OpenAFS credential macros (`afs_cr_uid`, `afs_set_cr_group_info`, etc.) and Linux group-info reference APIs.

## Risks
`crget` on modern credential kernels calls `get_cred(tmp)` on freshly allocated memory, which relies on `cred_t` layout/configuration assumptions elsewhere in the tree; this is a sensitive area for kernel API drift. `crset` silently returns when real and effective credentials differ, which can surprise callers expecting a credential change. Group-info reference ownership must stay exact or leaks/use-after-free bugs follow. Older branches directly mutate `current` credential fields, which is unsafe on newer kernels and must be gated correctly.

## Test signals
Build tests across both credential models are essential. Runtime tests should cover `setpag`, `setgroups`, token lookup under duplicated credentials, `crset` for matching/nonmatching real credentials, group reference leak detection, and NFS translator/export request credential propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_cred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_crypto.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_crypto.c

## Purpose
This small Linux OSI file supplies random-byte generation for OpenAFS cryptographic or nonce consumers.

## Important APIs, types, and functions
- `osi_readRandom(void *data, afs_size_t len)` fills `data` with `len` bytes using Linux `get_random_bytes` and returns `0`.

## Control flow and behavior
The function is a direct wrapper: callers provide a buffer and byte length, Linux kernel random bytes are written into the buffer, and success is always reported as `0`.

## State and persistence
No OpenAFS state is stored. The only state dependency is the kernel random subsystem.

## Dependencies and integration points
It includes Linux `random.h` and OpenAFS base headers. The exported OSI function is expected by portable AFS code that needs random material.

## Risks
There is no error path or readiness indication. The function trusts caller-provided buffer and length and cannot report entropy/rng subsystem failures. Behavior depends on `get_random_bytes` semantics for the target kernel.

## Test signals
Compile coverage and simple kernel-unit style checks that the buffer changes and the function returns `0` are enough. Security review should verify callers do not need blocking or failure-aware randomness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_export.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_export.c

## Purpose
This file implements Linux `export_operations` for exporting AFS through NFS translator support. It encodes AFS FIDs into Linux file handles, decodes file handles back to vcaches/dentries, resolves parent/name relationships for exported dentries, and handles dynroot/fakestat special cases.

## Important APIs, types, and functions
- File-handle type constants such as `AFSFH_NET_VENUSFID`, `AFSFH_NET_CELLFID`, `AFSFH_DYN_RO_CELL`, `AFSFH_DYN_MOUNT`, and related dynroot link/cell variants.
- `afs_encode_fh` serializes normal and dynroot vcache FIDs into Linux export file handles.
- `afs_fh_to_dentry` or legacy `afs_decode_fh` decodes file handles to AFS `VenusFid` values and calls dentry construction.
- `update_dir_parent` reads the `..` entry from a directory dcache and updates `adp->f.parent`.
- `UnEvalFakeStat` maps a fakestat volume-root directory back to its mount point when required.
- `get_dentry_from_fid` creates an AFS request, obtains a vcache, fills inode attributes, and creates an anonymous dentry.
- `afs_export_get_dentry`, `afs_export_get_name`, and `afs_export_get_parent` implement the Linux export callbacks.
- `afs_export_ops` registers the callback table.

## Control flow and behavior
Encoding starts from the dentry inode's vcache. Dynroot FIDs are encoded by dynroot vnode type: cell/alias handles store a cell handle, mount handles also store the unique field, and unsupported dynroot symlinks fail. Normal file handles prefer a migratable cell-handle format when there is enough space; otherwise they emit a four-word network-order VenusFid.

Decoding switches on file-handle type, validates length, maps cell handles back to local cell numbers, synthesizes dynroot FIDs where needed, then calls the modern or legacy dentry lookup path. `get_dentry_from_fid` builds request/attribute objects, calls `afs_GetVCache`, updates missing directory parents, optionally unevaluates fakestat volume roots, refreshes inode attributes with `afs_getattr`/`afs_fill_inode`, drops `AFS_GLOCK` around `d_alloc_anon`, attaches AFS dentry operations, and returns the dentry or an encoded error.

`afs_export_get_name` resolves a child's name in a parent directory. It handles the dynamic mount directory, volume-root mount point FID translation, fake-stat evaluation, parent cell/volume mismatch rejection, dcache freshness/fetching waits, and `afs_dir_EnumerateDir` with `get_name_hook`. `afs_export_get_parent` handles dynmount roots, dynroot mount children, volume-root mount parent FIDs, and ordinary parent FID fields, using `update_dir_parent` if a directory parent is not yet cached.

## State and persistence
The file updates runtime vcache metadata such as directory parent vnode/unique fields and may force vcache/inode attribute refresh. It does not persist data itself, but it uses cached directory contents and volume/cell metadata to reconstruct exported object identity. File handles include cell handles to remain stable across local cell-number changes.

## Dependencies and integration points
The code integrates Linux exportfs with OpenAFS vcache, dcache, dynroot, fakestat, cell, volume, request, inode, dentry, and NFS translator layers. It is compiled only when `AFS_NONFSTRANS` is not defined. It depends on `afs_dentry_operations`, `afs_fill_inode`, `afs_GetCellByHandle`, `afs_GetDCache`, `afs_dir_Lookup`, and `afs_dir_EnumerateDir`.

## Risks
Export correctness is sensitive to stale directory caches, missing parent FIDs, cell-handle lookup failures, fakestat policy, and dynroot edge cases. `afs_export_get_name` includes an unconditional success `printk`, which may be noisy for exported workloads. `d_alloc_anon` requires careful lock dropping; vcache/inode references must remain valid across that window. NFS export semantics rely on stable handles; fallback four-word local cell-number handles are less migratable. Unsupported dynroot symlink handles return failure.

## Test signals
NFS export tests should cover normal file and directory handle encode/decode, reconnect after cell-number changes using cell handles, dynroot cell/link/mount cases, volume roots with fakestat enabled/disabled, parent lookup for newly materialized directories, stale directory cache refresh/retry, negative dentries, and missing cells/volumes. Lockdep and reference-count leak checks are high value around anonymous dentry construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_file.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_file.c

## Purpose
This file implements Linux cache-file operations for OpenAFS disk cache access. It opens cache files from stored file handles, records cache filesystem metadata, performs kernel-space read/write/truncate/stat operations through Linux VFS wrappers, and implements AFS `uio` movement helpers.

## Important APIs, types, and functions
- `afs_linux_raw_open(afs_dcache_id_t *ainode)` decodes a stored cache file handle to a dentry and opens it read/write with cache credentials.
- `osi_UFSOpen` allocates and initializes `struct osi_file` for a cache dcache entry.
- `osi_get_fh` encodes and validates uniform filesystem file handles for cache files.
- `afs_osi_Stat`, `osi_UFSClose`, and `osi_UFSTruncate` implement stat, close, and shrink operations.
- `afs_osi_Read` and `afs_osi_Write` build one-element `uio`s and call `osi_rdwr`.
- `osi_InitCacheInfo` resolves the cache path, stores cache device/superblock/mount/filehandle info, and initializes export ops.
- `osi_rdwr` loops through `uio` iovecs, temporarily lifts `RLIMIT_FSIZE`, optionally switches address limits on older kernels, and calls `afs_file_read`/`afs_file_write`.
- `setup_uio` and `uiomove` are utility routines for AFS-style UIO structures.

## Control flow and behavior
Cache initialization looks up the cache directory path, stores the mount, dentry, superblock, device, fragment mask, and initial file handle, then configures superblock export operations for file-handle decode support. Opening a cache file decodes its stored file handle through `afs_get_dentry_from_fh`, sets `S_NOATIME`, overrides credentials when available, opens via `afs_dentry_open`/`dentry_open`, falls back from stashed cache credentials to current credentials on newer cred kernels, and returns a `struct file`.

Read/write wrappers validate `struct osi_file`, update the stored offset when requested, build a `uio`, drop `AFS_GLOCK`, call `osi_rdwr`, reacquire `AFS_GLOCK`, convert success to byte counts, and normalize errors. `osi_rdwr` overrides cache credentials, sets file-size rlimit to infinity, optionally sets kernel address limits for old APIs, iterates iovecs, calls the compatibility file read/write wrapper at `uio_offset`, advances iovec/residual/offset on progress, and treats a zero-length VFS transfer as `EIO`. Truncation avoids expensive no-op truncates, locks the inode, prepares attributes with current time, calls compatibility setattr helpers, and truncates page cache.

## State and persistence
This file stores global cache file-handle format state (`cache_fh_type`, `cache_fh_len`) and uses global cache mount/superblock/device values. `struct osi_file` tracks `filp`, `size`, `offset`, and optional completion callback `proc`. It persists cache contents through the underlying Linux filesystem and keeps access times suppressed via `S_NOATIME`.

## Dependencies and integration points
It depends on Linux VFS, exportfs, namei, credentials, inode locks, file read/write APIs, and compatibility helpers from `osi_compat.h`. It integrates with OpenAFS disk cache state (`cacheDiskType`, `cacheDev`, `cacheInode`, `afs_cacheMnt`, `afs_cacheSBp`, `cache_creds`), allocator/stat APIs, and higher-level cache manager read/write paths.

## Risks
Cache file handle decoding failures are warned as potentially leading to AFS access errors or kernel panic. Uniform file-handle assumptions are enforced with panic if cache files produce inconsistent handle type/length. Credential override/fallback behavior can mask LSM issues or fail under changed security policy. `osi_rdwr` mutates the current task rlimit and older address limit state and must restore them on every path. A zero-byte VFS read/write is treated as `EIO`, which may turn EOF-like conditions into errors for cache operations. Truncate avoids `notify_change` intentionally, so compatibility with newer inode/dentry expectations depends on wrappers.

## Test signals
Test cache initialization on filesystems with and without export operations, cache open/read/write/truncate/stat/close, file-handle consistency across multiple cache files, SELinux/AppArmor cache credential scenarios, ENOSPC write warnings, shutdown behavior with null `osi_file`, and old/new kernel file I/O API builds. Fault injection around `afs_get_dentry_from_fh`, `dentry_open`, `setattr_prepare`, and partial VFS transfers is valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_flush.s -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_flush.s

## Purpose
This PowerPC64 assembly file exports `flush_cache(addr, len)`, a low-level helper that flushes data cache and invalidates instruction cache over an address range.

## Important APIs, types, and functions
- `flush_cache` is an ELFv1-style function descriptor in `.opd` pointing to `.flush_cache`.
- `.flush_cache` iterates cache-line-sized chunks, performing `dcbf` and `icbi`, then issues `sync` and `isync`.

## Control flow and behavior
The function rounds the requested length up by adding `0x1f`, shifts to count 32-byte cache lines, exits immediately when the count is zero, and loops over each line flushing data cache and invalidating instruction cache at the current address. It advances by `0x20` bytes and finishes with synchronization barriers.

## State and persistence
It mutates processor cache state only. There is no OpenAFS memory or disk state.

## Dependencies and integration points
The code is architecture-specific PowerPC64 assembly borrowed from Linux boot code. It is expected by Linux/PPC64 AFS code paths that need explicit instruction/data cache coherency.

## Risks
The code assumes 32-byte cache-line granularity and old PPC64 ABI/function descriptor conventions. Incorrect use on kernels/architectures with different ABI or cache geometry would be unsafe. There is no runtime validation.

## Test signals
Build/link tests on the intended PPC64 ABI are the main signal. Runtime validation should exercise any caller that writes executable or code-like data and then invokes this flush before execution or probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_flush.s -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_gcpags.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_gcpags.c

## Purpose
This file supports PAG garbage collection on Linux by traversing process credentials and extracting credentials for a task when group-based PAGs are in use.

## Important APIs, types, and functions
- `afs_osi_TraverseProcTable()` walks live processes and calls `afs_GCPAGs_perproc_func`.
- `afs_osi_proc2cred(afs_proc_t *pr)` returns a static AFS credential snapshot for a process.

## Control flow and behavior
When `AFS_GCPAGS` is enabled and keyring/credential conditions permit safe group scanning, traversal enters `rcu_read_lock`, iterates `for_each_process` or legacy `for_each_task`, skips pid-zero and zombie/exited tasks, and invokes the portable PAG-GC callback. `afs_osi_proc2cred` validates process state, fills a static `afs_ucred_t` with uid and group info from the task, increments group-info references, and returns the static pointer.

## State and persistence
`afs_osi_proc2cred` uses a static credential object overwritten on each call. It increments group-info references for returned snapshots, although comments warn that freeing the static credential would be dangerous. No persistent state exists.

## Dependencies and integration points
The code integrates Linux task traversal/RCU with OpenAFS PAG garbage collection. It is disabled when keyring PAGs are used or when safe RCU/task credential access is not available.

## Risks
The static credential return is explicitly dangerous if consumers call `crfree` on it. Task credential access must match kernel RCU semantics exactly. The code is compile-time gated away for keyring support, so group-based and keyring-based PAG GC behavior diverges.

## Test signals
PAG GC tests should cover process traversal with live, exiting, and zombie tasks; group-PAG detection; reference leak checks for group info; and build variants with/without `LINUX_KEYRING_SUPPORT`, `STRUCT_TASK_STRUCT_HAS_CRED`, and RCU support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_groups.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_groups.c

## Purpose
This file implements Linux PAG management through process groups and, when configured, Linux keyrings. It handles `setpag`, preserves PAGs across `setgroups` syscall interception on non-keyring systems, defines the AFS PAG key type, and registers/unregisters keyring support.

## Important APIs, types, and functions
- `afs_linux_pag_from_groups` and `afs_linux_pag_to_groups` encode/decode PAGs in Linux `group_info`, either one-group or two-group style.
- `osi_get_group_pag` extracts the group-based PAG from an AFS credential.
- `afs_setgroups` installs a new group list in the AFS credential/current task and optionally parent task on old kernels.
- `__setpag` generates or applies a PAG value and rewrites group info.
- `setpag` wraps `__setpag`, installs a session keyring and `_pag` key when keyrings are enabled, and rolls back on failure.
- Non-keyring `afs_xsetgroups`, `afs_xsetgroups32`, `afs32_xsetgroups`, and `afs32_xsetgroups32` wrap setgroups syscalls to restore a lost PAG.
- Keyring callbacks `afs_pag_describe`, `afs_pag_instantiate`, `afs_pag_match`, and `afs_pag_destroy` define `key_type_afs_pag`.
- `osi_keyring_init`, `osi_keyring_shutdown`, and `osi_get_keyring_pag` register and query keyring PAG state.

## Control flow and behavior
For group-based PAGs, `__setpag` optionally calls `afs_genpag`, references the old group list, constructs a new group list with PAG groups inserted/replaced, installs it through `afs_setgroups`, and returns the old groups to the caller for rollback. `setpag` then optionally creates a session keyring, allocates an `_pag` key as root-owned, instantiates it with the new PAG, and converts negative keyring errors to positive AFS syscall errors. On failure it restores old groups, expires the newly marked user, and clears the output PAG.

Without keyring support, setgroups syscall wrappers record the old PAG, invoke the real syscall, then restore the PAG if the new groups dropped it. Architecture-specific 32-bit syscall variants are provided for PPC64, SPARC64, and AMD64.

With keyring support, `afs_pag_instantiate` verifies root ownership, payload size, current group PAG, and payload/PAG match before storing the PAG. Destroying a PAG key expires the corresponding AFS user under `AFS_GLOCK` as needed. `osi_get_keyring_pag` searches the session keyring, validates the key, returns the PAG, and may reinsert the PAG into current groups when the credential belongs to the current process.

## State and persistence
State lives in Linux task credentials/groups, session keyrings, the registered `key_type_afs_pag`, and AFS user/token state expired by PAG destruction. PAGs persist for the life of credentials/session keyrings and are mirrored between groups and keyrings in keyring builds.

## Dependencies and integration points
This code depends on Linux group-info, syscall hook pointers, credentials, keyring APIs, tasklist/RCU lookup for keyring type discovery, and OpenAFS PAG/token/user functions. It integrates with syscall-table probing/hooking, credential handling, and NFS translator behavior (`NFSXLATOR_CRED` is excluded from keyring PAG installation).

## Risks
PAG encoding in group lists is sensitive to sorted group order and kernel gid types. The non-onegroup branch contains assignments through `GROUP_AT(new, ...)` even though `new` is a pointer-to-pointer, making macro expectations important and worth compile coverage. Keyring install must handle quotas, restrictions, session keyring lifetime, and credential commit semantics. Syscall interception paths depend on locating writable syscall tables and correct 32-bit ABI hooks. Rollback paths must preserve group-info references exactly.

## Test signals
Run `setpag`/token tests with keyring and non-keyring builds, group list preservation across `setgroups`, one-group/two-group PAG encodings, root/non-root keyring quota behavior, session keyring absence, key destruction token expiry, NFS translator credentials, and 32-bit compatibility syscall wrappers on affected architectures. Reference-count and keyring leak tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_inode.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_inode.c

## Purpose
This Linux file provides stubs for legacy inode syscalls that OpenAFS exposes on some platforms: create, open, and increment/decrement.

## Important APIs, types, and functions
- `afs_syscall_icreate(long a, long b, long c, long d, long e, long f)`
- `afs_syscall_iopen(int a, int b, int c)`
- `afs_syscall_iincdec(int a, int v, int c, int d)`

## Control flow and behavior
All three functions ignore their arguments and return `0`. There is no actual inode manipulation in this Linux implementation.

## State and persistence
No state is read or written. No persistent inode changes occur through these stubs.

## Dependencies and integration points
The file includes OpenAFS inode/stat headers so the symbols satisfy portable syscall dispatch references. It prevents link failures where the common syscall layer expects these platform hooks.

## Risks
Returning success for no-op inode operations can mislead callers if any Linux path still expects real side effects. The risk is mitigated if these syscalls are obsolete or unreachable for Linux cache configurations.

## Test signals
Build/link tests are the primary signal. If ioctl/syscall dispatch exposes these calls, smoke tests should verify expected user-visible behavior and ensure no caller relies on real inode creation/open/increment semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_inode.h -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_inode.h

## Purpose
This header is empty in this source snapshot. It exists as a Linux platform include placeholder for code that includes `afs/osi_inode.h`.

## Important APIs, types, and functions
There are no declarations, macros, types, or functions in the file.

## Control flow and behavior
No control flow exists.

## State and persistence
No state exists.

## Dependencies and integration points
Its only integration role is path/name compatibility for includes in files such as `osi_inode.c`.

## Risks
The main risk is false assumptions by maintainers: adding Linux inode declarations elsewhere while this header remains empty may hide missing prototypes depending on include order.

## Test signals
Compile coverage is sufficient; missing-prototype warnings in Linux inode/syscall code would indicate this placeholder needs content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_ioctl.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_ioctl.c

## Purpose
This file creates the Linux procfs ioctl endpoint used to pass OpenAFS syscall requests from userspace into kernel `afs_syscall`.

## Important APIs, types, and functions
- `afs_ioctl` validates ioctl command numbers, copies `struct afsprocdata` or compat `struct afsprocdata32` from userspace, and calls `afs_syscall`.
- `afs_unlocked_ioctl` adapts the modern file ioctl signature.
- `afs_syscall_ops` is either `struct proc_ops` or `struct file_operations` depending on kernel support.
- `osi_ioctl_init` creates the proc entry named `PROC_SYSCALL_NAME`.
- `osi_ioctl_clean` removes that proc entry.

## Control flow and behavior
The ioctl path accepts only `VIOC_SYSCALL` and `VIOC_SYSCALL32`. On 32-bit compatibility syscalls when `NEED_IOCTL32` is enabled, it copies the 32-bit argument structure and widens fields before dispatching. Otherwise it copies the native structure. Copy failures return `-EFAULT`, bad commands return `-EINVAL`, and `afs_syscall` returns the actual AFS operation result.

## State and persistence
The file creates/removes a procfs node under `openafs_procfs`. It does not persist data beyond the proc entry lifecycle.

## Dependencies and integration points
It depends on `openafs_procfs` from `osi_proc.c` or PAG module init, compatibility wrappers in `osi_compat.h`, Linux procfs ioctl operations, `copy_from_user`, and the common `afs_syscall` dispatcher.

## Risks
The proc entry is created with mode `0666`, so validation must rely on `afs_syscall` and downstream authorization. Compat argument translation must match userspace structure layout exactly. The init code does not report failure if proc creation returns NULL, so later user tools may fail with missing endpoint.

## Test signals
Test native and compat ioctl dispatch, invalid command rejection, bad user pointer `-EFAULT`, proc entry create/remove on module load/unload, and permission/authorization behavior for privileged and unprivileged callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_machdep.h -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_machdep.h

## Purpose
This Linux machine-dependent header maps portable OpenAFS OS abstractions to Linux task, signal, time, inode, credential, user-copy, vnode, uid/gid, and syscall-compatibility APIs.

## Important APIs, types, and functions
- Process/signal macros: `getpid`, `getppid`, `RECALC_SIGPENDING`, `SIG_LOCK`, `SIG_UNLOCK`, `TASK_STRUCT_RLIM`.
- Time helpers: `osi_Time`, `osi_GetTime`, inode timestamp accessors.
- Vnode/inode macros: `VN_HOLD`, `VN_RELE`, `vType`, `vSetType`, `IsAfsVnode`, `afs_suser`, and `wakeup`.
- User-copy helpers: `copyin`, `copyinstr`, and `copyout`.
- `afs_in_compat_syscall` detects 32-bit syscall mode on supported 64-bit architectures.
- Kernel print aliases: `printf` and `uprintf` to `printk`.
- Group/credential compatibility types and macros such as `GROUP_AT`, `afs_proc_t`, `afs_kuid_t`, `afs_kgid_t`, and namespace globals.

## Control flow and behavior
Most behavior is compile-time selection. The header chooses parent PID fields based on `task_struct`, signal lock locations based on kernel structure variants, time APIs based on available `ktime`/legacy calls, and compatibility syscall detection by architecture-specific thread flags or helpers. User-copy wrappers convert Linux copy return conventions into AFS-style error codes.

## State and persistence
The header owns no standalone state, but it references and mutates process signal masks, inode timestamps, and namespace/idmap globals initialized elsewhere. It affects all Linux AFS code that uses portable vnode/credential/time macros.

## Dependencies and integration points
It depends on Linux scheduler, credential, uaccess, uidgid, and time headers plus OpenAFS sysincludes. It is foundational for Linux platform code and is included before many portable AFS sources are compiled for Linux.

## Risks
Kernel structure drift is the main risk. Incorrect branch selection for signal locks, parent PID fields, rlimit location, or compat syscall detection can cause compile failures or runtime corruption. Macros such as `vSetType` directly mutate inode mode bits and must remain aligned with Linux inode rules. User namespace handling uses NULL when `current_user_ns` would require GPL-only `init_user_ns`, so uid/gid conversion behavior depends on configuration.

## Test signals
Build matrix coverage across old/new task credential models, signal structures, uid/gid namespace support, and 64-bit compat architectures is essential. Runtime signals include correct PID/PPID reporting, signal mask blocking/unblocking in sleeps, user-copy error propagation, time/timestamp updates, and `afs_in_compat_syscall` behavior for 32-bit userspace on 64-bit kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_misc.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_misc.c

## Purpose
This file contains Linux miscellaneous OSI helpers: signal masking, pathname lookup, absolute path resolution, kernel thread startup wrappers, and fatal-signal detection.

## Important APIs, types, and functions
- `osi_linux_mask` blocks all signals for the current task.
- `osi_linux_unmaskrxk` unblocks `SIGKILL` for the RX kernel listener task during shutdown.
- `osi_lookupname_internal` resolves a kernel pathname to dentry/mount references.
- `osi_lookupname` handles user/kernel path strings and returns a dentry.
- `osi_abspath` resolves a user pathname and formats its absolute path with `d_path`.
- `afs_start_thread` starts a named kernel thread with optional `AFS_GLOCK` around the target function.
- `osi_kill_pending` reports fatal pending signals when the kernel provides `fatal_signal_pending`.

## Control flow and behavior
Path lookup uses `afs_getname` for user paths, copying through `strncpy_from_user` into a kernel name buffer with `PATH_MAX` validation. `osi_lookupname_internal` builds lookup flags with `LOOKUP_FOLLOW` as requested, calls `afs_kern_path`, then extracts dentry/mount references with compatibility helpers. `osi_abspath` resolves a path, calls `afs_d_path`, stores the returned pointer in the caller output, releases references, and frees the copied name.

Thread startup wraps the requested `void (*)(void)` in a kthread function that increments the module reference count, optionally takes `AFS_GLOCK`, runs the function, drops locks/reference, and exits. Signal mask helpers use `SIG_LOCK` and `RECALC_SIGPENDING`.

## State and persistence
The file mutates the current task's signal mask and may mutate the RX listener task signal mask. It starts kernel threads and temporarily increments module references. It stores no persistent file or module state beyond globals declared elsewhere (`afs_osi_cred`, `afs_osicred_initialized`).

## Dependencies and integration points
It depends on Linux dcache/namei/kthread/signal APIs, `osi_compat.h` path helpers, OpenAFS global locking, RX listener task state, and module reference management. Lookup helpers are used by cache initialization and other path-based AFS operations.

## Risks
`afs_start_thread` does not check `kthread_run` failure, so thread start failure can be silent. Signal mask manipulation on another task (`rxk_ListenerTask`) assumes that pointer remains valid. Pathname copies from userspace must preserve negative errno conversion exactly. `osi_abspath` returns a pointer into the caller-supplied buffer after releasing dentry/mount references, which is normal for `d_path` but requires caller buffer lifetime.

## Test signals
Test user and kernel pathname lookup, follow/no-follow behavior, `ENAMETOOLONG` and bad pointer cases, absolute path formatting, kthread startup with and without `AFS_GLOCK`, module unload sequencing, RX listener shutdown signal unmasking, and fatal-signal detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_module.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_module.c

## Purpose
This file is the main Linux OpenAFS filesystem kernel module entry/exit implementation. It initializes global OSI state, syscall hooks, inode cache, filesystem registration, proc/ioctl/sysctl/keyring/pagecopy support, NFS translator hooks, and tears them down on unload.

## Important APIs, types, and functions
- Globals: `afs_global_lock`, `afs_global_owner`, `afs_ns`, and optionally `afs_mnt_idmap`.
- `afs_init_idmap` records the mount idmap from the current fs root for idmapped setattr compatibility.
- `afs_init` is the `module_init` function.
- `afs_cleanup` is the `module_exit` function.
- Module metadata declares the OpenAFS license URL and description.

## Control flow and behavior
Initialization records the current user namespace and mount idmap where configured, calls `osi_Init`, initializes `CellLRU`, initializes NFS translator server hooks unless disabled, installs syscall support, initializes the inode cache, registers `afs_fs_type`, then initializes sysctl, keyring, procfs, ioctl proc endpoint, and background pagecopy support. Error handling unwinds syscall/inode-cache/filesystem setup for early failures.

Cleanup runs the reverse-ish sequence: shutdown pagecopy, keyring, sysctl, syscall support, filesystem registration, inode cache, NFS translator hooks, sleep subsystem, tracked allocator memory, ioctl endpoint, and procfs entries.

## State and persistence
The module maintains global lock ownership, namespace/idmap pointers, registered filesystem/proc/sysctl/keyring state, inode caches, syscall hooks, NFS auth hooks, pagecopy thread, sleep events, and tracked allocations. Persistent user data is not written here; cache/filesystem persistence is handled in lower layers.

## Dependencies and integration points
It integrates all Linux AFS platform components plus the portable cache manager. It depends on `afs_fs_type`, `osi_syscall_*`, `afs_init_inodecache`, `register_filesystem`, sysctl/proc/ioctl/pagecopy/keyring functions, NFS translator hooks, and allocator/sleep shutdown functions.

## Risks
Initialization error unwinding covers early stages but later init calls such as sysctl/keyring/proc/ioctl/pagecopy do not propagate failures. Cleanup order matters: currently `osi_syscall_clean` runs before filesystem unregister and inode cache destruction, while proc/ioctl cleanup occurs after allocator cleanup; any active proc/ioctl use during unload must be quiesced by module reference handling elsewhere. Stored namespace/idmap pointers assume the chosen root context remains valid enough for later setattr wrappers.

## Test signals
Module load/unload tests with and without keyring/NFS translator/idmapped support, failure injection at syscall/inodecache/register_filesystem stages, proc/sysctl/ioctl availability after init, pagecopy thread creation/shutdown, filesystem mount/unmount, and leak checks after unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_nfssrv.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_nfssrv.c

## Purpose
This file installs Linux NFS server authentication hooks for the OpenAFS NFS translator. It tracks active `nfsd` kernel threads, captures client credentials/address during RPC authentication, maps them to AFS PAG/UID state, and restores original auth operations on shutdown.

## Important APIs, types, and functions
- Module parameter `authtab_addr` supplies the kernel `authtab` address if the weak symbol is unavailable.
- `struct nfs_server_thread` records nfsd pid, active flag, latest client address/auth fields, mapped AFS UID/PAG, and handler result.
- `find_nfs_thread(create)` verifies current is an `nfsd` kernel thread, finds/creates its tracking record, and links it in `nfssrv_list`.
- `svcauth_afs_accept` wraps original `auth_ops.accept`, captures RPC credential/client data, and calls `afs_nfsclient_reqhandler`.
- `osi_linux_nfs_initreq` applies captured NFS translator state to an AFS request.
- `osi_linux_nfssrv_init` clones and registers replacement `auth_ops` for each flavor.
- `osi_linux_nfssrv_shutdown` restores originals and frees tracking state.

## Control flow and behavior
Init locates `authtab` via weak symbol or module parameter, initializes `afs_xnfssrv`, iterates auth flavors, holds each original owner module, allocates a clone of its `auth_ops`, replaces `.owner` with OpenAFS and `.accept` with `svcauth_afs_accept`, unregisters the original flavor, and registers the clone. On each accepted RPC, the wrapper first delegates to the original accept; if successful, it finds the nfsd tracking record under `AFS_GLOCK`, captures IPv4 address, auth flavor, uid/gid/groups, maps anonymous uid -1 to -2, calls `afs_nfsclient_reqhandler`, stores success/error code and AFS uid, and returns `SVC_OK` so later request initialization can enforce access.

`osi_linux_nfs_initreq` checks current nfsd state, returns no-op for inactive threads, and when active sets the request code and marks credentials as `NFSXLATOR_CRED` with the mapped AFS uid.

## State and persistence
Runtime state includes `afs_authtab`, cloned/original auth operation arrays, `nfssrv_list`, `whine_memory`, and `afs_xnfssrv`. Each nfsd thread record persists until shutdown and is updated per RPC. No disk state is written.

## Dependencies and integration points
This code depends on Linux SunRPC `auth_ops`, `svc_auth_register/unregister`, nfsd task identity, OpenAFS locks/allocation/credentials, and `afs_nfsclient_reqhandler`. It is initialized by `osi_module.c` unless `AFS_NONFSTRANS` is defined and has stubs elsewhere for the standalone PAG module.

## Risks
Hooking global SunRPC auth tables is invasive and version-sensitive. If `authtab` is missing, translator hooks are silently skipped after warnings. Thread tracking is keyed by pid and may leak stale nfsd entries until module shutdown. Only IPv4 clients are accepted for mapping; non-IPv4 requests log and leave access denied state. Auth operation clone/restore ordering must be correct to avoid disrupting NFS server auth. Concurrent RPCs on the same nfsd thread update a single record.

## Test signals
Test NFS translator access through multiple auth flavors, missing and supplied `authtab_addr`, IPv4 and non-IPv4 clients, anonymous uid mapping, multiple nfsd threads, module unload restoring original auth ops, and failure paths for allocation and `afs_nfsclient_reqhandler`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_nfssrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_pag_module.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_pag_module.c

## Purpose
This file implements a standalone Linux kernel module for OpenAFS PAG management without the full filesystem client. It initializes syscall/ioctl/proc support, starts the PAG manager, and provides stubs for NFS translator symbols needed by shared code.

## Important APIs, types, and functions
- Module parameters `nfs_server_addr` and `this_cell` configure standalone PAG manager behavior.
- Globals: `afs_global_lock`, `openafs_procfs`, `afs_global_owner`, and optional `afs_ns`.
- `afspag_init` is the standalone module init function.
- `afspag_cleanup` is the standalone module exit function.
- Stub `osi_linux_nfs_initreq` always denies with `EACCES`.
- Stub `afs_nfsclient_reqhandler` returns `EINVAL`.

## Control flow and behavior
Initialization records the current user namespace if applicable, calls `osi_Init`, installs syscall support, creates `/proc/fs/openafs` or equivalent based on `proc_root_fs` availability, installs the ioctl endpoint, initializes `afspag` with the configured NFS server address, and optionally sets the primary cell. Cleanup removes syscall hooks, frees tracked allocations, removes the ioctl entry and proc directory, and returns.

## State and persistence
State is limited to module globals, procfs entries, syscall hooks, allocator state, and PAG manager state initialized by `afspag_Init`. There is no filesystem registration or disk cache state.

## Dependencies and integration points
The standalone module shares OSI/syscall/ioctl/proc and PAG code with the full Linux module but does not initialize the AFS filesystem, inode cache, pagecopy thread, keyring hooks, or NFS translator. The NFS stubs satisfy references from common initialization code that is not actually reached.

## Risks
Init does not check `proc_mkdir` or `osi_ioctl_init` success. Cleanup order calls `osi_linux_free_afs_memory` before `osi_ioctl_clean`, so any unexpectedly live ioctl/proc user would be risky. The stubs deliberately deny NFS translator behavior; accidental use in a translator context would fail.

## Test signals
Load/unload the standalone PAG module, verify proc/ioctl endpoint creation/removal, run PAG creation/query user tools, test `this_cell` and `nfs_server_addr` parameters, and ensure no filesystem registration side effects occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_pag_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_pagecopy.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_pagecopy.c

## Purpose
This file implements asynchronous background copying from disk-cache pages to AFS pages for Linux readahead/readpage paths. It lets readpages queue copies that wait for backing cache pages to unlock, then uses workqueue jobs to copy page data without blocking the original readahead caller.

## Important APIs, types, and functions
- `struct afs_pagecopy_page` links one cache page to one target AFS page.
- `struct afs_pagecopy_task` groups pages for one higher-level read/readahead task and owns workqueue state, page lists, refcount, and a spinlock.
- `afs_pagecopy_init_task` allocates and initializes a task.
- `afs_pagecopy_queue_page` references pages, queues them on the task, adds the task to the global check queue, and wakes the monitor thread.
- `afs_pagecopy_put_task` drops task references and frees on zero.
- `afs_pagecopy_checkworkload` moves unlocked cache pages to copy-ready lists and schedules work.
- `afs_pagecopy_worker` copies page contents, marks target page state, unlocks target pages, drops references, and frees page records.
- `afs_pagecopy_thread` monitors queued tasks, waits for locked cache pages, and sleeps on a waitqueue.
- `afs_init_pagecopy` and `afs_shutdown_pagecopy` start/stop the background thread.

## Control flow and behavior
Callers create a task, queue page pairs, and eventually drop their task reference. Queueing increments page references and, if the task is not already on the global workload list, adds it with an extra task reference. The monitor thread repeatedly scans all tasks. For each queued page whose cache page is unlocked, it moves the page to `copypages`, increments the task reference, and schedules the task work item. If a page remains locked, it records one cache page to wait on. Tasks with no more check pages are removed from the global queue and their queue reference is released.

Workers drain `copypages` under the task lock. For each page, if the cache page is uptodate, they call `copy_highpage`, flush target dcache, clear target error, and mark target uptodate. They always unlock the target AFS page, release both page references, free the page record, and finally drop the work reference. The monitor waits on a locked cache page with `afs_page_wait_locked`/`afs_put_page`, then sleeps until work is queued or the thread is stopped.

## State and persistence
Runtime state includes global waitqueue `afs_pagecopy_wq`, spinlock `afs_pagecopy_lock`, list `afs_pagecopy_tasks`, monitor thread pointer, task lists/refcounts, and page references. It mutates page uptodate/error/locked/cache coherency state. No disk state is written directly.

## Dependencies and integration points
The code depends on Linux pages, kthreads, waitqueues, workqueues, spinlocks, and compatibility helpers for folio/page waiting and `ClearPageError`. It integrates with Linux AFS VM/readahead code through prototypes in `osi_pagecopy.h` and is initialized/shutdown by `osi_module.c`.

## Risks
`afs_pagecopy_init_task` does not check `kzalloc` failure before dereferencing. `afs_pagecopy_queue_page` also assumes page record allocation succeeds. Shutdown stops the monitor thread but does not explicitly flush queued work items or drain tasks in this file, so callers/module unload ordering must guarantee no live tasks. Refcount/list locking is subtle: scheduling failure drops a reference, and task removal drops the global queue reference. Target pages are unlocked even if the cache page is not uptodate, leaving error/uptodate state dependent on prior initialization.

## Test signals
Test readahead with locked and already-unlocked cache pages, cache-page error/not-uptodate cases, multi-page tasks, concurrent queueing, module unload with outstanding pagecopy work, allocation failure injection, and lockdep/KASAN/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_pagecopy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_pagecopy.h -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_pagecopy.h

## Purpose
This header declares the Linux background pagecopy task API used by AFS VM/readahead code.

## Important APIs, types, and functions
- Forward declaration `struct afs_pagecopy_task`.
- `afs_pagecopy_init_task()`
- `afs_pagecopy_queue_page(task, cachepage, afspage)`
- `afs_pagecopy_put_task(task)`
- `afs_init_pagecopy()`
- `afs_shutdown_pagecopy()`

## Control flow and behavior
The header contains declarations only. Expected caller flow is to initialize global pagecopy support, create a task for a batch of cache-to-AFS page copies, queue page pairs, drop the task reference, and shut down support at module exit.

## State and persistence
No header-owned state exists.

## Dependencies and integration points
The declarations require Linux `struct page` to be visible to users of the header. Implementations live in `osi_pagecopy.c`, and module lifecycle calls are made from `osi_module.c`.

## Risks
The API exposes an opaque task but no explicit cancellation/drain status, so correct lifetime depends on callers following refcount conventions. The header itself does not document allocation failure behavior.

## Test signals
Compile users against the header and run the runtime pagecopy tests described for `osi_pagecopy.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_pagecopy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_probe.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_probe.c

## Purpose
This file locates Linux syscall tables when direct exported symbols or configured addresses are unavailable. It supports OpenAFS syscall and setgroups hooking on older Linux kernels by using weak symbols, module parameters, optional kallsyms lookups, and pattern scans across kernel memory.

## Important APIs, types, and functions
- Module parameters `sys_call_table_addr`, `probe_carefully`, `probe_ignore_syscalls`, and debug-only probe controls.
- Weak symbol references for `sys_call_table`, 32-bit syscall tables, syscall functions, and optional kallsyms functions.
- `tryctl` describes syscall-number/function combinations to match.
- `probectl` describes one target table, including symbol names, offsets, scan ranges, zapped/unique syscall lists, and verification syscall.
- `main_probe`, plus platform variants `ia32_probe`, `sct32_probe`, and `emu_probe`, define architecture-specific probing.
- `check_table` rejects candidate tables containing invalid text pointers.
- `try` scans for direct syscall function pointer combinations.
- `check_harder` validates candidates through unimplemented syscall equivalence, unique syscall distinctness, and verification pointer.
- `try_harder` performs pattern-only scanning and optionally rejects multiple matches.
- `scan_for_syscall_table` runs all `try` patterns and fallback hard scans.
- `do_find_syscall_table` tries weak symbol, kallsyms, module parameter, compiled-in address, primary scan, and alternate scan.
- `check_access` and `check_table_readable` validate page table readability/writability on i386/amd64.
- `osi_find_syscall_table(which)` is the public entry point.

## Control flow and behavior
For each requested probe index, `osi_find_syscall_table` selects a `probectl`, injects any module-parameter address, and calls `do_find_syscall_table`. Discovery first accepts an exported weak symbol, then optional `kallsyms_symbol_to_address`, then explicit module parameter and compiled-in addresses. If none work, it constructs a scan base/length from configured defaults or kallsyms section bounds and calls `scan_for_syscall_table`; an alternate scan range based around `scsi_command_size` is tried afterward.

Scanning first tests exact syscall function pointer combinations such as close/wait4 or close/ioctl where symbols are available. Candidate bases are range-checked against kernel text/data bounds and `check_table` skips unreadable or obviously invalid tables. If exact combinations fail, `try_harder` looks for tables where known unimplemented syscalls share one handler, unique syscalls do not duplicate other entries, and a verification syscall matches its weak function pointer. S390 variants scan even/odd alignments. On i386/amd64, the final result must be writable or hooks are not installed.

If syscall probing is disabled at compile time, `osi_find_syscall_table` returns `0`.

## State and persistence
There is no long-term state beyond module parameters and debug settings. The function returns raw kernel addresses to the syscall hook layer, which may later mutate the table. No disk state exists.

## Dependencies and integration points
This code depends on Linux architecture macros, syscall-number headers, kernel memory layout symbols such as `init_mm`, optional kallsyms, page table APIs on x86, and weak syscall function exports. It feeds `osi_syscall.c`/setgroups hook setup and is referenced in `osi_prototypes.h`.

## Risks
This is highly version- and architecture-sensitive kernel memory probing. Pattern scans can produce false positives or miss tables on changed layouts; `probe_carefully` mitigates duplicate matches but cannot make scanning inherently safe. Writability checks only exist on i386/amd64. Weak references and function descriptors differ by architecture. Hooking syscall tables is incompatible with many modern kernel hardening policies and may be blocked when tables are read-only or hidden. Incorrect `sys_call_table_addr` parameters can point at arbitrary memory.

## Test signals
Build across supported architectures and configurations with probing enabled/disabled, kallsyms available/unavailable, exported/unexported tables, and 32-bit compatibility tables. Runtime tests should verify table discovery method logs, invalid index handling, explicit module parameter addresses, read-only table rejection on x86, duplicate-match behavior with `probe_carefully`, and successful downstream syscall hook installation only when safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_proc.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_proc.c

## Purpose
This file creates Linux procfs reporting entries for OpenAFS cell database and unixuser/token state. It supports both modern `seq_file` proc operations and older `create_proc_info_entry` style output.

## Important APIs, types, and functions
- Global `openafs_procfs` stores the `/proc/fs/openafs` directory.
- CellServDB seq functions `c_start`, `c_next`, `c_stop`, and `c_show` iterate `CellLRU`.
- `afs_csdb_open` and `afs_csdb_operations` expose the cell database proc file.
- Unixuser seq functions `uu_start`, `uu_next`, `uu_stop`, and `uu_show` iterate `afs_users` and print token/exporter details.
- Legacy `csdbproc_info` renders CellServDB output without `seq_file`.
- `osi_proc_init` creates the proc directory and entries.
- `osi_proc_clean` removes entries and the proc directory.

## Control flow and behavior
Modern cell iteration locks `AFS_GLOCK` and `afs_xcell`, walks `CellLRU` to the requested sequence position, unlocks global lock while preserving the read lock until stop, and prints cell names, ids, indexes, and server IPs. Unixuser iteration locks `afs_xuser`, emits a header at position zero, walks all hash buckets, increments the user refcount while switching from global user-list lock to per-user lock, prints uid/PAG, refs, states, cell, vice id, token timestamps/auth handle, and NFS exporter/sysname details, then releases the user and reacquires list locking.

`osi_proc_init` creates `/proc/fs/openafs` using either `proc_root_fs` or a string path, then creates `unixusers` and CellServDB entries with `afs_proc_create` or legacy `create_proc_info_entry`. Cleanup removes CellServDB, optional unixusers, and the directory.

## State and persistence
Proc entries are runtime kernel objects. Output is derived from in-memory cell/user/token/exporter state; no state is stored by this file.

## Dependencies and integration points
It depends on Linux procfs/seq_file APIs, OpenAFS cell and unixuser tables, token structures, NFS client exporter data, locks `afs_xcell`/`afs_xuser`, and compatibility wrappers from `osi_compat.h`.

## Risks
Seq iteration lock choreography is delicate: start/next/stop manipulate `AFS_GLOCK` and AFS read locks across callbacks. User output touches token structures and exporter data while locks are intentionally switched, so stale references are possible if refcounting is wrong. Proc creation failure is not strongly surfaced. The legacy `csdbproc_info` does fixed-width offset accounting that can be fragile.

## Test signals
Read `/proc/fs/openafs/CellServDB` and `/proc/fs/openafs/unixusers` under populated and empty cell/user tables, concurrent token/cell updates, large user counts, NFS exporter users, proc creation/removal on load/unload, and both `seq_file` and legacy proc builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_prototypes.h

## Purpose
This Linux header declares platform OSI functions exported across the OpenAFS Linux kernel implementation. It is the shared prototype surface for allocator, credential, NFS translator, file, ioctl, misc, syscall probe, proc, sleep, sysctl, VM, vcache, vfs, vnode, and groups/keyring code.

## Important APIs, types, and functions
The header declares:
- Allocator APIs: `osi_linux_alloc`, `osi_linux_free`, `osi_linux_free_afs_memory`, `osi_linux_verify_alloced_memory`.
- Credential APIs: `crget`, `crfree`, `crdup`, `crref`, `crset`.
- NFS translator APIs and `afs_xnfssrv`.
- Cache file APIs: `osi_InitCacheInfo`, `osi_rdwr`, `afs_linux_raw_open`.
- Proc/ioctl/syscall/sysctl lifecycle APIs.
- VM and vcache helpers for flushing, smushing, storing, and resetting root vcache.
- VFS/vnode helpers: `vattr2inode`, inode cache lifecycle, `afs_fill_inode`.
- PAG/keyring APIs: `osi_keyring_init`, `osi_keyring_shutdown`, `__setpag`, optional `osi_get_keyring_pag`, and `key_type_afs_pag`.

## Control flow and behavior
There is no executable control flow. The header coordinates C compilation by making cross-file symbols visible.

## State and persistence
No state is owned here. It declares external state such as `afs_xnfssrv` and `key_type_afs_pag`.

## Dependencies and integration points
This is a central integration header for Linux OpenAFS platform files. It assumes many OpenAFS types are already declared (`struct vrequest`, `afs_ucred_t`, `struct osi_file`, `struct vcache`, etc.) and is included by code needing cross-module prototypes.

## Risks
Prototype drift is the main risk. If function signatures in implementation files change without updating this header, old-style implicit declarations or ABI mismatches can appear depending on compiler settings. Conditional keyring prototypes must match `LINUX_KEYRING_SUPPORT`.

## Test signals
Compiler warnings/errors for missing or incompatible prototypes are the primary signal. Full Linux module builds with keyring and non-keyring configs verify the conditional declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_sleep.c -->
# sources/distributed-fs/openafs/src/afs/LINUX/osi_sleep.c

## Purpose
This file implements OpenAFS sleep, timed sleep, wakeup, and wait-handle primitives on Linux using waitqueues and an event hash table keyed by event addresses.

## Important APIs, types, and functions
- `afs_osi_InitWaitHandle` initializes a wait handle.
- `afs_osi_CancelWait` cancels a wait by clearing its proc marker and waking the shared wait event.
- `afs_osi_Wait` waits for a timeout or cancellation using `afs_osi_TimedSleep`.
- `afs_evhasht` and `afs_evhashcnt` store event waitqueue records.
- `afs_getevent` and `afs_addevent` find or allocate event records.
- `afs_linux_sleep(event, killable)` implements interruptible or signal-masked sleeps.
- `afs_osi_SleepSig` and `afs_osi_Sleep` expose signal-aware and signal-blocking sleeps.
- `afs_osi_TimedSleep` sleeps with a millisecond timeout.
- `afs_osi_Wakeup` advances an event sequence and wakes waiters.

## Control flow and behavior
Events are looked up by hashing the event pointer. `afs_getevent` increments the refcount of a matching event or reuses a zero-refcount record in the bucket; `afs_addevent` allocates a new waitqueue record with a dummy event marker. Sleeping records the current event sequence, drops `AFS_GLOCK`, adjusts the current signal mask for killable or non-killable behavior, waits with freezer-aware waitqueue helpers until the sequence changes, restores the signal mask, reacquires `AFS_GLOCK`, normalizes `-ERESTARTSYS` to `EINTR`, and decrements the event refcount.

Timed sleep is similar but uses `wait_event_freezable_timeout` and does not adjust signal masks itself. Wakeup finds the event, increments its sequence only when more than one reference indicates sleepers are present, wakes the waitqueue, releases the lookup reference, and returns status codes indicating no sleepers, wake performed, or no wake.

## State and persistence
The event hash table and event records persist for module lifetime; event records are reused by setting `refcount` to zero but not freed in this file. Wait handles store a `proc` marker for cancellation. Signal masks are temporarily modified during sleeps.

## Dependencies and integration points
The code depends on Linux waitqueues, scheduler/freezer compatibility wrappers, signal locking macros from `osi_machdep.h`, OpenAFS global lock assertions, and AFS stats counters. It underlies broader cache manager waits, including dcache fetch waits and cancellation paths.

## Risks
Event records are never reclaimed here, so the table can grow with distinct event addresses until shutdown. `afs_getevent` returns NULL when no reusable record exists, forcing allocation, but allocation failure is not checked after `kzalloc` in `afs_addevent`. Wakeup requires `refcount > 1`; incorrect refcount handling can miss wakes. Signal mask manipulation must be exact or kernel threads may become unkillable/incorrectly interruptible. `afs_osi_Wait` computes end time in seconds from millisecond input, so subsecond precision is coarse.

## Test signals
Exercise sleep/wakeup with multiple waiters, timed sleep expiry, signal interruption through `SleepSig`, non-killable sleep signal masking, cancellation through wait handles, freezer behavior, many distinct event addresses, allocation failure injection, and shutdown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/LINUX/osi_sleep.c -->
