# Group Research: group_1006_linux_stable_sources_os_linux_linux_stable_fs_hpfs_super_c_sources__b113d626bb5b

Scope: `Docs/research_subset_a.md` only. All 10 listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/hpfs/super.c

This file implements HPFS filesystem registration, mount/remount parsing, superblock initialization, dirty-state management, statfs, trim ioctl handling, and HPFS inode slab setup.

Key responsibilities:
- Manages HPFS dirty/chkdsk state through sector 17 spare block updates in `mark_dirty()` and `unmark_dirty()`.
- Centralizes HPFS error policy in `hpfs_error()`, supporting continue, remount-readonly, and panic behavior.
- Provides cycle detection helper `hpfs_stop_cycles()` for corrupted on-disk graph structures.
- Counts free blocks and free dnodes by scanning HPFS bitmap sectors for `hpfs_statfs()`.
- Implements `FITRIM` in `hpfs_ioctl()` with `CAP_SYS_ADMIN` enforcement and sector-size conversion.
- Defines an HPFS-specific inode slab cache with `hpfs_alloc_inode()` and `hpfs_free_inode()`.
- Parses mount options via the modern `fs_context` API: `uid`, `gid`, `umask`, `case`, `check`, `errors`, `eas`, `chkdsk`, and `timeshift`.
- Handles remount/reconfigure in `hpfs_reconfigure()`, including rejecting `timeshift` changes.
- Initializes the superblock in `hpfs_fill_super()` by reading boot, super, and spare blocks, validating magic/version fields, loading hotfix maps, bitmap directories, optional code pages, and the root inode.

Important interactions:
- Uses HPFS helpers from `hpfs_fn.h` for sector mapping, bitmap loading, hotfix handling, root dnode lookup, inode initialization, and HPFS locking.
- Integrates with VFS through `super_operations`, `file_system_type`, `get_tree_bdev()`, `kill_block_super`, and `fs_context_operations`.
- Updates root inode timestamps and HPFS inode-private fields from the root directory entry after mounting.

Notable invariants and risks:
- HPFS uses 512-byte filesystem blocks and rejects superblock sizes at or above `0x80000000`.
- Dirty-state writes are synchronous to improve OS/2 chkdsk visibility.
- Mount error behavior is user-configurable and can intentionally continue on suspected corruption.
- `hpfs_fill_super()` has multiple buffer-head cleanup labels; correctness depends on each mapped sector being released on the matching failure path.
- Root inode setup depends on both `hpfs_read_inode()` and later root dirent lookup to finish timestamp and parent metadata.

Research notes:
- This is the operational entry point for HPFS in Linux: other HPFS files implement the metadata mechanics, while this file establishes the VFS contract, mount policy, and corruption response.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hpfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hugetlbfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/hugetlbfs/Makefile

This Makefile builds hugetlbfs when `CONFIG_HUGETLBFS` is enabled.

Key responsibilities:
- Adds `hugetlbfs.o` to the build for `CONFIG_HUGETLBFS`.
- Defines `hugetlbfs-objs := inode.o`, making `inode.c` the implementation unit for the hugetlbfs object.

Research notes:
- Despite the legacy comment mentioning ramfs routines, the build rule is narrowly scoped to hugetlbfs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hugetlbfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/hugetlbfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/hugetlbfs/inode.c

This file implements hugetlbfs, a ramfs-like filesystem backed by hugetlb pages. It covers file mapping, read behavior, hugepage reservation accounting, inode creation, truncation, hole punching, fallocate, mount option parsing, internal kernel mounts, and filesystem registration.

Key responsibilities:
- Defines mount context state for hugepage hstate selection, size/min-size limits, inode limits, ownership, and mode.
- Parses mount options: `uid`, `gid`, `mode`, `nr_inodes`, `pagesize`, `size`, and `min_size`.
- Implements `hugetlbfs_file_mmap()` with hugepage-aligned offsets, overflow checks, reservation via `hugetlb_reserve_pages()`, and size growth on writable mappings.
- Implements `hugetlb_get_unmapped_area()` with hugepage alignment requirements.
- Provides `hugetlbfs_read_iter()`, which reads hugetlb folios from page cache, zero-fills holes, and avoids raw HWPOISON subpages.
- Rejects normal buffered write begin/end paths; file population occurs through mmap faults and fallocate-style allocation.
- Removes hugepages from page cache during truncate, eviction, and hole punch while coordinating with hugetlb fault mutexes and VMA locks.
- Implements `hugetlbfs_fallocate()` for both preallocation and `FALLOC_FL_PUNCH_HOLE`.
- Enforces seals for grow, shrink, and write/future-write constraints in `hugetlbfs_setattr()` and hole punching.
- Creates regular files, directories, symlinks, special files, and tmpfiles using simple filesystem helpers plus hugetlb-specific reservation maps.
- Tracks inode limits using `hugetlbfs_dec_free_inodes()` and `hugetlbfs_inc_free_inodes()`.
- Implements `statfs`, mount option display, superblock teardown, inode slab cache setup, and filesystem registration.

Important interactions:
- Depends on hugetlb MM APIs for hstate lookup, hugepage allocation, reservation, subpool creation, migration, page cache insertion, and VMA unmapping.
- Uses `simple_*` VFS helpers for directory behavior while adding hugetlb-specific inode setup and reservation maps.
- Maintains internal kernel mounts in `hugetlbfs_vfsmount[]`, one per hstate where possible.
- Exposes `hugetlb_file_setup()` for kernel users such as SysV shared memory with `SHM_HUGETLB`.

Notable invariants and risks:
- File sizes and offsets must be hugepage aligned for truncation and mapping.
- Reservation accounting is subtle: truncate and hole punch differ in how reserve maps are released.
- Hole punch must coordinate with page faults and VMAs to avoid retaining mapped pages for removed ranges.
- Internal hugetlbfs mounts for non-default hstates are optional; default hstate mount is required.
- `hugetlbfs_fill_super()` uses `kfree(sbinfo->spool)` on an allocation failure path even though normal teardown uses `hugepage_put_subpool()`; this is worth checking against the exact ownership semantics of `hugepage_new_subpool()` in this kernel tree.

Research notes:
- This file is the bridge between VFS file semantics and hugetlb memory accounting. The most important logic is not pathname handling but synchronization among page cache, VMA mappings, reservation maps, and subpool/global hugepage counts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/hugetlbfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/init.c -->
# File Research: sources/os/linux/linux-stable/fs/init.c

This file provides init-only wrappers that mimic filesystem syscalls without using user address space path pointers or regular syscall file descriptor entry points. It is used by early init and related kernel startup code.

Key responsibilities:
- Implements init-time mount namespace operations: `init_mount()`, `init_umount()`, and `init_pivot_root()`.
- Implements current-root and current-working-directory changes through `init_chdir()` and `init_chroot()`.
- Provides init-time metadata operations: `init_chown()`, `init_chmod()`, `init_eaccess()`, `init_stat()`, and `init_utimes()`.
- Provides init-time creation/removal helpers: `init_mknod()`, `init_link()`, `init_symlink()`, `init_unlink()`, `init_mkdir()`, and `init_rmdir()`.
- Provides `init_dup()` to allocate a file descriptor for an existing kernel `struct file`.

Important interactions:
- Uses `kern_path()` for kernel-space pathname lookup.
- Calls internal VFS helpers declared in `fs/internal.h`, including `path_mount()`, `path_umount()`, `path_pivot_root()`, `filename_*at()` helpers, `chmod_common()`, and `chown_common()`.
- Checks permissions and security hooks for `chdir`, `chroot`, and write-intent operations.
- Uses `CLASS(filename_kernel, ...)` cleanup wrappers for kernel pathname objects.

Notable invariants and risks:
- Functions are marked `__init`, so they are intended only for boot/init lifecycle.
- These helpers intentionally avoid normal syscall user-copy paths.
- `init_chroot()` still enforces `CAP_SYS_CHROOT` and `security_path_chroot()`.

Research notes:
- This is a compact but important early-boot adapter layer between init code and normal VFS internals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/inode.c

This file implements the core Linux VFS inode cache: inode allocation, initialization, hashing, lookup, reference release, LRU reclaim, eviction, timestamps, ownership helpers, direct-I/O waiting, and init-time inode cache setup.

Key responsibilities:
- Defines inode cache locking rules and lock ordering across inode state, superblock inode lists, inode LRU, writeback lists, and the global inode hash.
- Initializes every inode in `inode_init_always_gfp()`, including operations, mapping state, ACL/fsnotify/security fields, writeback state, counters, locks, and address-space defaults.
- Provides inode allocation/free paths: `alloc_inode()`, `new_inode()`, `destroy_inode()`, and RCU-delayed freeing.
- Maintains link count helpers: `drop_nlink()`, `clear_nlink()`, `set_nlink()`, and `inc_nlink()`, including `s_remove_count` accounting.
- Initializes address spaces and inodes once per slab object via `address_space_init_once()` and `inode_init_once()`.
- Manages inode LRU insertion, removal, isolation, page-cache reclaim from inode mappings, and superblock shrinker support in `prune_icache_sb()`.
- Implements inode hash insertion/removal and lookup APIs: `iget_locked()`, `iget5_locked()`, `iget5_locked_rcu()`, `ilookup()`, `ilookup5()`, `find_inode_nowait()`, `find_inode_rcu()`, and `find_inode_by_ino_rcu()`.
- Handles races with `I_NEW`, `I_CREATING`, `I_FREEING`, and `I_WILL_FREE` through wait queues and retry loops.
- Implements `iput()` and `iput_final()`, including lazytime sync retry, drop decisions, LRU retention, forced writeout, and eviction.
- Provides `bmap()` for block filesystems when `CONFIG_BLOCK` is enabled.
- Implements atime, mtime, ctime, lazytime, i_version, and multigrain timestamp handling.
- Provides write modification helpers: `file_remove_privs()`, `file_update_time()`, `file_modified()`, and `kiocb_modified()`.
- Initializes inode hash tables and the inode slab cache via `inode_init_early()` and `inode_init()`.
- Provides special inode setup, inode owner initialization, owner/capability checks, SGID stripping, no-highmem mapping setup, and direct-I/O wait helpers.

Important interactions:
- Touches core VFS objects: `super_block`, `inode`, `address_space`, `dentry`, `vfsmount`, writeback state, security hooks, fsnotify, ACLs, fsverity, cdev/block/pipe file operations, and debugfs/sysctl reporting.
- Exports many symbols used by filesystems throughout the kernel tree.
- Coordinates with memory reclaim via `list_lru`, `invalidate_mapping_pages()`, and inode shrinker callbacks.
- Coordinates with writeback through inode dirty state, lazytime, `inode_wait_for_writeback()`, and writeback list removal.

Notable invariants and risks:
- `inode->i_lock` protects inode state transitions; multiple paths rely on state checks plus wait-bit wakeups to avoid use-after-free or duplicate inode instantiation.
- `I_NEW` must be cleared by `unlock_new_inode()` or discarded via `discard_new_inode()`.
- Inode LRU eligibility requires zero refcount, clean state, active superblock, and shrinkable mapping.
- `iput()` can sleep and can trigger full filesystem eviction paths.
- Multigrain timestamp logic uses atomic nanosecond compare/exchange and the `I_CTIME_QUERIED` bit; correctness depends on ordering between ctime sec/nsec fields and query/update paths.
- The file contains broad VFS infrastructure, so small behavioral changes can affect nearly every filesystem.

Research notes:
- This is one of the central VFS lifecycle files. Its critical themes are object lifetime, lookup race handling, shrinker behavior, and timestamp/write-side metadata consistency.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/internal.h

This header declares internal VFS interfaces shared among files under `fs/`. It is not a public filesystem API; it connects namespace, namei, file table, superblock, inode, dcache, xattr, stat, splice, mount-idmap, and namespace filesystem internals.

Key responsibilities:
- Declares internal init hooks such as `bdev_cache_init()`, `chrdev_init()`, `filename_init()`, and `mnt_init()`.
- Declares internal namei helpers for lookup, mkdir, mknod, symlink, link, unlink, rmdir, rename, tmpfile, and no-permission lookup paths.
- Declares namespace and mount helpers: `path_mount()`, `path_umount()`, `path_pivot_root()`, `lookup_mnt()`, `finish_automount()`, and mount write-access helpers.
- Provides read-only remount synchronization helpers `sb_start_ro_state_change()` and `sb_end_ro_state_change()` with explicit memory barriers.
- Declares file table helpers for empty/backing file allocation and close/fput variants.
- Provides inline write-access release helpers `file_put_write_access()` and `put_file_access()`.
- Declares inode, writeback, dcache, pipe, fs pin, nsfs, stat, splice, xattr, idmap, stashed dentry, anon inode, pidfs, and nsfs internal hooks.
- Defines internal structures such as `open_flags`, `xattr_name`, `kernel_xattr_ctx`, and `stashed_operations`.
- Provides `path_mounted()` helper to identify mount roots.

Important interactions:
- Used by `fs/init.c`, `fs/ioctl.c`, `fs/inode.c`, and many other VFS implementation files.
- Bridges otherwise separate VFS implementation units while avoiding public exposure in `include/linux/fs.h`.

Notable invariants and risks:
- Memory barriers in `sb_start_ro_state_change()` and `sb_end_ro_state_change()` pair with mount read-only checks and write-access acquisition paths.
- Helpers in this header are internal contracts; changing prototypes or semantics can cascade across core VFS code.
- `put_file_access()` encodes mode-specific release behavior for read counts, writers, and backing files.

Research notes:
- This header is best understood as the VFS private linkage surface. It reveals subsystem boundaries and dependency directions inside `fs/`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/ioctl.c

This file implements the generic VFS ioctl syscall path and common filesystem/file ioctl commands before dispatching to filesystem-specific handlers.

Key responsibilities:
- Provides `vfs_ioctl()` wrapper for `file_operations->unlocked_ioctl`, translating `-ENOIOCTLCMD` to `-ENOTTY`.
- Implements privileged `FIBMAP` handling through `bmap()` and `CAP_SYS_RAWIO`.
- Implements FIEMAP helpers: `fiemap_fill_next_extent()`, `fiemap_prep()`, and `ioctl_fiemap()`.
- Implements file clone and clone-range ioctls through `vfs_clone_file_range()`.
- Implements legacy XFS-style preallocation ioctls through `vfs_fallocate()`.
- Handles `FIONBIO`, `FIOASYNC`, `FIOQSIZE`, filesystem freeze/thaw, dedupe range, filesystem UUID, and filesystem sysfs path ioctls.
- Dispatches generic ioctls in `do_vfs_ioctl()` and falls back to file-specific or filesystem-specific ioctl handlers.
- Implements native `sys_ioctl` and compat `compat_sys_ioctl`.
- Exports `compat_ptr_ioctl()` for file operations whose ioctl arguments are pointer-compatible between native and compat modes.

Important interactions:
- Calls LSM hooks `security_file_ioctl()` and `security_file_ioctl_compat()` before ioctl dispatch.
- Uses file attribute helpers from `fileattr.h` for `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, and `FS_IOC_FSSETXATTR`.
- Coordinates freeze/thaw through superblock operations or generic `freeze_super()` / `thaw_super()`.
- Uses `copy_from_user()`, `copy_to_user()`, `get_user()`, and `put_user()` heavily because this is the syscall boundary.

Notable invariants and risks:
- `FIEMAP_MAX_EXTENTS` avoids 32-bit overflow in extent array sizing.
- `FICLONE` takes an integer fd argument, so compat handling must not blindly `compat_ptr()` it.
- Dedupe range allocation is capped to one page.
- `FIONREAD` for regular files reports `i_size - f_pos`, while non-regular and anonymous cases dispatch to file-specific ioctl handling.
- New common ioctls must be audited for compat layout and LSM impact, as noted in the file comments.

Research notes:
- This is the generic ioctl funnel for VFS. It standardizes common file/filesystem commands and isolates compat-specific traps before invoking filesystem-private ioctl code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/iomap/Makefile

This Makefile builds the iomap library objects according to enabled kernel configuration options.

Key responsibilities:
- Adds include path `-I $(src)` for trace event headers.
- Builds `iomap.o` when `CONFIG_FS_IOMAP` is enabled.
- Always includes `trace.o`, `iter.o`, and `buffered-io.o` in the iomap core object.
- Adds block-backed helpers when `CONFIG_BLOCK` is enabled: `direct-io.o`, `ioend.o`, `fiemap.o`, `seek.o`, and `bio.o`.
- Adds `swapfile.o` when `CONFIG_SWAP` is enabled.

Research notes:
- `buffered-io.c` is part of the core iomap library, while `bio.c` is only built for block-enabled kernels.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/bio.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/bio.c

This file implements BIO-backed buffered read helpers for iomap.

Key responsibilities:
- Completes buffered read BIOs by iterating all folios and calling `iomap_finish_folio_read()`.
- Defers failed read completions to workqueue context through `failed_read_work` to avoid nested inode-lock acquisition in filesystem error reporting.
- Allocates and submits read BIOs for contiguous folio ranges in `iomap_read_alloc_bio()` and `iomap_bio_read_folio_range()`.
- Supports caller-provided BIO sets through `iomap_read_folio_ctx->ops->bio_set`, otherwise uses `fs_bio_set`.
- Handles readahead allocation flags and marks BIOs with `REQ_RAHEAD` when appropriate.
- Supports metadata/data integrity payloads when the iomap has `IOMAP_F_INTEGRITY`.
- Provides synchronous single-folio range reads through `iomap_bio_read_folio_range_sync()`.

Important interactions:
- Exports `iomap_bio_read_folio_range`, `iomap_bio_read_ops`, and sync read helper for use by buffered iomap code and filesystems.
- Depends on `iomap_sector()`, `iomap_max_bio_size()`, and the current `iomap_iter` mapping.
- Integrates with folio completion logic in `buffered-io.c`.

Notable invariants and risks:
- BIO coalescing requires contiguous sectors and enough remaining max BIO size.
- Failed reads are queued after dropping the spinlock; ownership of the BIO transfers to the failure work item.
- Allocation fallback retries a single-page BIO after larger BIO allocation failure to avoid partial-page read complexity.

Research notes:
- This file is the block-device read submission backend for iomap buffered reads; higher-level folio state tracking lives in `buffered-io.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/buffered-io.c -->
# File Research: sources/os/linux/linux-stable/fs/iomap/buffered-io.c

This file implements iomap buffered I/O over folios: buffered reads, readahead, buffered writes, dirty tracking, invalidation, delayed-allocation release, zeroing, page-mkwrite, and writeback.

Key responsibilities:
- Defines `struct iomap_folio_state`, which tracks per-block uptodate and dirty bits plus pending read/write byte counts for folios larger than filesystem blocks.
- Provides helpers to allocate/free folio private state, mark ranges uptodate or dirty, locate dirty/clean/uptodate ranges, and clear dirty subranges.
- Adjusts read ranges to skip already-uptodate blocks and avoid reading beyond EOF.
- Handles inline data reads through `iomap_read_inline_data()`.
- Completes reads via `iomap_finish_folio_read()`, including filesystem error reporting and per-folio pending-byte accounting.
- Implements `iomap_read_folio()` and `iomap_readahead()` using `iomap_iter` plus pluggable read operations.
- Provides partial-uptodate checks for filesystems with sub-folio block state.
- Implements buffered write begin/end paths, including stale iomap validation, optional buffer-head fallback, inline write handling, short-copy retry behavior, folio sizing, and page-cache size extension.
- Exports `iomap_file_buffered_write()` as the generic buffered write implementation.
- Provides delayed-allocation cleanup in `iomap_write_delalloc_release()`, preserving dirty cached ranges while punching unused delalloc reservations.
- Implements unshare, zero-range, truncate-page zeroing, and page-mkwrite support.
- Implements writeback helpers: per-folio writeback initialization, completion, dirty-range iteration, EOF handling, and `iomap_writepages()`.

Important interactions:
- Uses iomap iteration callbacks from filesystems to translate logical file ranges into mapping state.
- Calls BIO-backed read helpers from `bio.c` for synchronous or asynchronous reads when custom write/read ops are absent.
- Coordinates with page cache APIs, folio locking, writeback iteration, dirty throttling, invalidate locks, and filesystem error reporting.
- Supports both pure iomap folio state and buffer-head compatibility via `IOMAP_F_BUFFER_HEAD`.

Notable invariants and risks:
- Per-block dirty and uptodate state is mandatory for correctness when filesystem block size is smaller than folio size.
- Read completion must avoid marking the whole folio uptodate while asynchronous read bytes are still pending.
- Delalloc release requires the caller to hold `mapping->invalidate_lock` for write to prevent page faults from dirtying folios after reservation punching.
- Write begin must revalidate stale mappings to avoid data corruption after concurrent extent conversion or reclaim.
- EOF writeback handling must avoid repeatedly writing folios entirely beyond `i_size`, including large offsets on 32-bit systems.
- Writeback from reclaim context is refused with a warning because iomap writeback should not run from direct reclaim.

Research notes:
- This is the core buffered-I/O engine for iomap-based filesystems. Its main complexity is maintaining byte/block-level correctness across large folios, delayed allocation, mmap faults, writeback, EOF, and concurrent extent-state changes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/iomap/buffered-io.c -->