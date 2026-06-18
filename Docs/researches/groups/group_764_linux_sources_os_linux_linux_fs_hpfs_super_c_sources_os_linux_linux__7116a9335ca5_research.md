# Group Research: group_764_linux_sources_os_linux_linux_fs_hpfs_super_c_sources_os_linux_linux__7116a9335ca5

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hpfs/super.c -->
# File Research: sources/os/linux/linux/fs/hpfs/super.c

HPFS superblock, mount, remount, statfs, ioctl, and module lifecycle implementation. It wires the OS/2 HPFS filesystem into the VFS through `file_system_type`, `fs_context_operations`, and `super_operations`.

Key behavior:
- Maintains HPFS dirty/chkdsk state with `mark_dirty()` and `unmark_dirty()` by updating the spare block at sector 17.
- Centralizes filesystem error policy in `hpfs_error()`: continue, remount read-only, or panic depending on `errors=` mount option.
- Provides cycle detection helper `hpfs_stop_cycles()` for corrupt on-disk graph structures.
- Implements `hpfs_statfs()` by lazily counting free sectors from bitmap bands and free dnodes from the dnode bitmap.
- Handles HPFS-specific `FITRIM` via `hpfs_ioctl()`, gated by `CAP_SYS_ADMIN`.
- Allocates HPFS inode private objects from `hpfs_inode_cache`.

Mount interface:
- Parses `uid`, `gid`, `umask`, `case`, `check`, `errors`, `eas`, `chkdsk`, and `timeshift`.
- `hpfs_fill_super()` validates boot/super/spare blocks, loads bitmap directory and codepage table, initializes `hpfs_sb_info`, creates the root inode, and reconstructs root timestamps from the root dirent.
- Remount forbids changing `timeshift`, syncs first, updates policy fields, and marks the filesystem dirty when becoming writable.

Dependencies include HPFS helpers from `hpfs_fn.h`, block buffer mapping, bitmap helpers, fs parser APIs, VFS inode/super APIs, and user-copy helpers.

Risks and invariants:
- Mount failure paths manually unwind buffer heads and `hpfs_sb_info`; edits must preserve the `bail*` ordering.
- Dirty/clean marking is part of cross-OS recovery semantics with OS/2 chkdsk.
- `sb_timeshift` is intentionally immutable across remount.
- Bitmap free-space counts are cached and depend on HPFS bitmap integrity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hpfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hugetlbfs/Makefile -->
# File Research: sources/os/linux/linux/fs/hugetlbfs/Makefile

Small kbuild file for hugetlbfs.

Behavior:
- Builds `hugetlbfs.o` when `CONFIG_HUGETLBFS` is enabled.
- The composite object contains only `inode.o`.

Despite the comment saying “linux ramfs routines”, this directory builds hugetlbfs. Functional risk is low; changes here affect whether the hugetlbfs implementation is linked into the kernel.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hugetlbfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/hugetlbfs/inode.c -->
# File Research: sources/os/linux/linux/fs/hugetlbfs/inode.c

Full hugetlbfs implementation: a pseudo filesystem whose file contents are backed by hugetlb pages. It provides mount option parsing, inode creation, mmap/read/fallocate/truncate behavior, reservation accounting, internal kernel mounts for each hugepage hstate, and exported setup helpers for System V shared memory and similar users.

Main interfaces:
- `hugetlbfs_file_mmap()` validates hugepage alignment, installs hugetlb VMA operations, reserves pages, and extends file size for writable mappings.
- `hugetlb_get_unmapped_area()` enforces hugepage-aligned lengths and fixed addresses.
- `hugetlbfs_read_iter()` reads from hugetlb folios, returns zero-filled holes, and avoids raw HWPOISON subpages.
- `remove_inode_hugepages()`, `hugetlb_vmtruncate()`, and `hugetlbfs_punch_hole()` coordinate page-cache removal, VMA unmapping, reserve-map updates, and partial-page zeroing.
- `hugetlbfs_fallocate()` supports hole punching and preallocation by allocating huge folios through a pseudo VMA.
- `hugetlbfs_setattr()` enforces hugepage-aligned sizes and memfd seals.
- `hugetlbfs_get_inode()` creates regular, directory, symlink, and special inodes with reservation maps only where page allocations can occur.
- `hugetlb_file_setup()` creates pseudo hugetlbfs files for kernel consumers and enforces hugepage shm permission checks.

Mount behavior:
- Parses `uid`, `gid`, `mode`, `size`, `min_size`, `nr_inodes`, and `pagesize`.
- Supports byte sizes and percentages for subpool limits.
- `hugetlbfs_fill_super()` creates `hugetlbfs_sb_info`, optional subpool, root dentry, hugepage block size, and non-stacking depth.
- `init_hugetlbfs_fs()` creates the inode cache, registers the filesystem, and mounts one internal hugetlbfs instance per hstate.

Accounting and lifecycle:
- Inode allocation/deallocation maintains optional inode limits.
- Superblock teardown releases hugepage subpools.
- Eviction removes hugepages, releases reservation maps, and clears the inode.
- Migration support preserves hugetlb subpool attachment.

Concurrency and risk:
- Truncate, hole punch, and fallocate depend on `hugetlb_fault_mutex_table`, `i_mmap_rwsem`, hugetlb VMA locks, folio locks, and inode locks in carefully documented order.
- Reserve-map and subpool counts must remain synchronized with page-cache deletion.
- mmap and fallocate paths must preserve hugepage alignment and overflow checks.
- HWPOISON handling in reads deliberately returns partial safe data or `-EIO`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/hugetlbfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/init.c -->
# File Research: sources/os/linux/linux/fs/init.c

Early-init filesystem syscall substitutes. These helpers let `init/` and related kernel boot code perform filesystem operations without using user address spaces or normal file-descriptor syscall entry.

Provided helpers:
- Mount namespace operations: `init_mount()`, `init_umount()`, `init_pivot_root()`.
- Directory/root changes: `init_chdir()`, `init_chroot()`.
- Metadata operations: `init_chown()`, `init_chmod()`, `init_stat()`, `init_eaccess()`, `init_utimes()`.
- Object operations: `init_mknod()`, `init_link()`, `init_symlink()`, `init_unlink()`, `init_mkdir()`, `init_rmdir()`.
- `init_dup()` installs a kernel-held file into a new fd slot.

Implementation pattern:
- Path-based helpers use `kern_path()` and release with `path_put()`.
- Write operations acquire mount write access when needed.
- Name-based create/remove operations use `CLASS(filename_kernel, ...)` wrappers before calling internal filename helpers.
- `init_chroot()` checks execute permission, `CAP_SYS_CHROOT`, and LSM `security_path_chroot()`.

Risks:
- These functions run during early boot, so they bypass normal user-copy syscall plumbing but still need correct VFS permission, capability, LSM, and mount-write semantics.
- `init_dup()` returns `0` after installing the fd rather than the fd number, matching this internal API’s expected use.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/inode.c -->
# File Research: sources/os/linux/linux/fs/inode.c

Core VFS inode implementation. This file owns generic inode allocation, initialization, hashing, lookup, refcounting, LRU reclaim, eviction, timestamp updates, permission-related write side effects, inode-number generation, and inode cache initialization.

Major responsibilities:
- Defines and exports `empty_aops`, inode counters, inode sysctls, and optional multigrain timestamp debugfs counters.
- Initializes each inode via `inode_init_always_gfp()` and once-per-slab state via `inode_init_once()`.
- Provides generic inode allocation/freeing through `alloc_inode()`, `new_inode()`, `destroy_inode()`, and RCU delayed freeing.
- Manages link-count helpers `drop_nlink()`, `clear_nlink()`, `set_nlink()`, and `inc_nlink()` while tracking pending removals.
- Maintains inode hash table with `__insert_inode_hash()`, `__remove_inode_hash()`, `iget_locked()`, `iget5_locked()`, `ilookup*()`, `find_inode*()`, and `insert_inode_locked*()`.
- Implements inode LRU and shrinker integration through `inode_lru_list_add()`, `prune_icache_sb()`, `evict_inodes()`, and `evict()`.
- Handles final reference release in `iput()` and `iput_final()`, including lazytime sync and filesystem `drop_inode()` policy.

Timestamp and write-side policy:
- `atime_needs_update()` and `touch_atime()` enforce mount/inode noatime, relatime, nodiratime, idmap, and read-only constraints.
- `inode_update_time()`, `generic_update_time()`, `file_update_time()`, `file_modified()`, and `kiocb_modified()` update atime/mtime/ctime and i_version.
- `current_time()`, `inode_set_ctime_current()`, and `inode_set_ctime_deleg()` implement multigrain timestamp behavior.
- `file_remove_privs()` removes suid/sgid/capability privilege state on writes.

Other exported helpers:
- `bmap()`, `init_special_inode()`, `inode_init_owner()`, `inode_owner_or_capable()`, `mode_strip_sgid()`, `inode_dio_wait()`, `inode_set_flags()`, `inode_nohighmem()`, and `timestamp_truncate()`.

Concurrency and invariants:
- Lock ordering is documented at the top and spans superblock inode list lock, inode `i_lock`, inode LRU locks, writeback locks, and inode hash lock.
- Lookup paths handle `I_NEW`, `I_CREATING`, `I_FREEING`, and `I_WILL_FREE` carefully, including wait queues on inode state bits.
- Eviction requires `I_FREEING`, no LRU membership, completed writeback, page-cache cleanup, hash removal, and wakeup of waiters.
- Refcount transitions in `igrab_from_hash()` and `unlock_new_inode()` rely on memory barriers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/internal.h -->
# File Research: sources/os/linux/linux/fs/internal.h

Private VFS header shared among `fs/` implementation files. It declares internal functions and small helpers that should not be part of the public filesystem API.

Coverage:
- Block device, buffer, char device, fs context, namei, namespace, fs_struct, file table, superblock, open, inode, writeback, dcache, pipe, fs_pin, namespace fs, stat, splice, xattr, ACL, attr/idmap, anon inode, pidfs, and nsfs internal interfaces.
- Defines `struct open_flags`, xattr helper structs, stashed dentry operations, and `path_mounted()`.

Important inline helpers:
- `file_put_write_access()` and `put_file_access()` release inode and mount write/read accounting.
- `sb_start_ro_state_change()` and `sb_end_ro_state_change()` coordinate read-only remount state with memory barriers so `mnt_is_readonly()` observes consistent superblock state.

Role:
- This header is an integration map for VFS internals. Files such as `fs/init.c`, `fs/ioctl.c`, and `fs/inode.c` consume these declarations to call across fs implementation units without exposing symbols globally.

Risks:
- Declarations here encode private coupling. Signature changes must be coordinated with all implementation and call sites.
- The read-only remount helpers depend on paired barriers documented in comments; weakening them can break mount write-access correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ioctl.c -->
# File Research: sources/os/linux/linux/fs/ioctl.c

Generic VFS ioctl syscall implementation. It handles common filesystem/file ioctls centrally, falls back to file-specific `->unlocked_ioctl`, and provides compat syscall behavior.

Core paths:
- `vfs_ioctl()` invokes `file_operations->unlocked_ioctl()` and maps `-ENOIOCTLCMD` to `-ENOTTY`.
- `ioctl_fibmap()` implements privileged FIBMAP using `bmap()`, with overflow warning.
- `fiemap_fill_next_extent()` and `fiemap_prep()` are exported helpers for filesystem `->fiemap` implementations.
- `ioctl_fiemap()` copies the user request, validates extent count, calls `inode->i_op->fiemap`, and copies results back.
- Clone/dedupe helpers call `vfs_clone_file_range()` and `vfs_dedupe_file_range()`.
- Legacy XFS preallocation ioctls are translated to `vfs_fallocate()` with `FALLOC_FL_KEEP_SIZE`.

Common ioctl dispatch:
- Handles close-on-exec, nonblocking, async notification, directory/file size query, freeze/thaw, fiemap, block size, clone, dedupe, flags, xflags, filesystem UUID, and filesystem sysfs path.
- Regular non-anon files also receive legacy file ioctls such as FIBMAP and reservation operations.
- The syscall path runs LSM hooks before dispatch.

Compat behavior:
- `compat_ptr_ioctl()` is exported for simple pointer-compatible handlers.
- `compat_sys_ioctl` special-cases `FICLONE`, x86_64 preallocation layout variants, and 32-bit flag ioctl numbers before falling back to generic or file compat handlers.

Risks:
- Any new common ioctl must consider compat argument layout and LSM impact, as the file comment warns.
- User-copy sizes for variable dedupe arrays and FIEMAP extent counts are bounded to avoid overflow or excessive allocation.
- Freeze/thaw requires `CAP_SYS_ADMIN` in the superblock user namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/Makefile -->
# File Research: sources/os/linux/linux/fs/iomap/Makefile

Kbuild file for the iomap library.

Build behavior:
- Adds `-I $(src)` so trace event headers can include local files.
- Builds `iomap.o` when `CONFIG_FS_IOMAP` is enabled.
- Core object list includes `trace.o`, `iter.o`, and `buffered-io.o`.
- With `CONFIG_BLOCK`, adds direct I/O, writeback completion, fiemap, seek, and bio helpers.
- With `CONFIG_SWAP`, adds swapfile support.

Risk:
- Configuration guards matter: non-block builds still get buffered iomap support, while block-only features are separated.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/bio.c -->
# File Research: sources/os/linux/linux/fs/iomap/bio.c

BIO-backed buffered read helper implementation for iomap.

Main behavior:
- Ends read BIOs by iterating all folio segments and calling `iomap_finish_folio_read()`.
- Defers failed buffered read completion to `failed_read_work` to avoid nested `i_lock` acquisition in filesystem error-reporting paths.
- Allocates and chains read BIOs in `iomap_bio_read_folio_range()`, merging contiguous sectors when possible and splitting when the bio is absent, non-contiguous, too large, or cannot accept another folio.
- Uses a caller-provided `bio_set` when available, otherwise `fs_bio_set`.
- Adds integrity payloads when `IOMAP_F_INTEGRITY` is set.
- Provides synchronous single-range read helper `iomap_bio_read_folio_range_sync()` with integrity verification.

Exports:
- `iomap_bio_read_folio_range`
- `iomap_bio_read_ops`
- `iomap_bio_read_folio_range_sync`

Risks:
- Failed BIO ownership transfers into the global failed-read list after locking; callers must not reuse the BIO.
- Readahead uses `__GFP_NORETRY | __GFP_NOWARN` and falls back to a single-page bio to avoid partial-page read complexity.
- Integrity allocation/free and verification must match the source iomap flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/iomap/buffered-io.c -->
# File Research: sources/os/linux/linux/fs/iomap/buffered-io.c

Buffered I/O implementation for iomap users. It handles folio state tracking, buffered reads/readahead, buffered writes, inline data, delayed-allocation cleanup, zeroing, page-mkwrite, and writeback.

Folio state:
- `struct iomap_folio_state` tracks per-block uptodate and dirty bits plus pending read/write byte counts.
- Helpers allocate/free state only when block size is smaller than folio size or partial tracking is needed.
- Range helpers set/clear/find uptodate and dirty block ranges.

Read path:
- `iomap_read_folio()` and `iomap_readahead()` drive `iomap_iter()` and submit ranges through `iomap_read_ops`.
- Handles holes, newly allocated blocks, post-EOF zeroing, inline data, fsverity metadata/zerohash synthesis, and partially uptodate folios.
- `iomap_finish_folio_read()` completes sub-folio reads and reports buffered read errors.

Write path:
- `iomap_file_buffered_write()` iterates mappings and writes user data through `iomap_write_iter()`.
- `iomap_write_begin()` obtains a folio, validates stale mappings, prepares needed blocks through zeroing or reads, and supports buffer-head fallback.
- `iomap_write_end()` marks copied ranges uptodate/dirty or updates inline data.
- Short writes revert iter state, shrink chunk size for large folios, and truncate newly allocated pagecache beyond EOF.

Delayed allocation and unshare:
- `iomap_write_delalloc_release()` scans dirty pagecache to punch only unused delalloc reservations after short writes.
- `iomap_file_unshare()` forces shared extents into private dirty pagecache via `IOMAP_UNSHARE`.

Zeroing and mmap:
- `iomap_zero_range()` and `iomap_truncate_page()` zero pagecache ranges, batching dirty folios where useful and flushing stale unwritten mappings.
- `iomap_page_mkwrite()` prepares a mapped folio for write faults and returns it locked on success.

Writeback:
- `iomap_writeback_folio()` handles EOF truncation/zeroing, starts writeback, finds dirty ranges, invokes filesystem `writeback_range`, clears dirty tracking, reports errors, and completes writeback accounting.
- `iomap_writepages()` iterates dirty folios and submits filesystem writeback, refusing reclaim-context writeback except as a warning/error path.

Risks and invariants:
- Folio private state pending counters must reach zero before free.
- Stale iomap detection prevents data corruption when extent state changes under buffered writes.
- Delalloc release requires `invalidate_lock` held write-side to avoid page-fault races.
- EOF handling avoids writing post-EOF data except fsverity metadata.
- Large-folio, sub-block dirty tracking, fsverity, buffer-head fallback, and block-device BIO helpers all share this path, so changes have broad filesystem impact.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/iomap/buffered-io.c -->