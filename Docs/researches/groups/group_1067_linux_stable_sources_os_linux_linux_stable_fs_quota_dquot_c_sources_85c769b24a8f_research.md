# Group Research: group_1067_linux_stable_sources_os_linux_linux_stable_fs_quota_dquot_c_sources_85c769b24a8f

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/dquot.c -->
# File Research: sources/os/linux/linux-stable/fs/quota/dquot.c

## Purpose
Implements the generic VFS disk quota core: dquot cache management, quota format registration, quota on/off, inode dquot attachment, quota accounting for block/inode allocation, quota ownership transfer, dirty writeback, user-visible quota state, and exported `dquot_operations` / `quotactl_ops`.

## Main Responsibilities
- Maintains global quota format registry via `register_quota_format`, `unregister_quota_format`, and module autoload in `find_quota_format`.
- Maintains dquot lifetime through hash table, `inuse_list`, `free_dquots`, `releasing_dquots`, dirty lists, slab cache, shrinker, and delayed release workqueue.
- Provides `dqget`, `dqgrab`, `dqput`, `dquot_acquire`, `dquot_commit`, `dquot_release`, and invalidation/writeback helpers.
- Attaches dquots to inodes using `i_dquot()` under `dq_data_lock` with `dquot_srcu` protection.
- Accounts allocation/freeing of blocks, reserved space, and inodes with limit enforcement and delayed warning emission.
- Implements transfer of usage between dquots for ownership changes.
- Implements quota enable/disable/resume and setup/cleanup of quota inode state.
- Exposes generic quota query/update operations for quota sysfile users.

## Key Concurrency Model
The file documents and enforces quota lock ordering:
- `dq_data_lock > dq_list_lock > inode->i_lock > dquot->dq_dqb_lock`
- `dq_list_lock > dq_state_lock`
- broader ordering: `s_umount > i_mutex > journal_lock > dquot->dq_lock > dqio_sem`

Important patterns:
- Inode dquot pointers are SRCU-protected.
- `DQ_RELEASING_B` prevents invalidation races during delayed release.
- `dquot->dq_lock` serializes disk read/write/release of an individual dquot.
- `dq_state_lock` protects quota on/off state transitions.

## Notable Functions
- `dqget()`: resolves or creates a cached active dquot for a `kqid`, waits for pending release, and acquires on-disk state as needed.
- `dqput()`: drops references and queues delayed release for last reference.
- `dquot_writeback_dquots()`: drains dirty dquot lists and writes quota metadata.
- `__dquot_initialize()`: attaches user, group, and project dquots to an inode.
- `__dquot_alloc_space()`, `dquot_alloc_inode()`, `__dquot_free_space()`, `dquot_free_inode()`: core accounting paths.
- `__dquot_transfer()` / `dquot_transfer()`: move usage when uid/gid ownership changes.
- `dquot_load_quota_inode()` / `dquot_load_quota_sb()`: turn quota accounting/enforcement on.
- `dquot_disable()` / `dquot_quota_off()`: suspend or turn quota off and invalidate cached dquots.
- `dquot_get_dqblk()`, `dquot_set_dqblk()`, `dquot_get_state()`, `dquot_set_dqinfo()`: generic user-facing quota operations.

## Interactions
Uses filesystem-supplied `quota_read`, `quota_write`, `dq_op`, and `s_qcop` hooks. Delegates on-disk format handling to registered quota format ops. Sends quota warnings through `quota_send_warning()` from `netlink.c`.

## Edge Cases
- Refuses quota files on encrypted inodes.
- Filesystems outside `init_user_ns` are not supported for VFS quota load.
- Handles quota file page-cache invalidation because quota I/O bypasses ordinary cached writes.
- Supports quota suspension separately from full quota disable.
- Root hardlimit bypass can be suppressed for old-format quotas with `DQF_ROOT_SQUASH`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/dquot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/kqid.c -->
# File Research: sources/os/linux/linux-stable/fs/quota/kqid.c

## Purpose
Provides exported helper operations for kernel quota identifiers, abstracting over user, group, and project quota ID types.

## Key Functions
- `qid_eq()`: compares two `struct kqid` values by type and then by uid/gid/projid equality.
- `qid_lt()`: total ordering helper across quota type and typed ID value.
- `from_kqid()`: maps a kernel quota ID into a target user namespace, returning `(qid_t)-1` if unmapped.
- `from_kqid_munged()`: maps a kernel quota ID into a target namespace, returning overflow IDs rather than failure.
- `qid_valid()`: checks type-specific validity.

## Dependencies
Uses Linux namespace ID helpers: `from_kuid`, `from_kgid`, `from_kprojid`, and munged/valid/equality variants.

## Notes
All helpers switch on `USRQUOTA`, `GRPQUOTA`, and `PRJQUOTA`; invalid types hit `BUG()`, reflecting that callers must pass a valid quota type.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/kqid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/netlink.c -->
# File Research: sources/os/linux/linux-stable/fs/quota/netlink.c

## Purpose
Defines the generic netlink family used by VFS quota code to notify userspace about quota warnings.

## Main Components
- Generic netlink family: `VFS_DQUOT`, version 1.
- Multicast group: `events`.
- Exported notifier: `quota_send_warning()`.

## `quota_send_warning()`
Builds and multicasts a `QUOTA_NL_C_WARNING` message with:
- quota type,
- exceeded quota ID,
- warning type,
- device major/minor,
- current uid as caused-by ID.

Allocation uses `GFP_NOFS` because warnings can be emitted from filesystem write paths where reclaim recursion could deadlock.

## Initialization
`quota_init()` registers the generic netlink family at `fs_initcall` time and logs failure if registration fails.

## Interactions
Called from `dquot.c` warning flushing after quota hard/soft limit transitions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota.c -->
# File Research: sources/os/linux/linux-stable/fs/quota/quota.c

## Purpose
Implements the syscall-facing quota control layer for `quotactl(2)` and `quotactl_fd(2)`. It validates permissions, resolves target superblocks, translates user ABI structures to internal quota control structures, and dispatches to filesystem quota operations.

## Main Responsibilities
- Permission enforcement in `check_quotactl_permission()`, allowing unprivileged reads of owned user/group quotas but requiring `CAP_SYS_ADMIN` for most operations.
- Global quota sync for `Q_SYNC` without a specific device.
- Dispatch of classic VFS quota commands and XFS-compatible quota commands.
- Conversion between:
  - `if_dqblk` and `qc_dqblk`,
  - `if_dqinfo` and `qc_info`,
  - `fs_disk_quota` and `qc_dqblk`,
  - `fs_quota_stat` / `fs_quota_statv` and `qc_state`.
- Compat ABI handling for alignment-sensitive structures and compat syscalls.
- Superblock lookup by block device for `quotactl`.
- File-descriptor-based superblock targeting for `quotactl_fd`.

## Key Dispatch Paths
- `do_quotactl()` validates quota type support and calls specific helpers for `Q_QUOTAON`, `Q_QUOTAOFF`, `Q_GETQUOTA`, `Q_SETQUOTA`, `Q_XGETQSTAT`, `Q_XSETQLIM`, etc.
- `quotactl_block()` looks up the mounted superblock for a block device and handles freeze/thaw waiting and exclusive locking for quota on/off commands.
- `quotactl_fd()` uses an already open file's mount superblock and write access guards for mutating commands.

## Edge Cases
- `Q_XQUOTASYNC` is treated as a no-op for coherent XFS-style quotas after read-only checks.
- Project quota state is squeezed into older XFS stat ABI fields only when group quota data is absent.
- Bigtime quota timer support maps high timer bits via `FS_DQ_BIGTIME`.
- `array_index_nospec()` is used before indexing quota type arrays.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota_tree.c -->
# File Research: sources/os/linux/linux-stable/fs/quota/quota_tree.c

## Purpose
Implements the shared on-disk quota trie used by VFS quota v2 formats. It manages lookup, insertion, deletion, iteration, and free-space tracking for quota records stored in fixed-size quota blocks.

## Data Model
The quota file is a radix tree:
- Internal tree blocks contain little-endian block references.
- Leaf/data blocks contain a `qt_disk_dqdbheader` followed by fixed-size quota entries.
- `QT_TREEOFF` identifies the root tree block offset.
- `qtree_mem_dqinfo` supplies block size, depth, record size, type, and format-specific callbacks.

## Main Responsibilities
- Block I/O wrappers: `read_blk()` and `write_blk()`.
- Sanity checks for free-list pointers and entry counts.
- Empty block free-list management via `get_free_dqblk()` and `put_free_dqblk()`.
- Data block free-entry list management via `insert_free_dqentry()` and `remove_free_dqentry()`.
- Record insertion through `dq_insert_tree()` and recursive `do_insert_tree()`.
- Record deletion through `qtree_delete_dquot()` and recursive `remove_tree()`.
- Lookup through `find_dqentry()`, `find_tree_dqentry()`, and `find_block_dqentry()`.
- Iteration through `qtree_get_next_id()`.

## Exported API
- `qtree_entry_unused()`
- `qtree_write_dquot()`
- `qtree_delete_dquot()`
- `qtree_read_dquot()`
- `qtree_release_dquot()`
- `qtree_get_next_id()`

## Corruption Defenses
The implementation checks:
- block number ranges,
- free-list header ranges,
- tree cycles,
- insertion into already-present entries,
- missing referenced quota IDs,
- excessive tree depth.

Errors are reported with `quota_error()` and generally return `-EIO` or `-EUCLEAN`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota_tree.h -->
# File Research: sources/os/linux/linux-stable/fs/quota/quota_tree.h

## Purpose
Defines the on-disk data-block header used by the VFS quota tree implementation.

## Key Definition
`struct qt_disk_dqdbheader` contains:
- `dqdh_next_free`: next block with free entries,
- `dqdh_prev_free`: previous block with free entries,
- `dqdh_entries`: valid entry count,
- padding to 16 bytes.

## Constant
`QT_TREEOFF` is `1`, meaning the quota tree root starts at block 1 of the quota file.

## Role
Used by `quota_tree.c` and v2 quota format support to manage leaf/data blocks in quota files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota_tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota_v1.c -->
# File Research: sources/os/linux/linux-stable/fs/quota/quota_v1.c

## Purpose
Implements support for the old VFS quota file format `QFMT_VFS_OLD`.

## Format
The quota file is a flat array of `struct v1_disk_dqblk`, indexed directly by uid/gid. Disk space limits are stored in 1 KiB quota blocks. Inode counts and limits are 32-bit fields. Grace times are stored in the record for ID 0.

## Main Functions
- `v1_disk2mem_dqblk()` and `v1_mem2disk_dqblk()`: convert between disk and in-memory quota structures.
- `v1_read_dqblk()`: reads a quota record by computed offset and marks all-zero limits as fake.
- `v1_commit_dqblk()`: writes a quota record, special-casing root user/group records to store grace times.
- `v1_check_quota_file()`: validates old-format layout and rejects files that appear to contain newer v2 magic.
- `v1_read_file_info()` / `v1_write_file_info()`: load and store global grace times and max limit metadata.

## Registration
Defines `v1_format_ops` and registers `v1_quota_format` at module init.

## Notes
This format supports user and group quotas only in its v2-magic rejection table and uses legacy fixed indexing, which makes sparse high IDs expensive/impractical compared with quota v2 trees.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota_v1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota_v2.c -->
# File Research: sources/os/linux/linux-stable/fs/quota/quota_v2.c

## Purpose
Implements VFS quota format v2 support for `QFMT_VFS_V0` and `QFMT_VFS_V1`, using the shared quota tree code.

## Format Variants
- v2r0: 32-bit inode/block limits, 64-bit current space and timers.
- v2r1: 64-bit limits/counts with an explicit pad field.
Both store block limits in 1 KiB quota blocks and convert to byte-based in-memory accounting.

## Main Responsibilities
- Validate quota file magic/version in `v2_check_quota_file()`.
- Read and write file info header in `v2_read_file_info()` and `v2_write_file_info()`.
- Allocate and initialize `qtree_mem_dqinfo` with block count, free block pointers, free-entry pointer, block size, tree depth, entry size, and format-specific callbacks.
- Convert disk quota records through v2r0/v2r1 `disk2mem`, `mem2disk`, and `is_id` callbacks.
- Delegate dquot read/write/release/iteration to `quota_tree.c`.

## Key Functions
- `v2_read_dquot()`
- `v2_write_dquot()`
- `v2_release_dquot()`
- `v2_get_next_id()`
- `v2_free_file_info()`

## Corruption Checks
`v2_read_file_info()` verifies that declared block counts and free-list pointers fit the quota file size and block range. Invalid metadata returns `-EUCLEAN`.

## Registration
Registers both v2r0 and v2r1 quota format descriptors with shared `v2_format_ops`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quota_v2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quotaio_v1.h -->
# File Research: sources/os/linux/linux-stable/fs/quota/quotaio_v1.h

## Purpose
Defines old-format VFS quota on-disk record layout and constants.

## Contents
- `MAX_IQ_TIME` and `MAX_DQ_TIME`: default inode and block grace times, both one week.
- `struct v1_disk_dqblk`: old quota record with 32-bit block/inode limits and current usage plus architecture-sized `unsigned long` timers.
- `v1_dqoff(UID)`: computes byte offset of a record by ID.

## Role
Consumed by `quota_v1.c` for direct array-style quota file reads and writes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quotaio_v1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quotaio_v2.h -->
# File Research: sources/os/linux/linux-stable/fs/quota/quotaio_v2.h

## Purpose
Defines VFS quota v2 on-disk constants and structures.

## Contents
- `V2_INITQMAGICS`: magic numbers for user, group, and project quotas.
- `V2_INITQVERSIONS`: current version values, all `1`.
- `struct v2_disk_dqheader`: file magic and version.
- `struct v2r0_disk_dqblk`: v0 quota record with 32-bit limit/count fields where applicable.
- `struct v2r1_disk_dqblk`: v1 quota record with 64-bit limits/counts.
- `struct v2_disk_dqinfo`: grace times, flags, block count, free block list head, and free-entry block list head.
- `V2_DQINFOOFF`: info header offset after the generic header.
- `V2_DQBLKSIZE_BITS`: quota tree block size shift, 10.

## Role
Used by `quota_v2.c` and `quota_tree.c` to interpret and maintain v2 quota files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/quota/quotaio_v2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/ramfs/Makefile

## Purpose
Build rules for ramfs.

## Behavior
- Always builds `ramfs.o` into `obj-y`.
- `ramfs-objs` consists of `inode.o` plus either:
  - `file-mmu.o` when `CONFIG_MMU=y`,
  - `file-nommu.o` otherwise.

## Role
Selects the correct ramfs file operation implementation for MMU vs no-MMU kernels.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/file-mmu.c -->
# File Research: sources/os/linux/linux-stable/fs/ramfs/file-mmu.c

## Purpose
Defines ramfs regular-file operations for MMU-capable systems.

## Main Components
- `ramfs_mmu_get_unmapped_area()`: delegates to `mm_get_unmapped_area()`.
- `ramfs_file_operations`: uses generic page-cache operations for read, write, mmap preparation, splice, seek, and noop fsync.
- `ramfs_file_inode_operations`: uses `simple_setattr` and `simple_getattr`.

## Design
Ramfs stores data entirely in the page cache and relies on generic VFS/MM helpers rather than filesystem-private data structures.

## Interactions
`inode.c` assigns these operations to regular ramfs inodes through `ramfs_get_inode()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/file-mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/file-nommu.c -->
# File Research: sources/os/linux/linux-stable/fs/ramfs/file-nommu.c

## Purpose
Defines ramfs regular-file operations for no-MMU systems, including support for direct/shared mappings backed by physically contiguous pages.

## Main Components
- `ramfs_mmap_capabilities()`: advertises direct, copy, read, write, and exec no-MMU mapping capabilities.
- `ramfs_nommu_expand_for_mapping()`: allocates contiguous pages for a file grown from size zero, splits high-order allocation, zeros pages, inserts them into page cache, and marks them dirty/uptodate.
- `ramfs_nommu_resize()`: handles truncation/growth and prevents shrinking over active shared mappings via `nommu_shrink_inode_mappings()`.
- `ramfs_nommu_setattr()`: handles size-changing attribute updates and normal attribute copying.
- `ramfs_nommu_get_unmapped_area()`: verifies requested pages exist and are physically contiguous, then returns a direct address or `-ENOSYS`.
- `ramfs_nommu_mmap_prepare()`: allows only no-MMU shared mappings and installs `generic_file_vm_ops`.

## File Operations
Provides read/write/splice/llseek/fsync plus no-MMU mapping hooks.

## Edge Cases
- Growth from zero is treated as likely shared mmap setup.
- Overlarge high-order allocations return `-EFBIG`.
- If page-cache folios are missing or not physically adjacent, direct mapping is refused with `-ENOSYS`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/file-nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ramfs/inode.c

## Purpose
Implements ramfs inode creation, directory operations, mount option parsing, superblock setup, filesystem context setup, and registration.

## Main Responsibilities
- `ramfs_get_inode()`: allocates and initializes ramfs inodes using `ram_aops`, unevictable mappings, timestamps, and type-specific inode/file operations.
- `ramfs_mknod()`, `ramfs_create()`, `ramfs_mkdir()`, `ramfs_symlink()`, `ramfs_tmpfile()`: implement object creation with LSM initialization and simple dentry helpers.
- Directory inode ops use simple VFS helpers for lookup, link, unlink, rmdir, rename, and tmpfile.
- `ramfs_show_options()`: reports non-default mount mode.
- `ramfs_parse_param()`: parses `mode=` and intentionally ignores unknown legacy options.
- `ramfs_fill_super()`: sets superblock limits, block size, magic, operations, dentry flags, time granularity, and root inode.
- `ramfs_init_fs_context()` / `ramfs_free_fc()`: allocate/free per-mount ramfs config.
- `ramfs_kill_sb()`: frees fs info and kills anonymous superblock.
- Registers `file_system_type` named `ramfs`.

## Mount State
`struct ramfs_fs_info` stores only mount options, currently root mode. Default mode is `0755`.

## Design
Ramfs is intentionally minimal and page-cache-backed, demonstrating a simple VFS filesystem with no persistent backing store and no custom data tree.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/ramfs/internal.h

## Purpose
Internal ramfs declaration header.

## Contents
Declares:
- `extern const struct inode_operations ramfs_file_inode_operations;`

## Role
Allows `inode.c` to reference file inode operations defined by either `file-mmu.c` or `file-nommu.c`, selected by the ramfs Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ramfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/read_write.c -->
# File Research: sources/os/linux/linux-stable/fs/read_write.c

## Purpose
Implements generic VFS read, write, seek, vector I/O, sendfile, copy_file_range, and common write/copy validation helpers.

## Major Areas
- Generic read-only file operations via `generic_ro_fops`.
- Seek helpers: `vfs_setpos`, `generic_file_llseek_size`, `generic_llseek_cookie`, `generic_file_llseek`, fixed/no-end/noop/default seek implementations, `vfs_llseek`, and lseek syscalls.
- Access validation: `rw_verify_area()` combines offset/count checks, LSM permission checks, and fsnotify permission hooks.
- Scalar I/O: `vfs_read`, `vfs_write`, `kernel_read`, `kernel_write`, `ksys_read`, `ksys_write`, `pread64`, `pwrite64`.
- Iter/vector I/O: `vfs_iter_read`, `vfs_iter_write`, `vfs_iocb_iter_read`, `vfs_iocb_iter_write`, `readv`, `writev`, `preadv`, `pwritev`, `preadv2`, `pwritev2`, plus compat variants.
- `sendfile`: implements splice-based file-to-file or file-to-pipe transfer.
- `copy_file_range`: validates ranges, tries filesystem copy, same-superblock clone, or splice fallback.
- Write validation: `generic_write_check_limits`, `generic_write_checks_count`, `generic_write_checks`, `generic_file_rw_checks`, and `generic_atomic_write_valid`.

## Important Semantics
- Clamps I/O to `MAX_RW_COUNT`.
- Uses `file_start_write()` / `file_end_write()` for write paths.
- Updates task I/O accounting and fsnotify access/modify events on success.
- Handles `FMODE_STREAM` by avoiding `f_pos`.
- Provides fallback looped `read`/`write` support for vector I/O when iter ops are unavailable.
- Enforces `RLIMIT_FSIZE`, `O_LARGEFILE`, max file size, swapfile restrictions, append restrictions, and overlap restrictions for copy operations.

## Edge Cases
- `SEEK_DATA` / `SEEK_HOLE` generic behavior treats the whole file as data and EOF as a virtual hole.
- `copy_file_range()` avoids unsafe cross-filesystem filesystem callbacks unless explicitly using splice.
- Atomic writes require ubuf iter, power-of-two length, position alignment, and direct I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/read_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/readdir.c -->
# File Research: sources/os/linux/linux-stable/fs/readdir.c

## Purpose
Implements VFS directory iteration wrappers and user ABI syscalls for reading directory entries.

## Main Responsibilities
- `iterate_dir()`: validates directory iteration support, checks permissions, takes shared inode lock, calls `iterate_shared`, updates `f_pos`, and emits access notifications.
- `wrap_directory_iterator()`: adapts old filesystems needing exclusive inode locking by temporarily upgrading from shared to write lock and downgrading afterward.
- `verify_dirent_name()`: rejects invalid directory entry names with zero/negative length, length at or above `PATH_MAX`, or embedded `/`.
- Implements old `readdir`, `getdents`, `getdents64`, and compat variants.

## ABI Writers
- `fillonedir()`: old one-entry ABI.
- `filldir()`: native `linux_dirent`.
- `filldir64()`: native `linux_dirent64`.
- `compat_fillonedir()` and `compat_filldir()`: compat ABI versions.

The fill callbacks:
- verify names,
- detect inode number overflow for narrower ABI fields,
- handle record alignment and buffer space,
- copy names and metadata to userspace with unsafe user access helpers,
- update previous record offsets when final position is known.

## Edge Cases
- Signal interruption is avoided for the first emitted entry but can stop after at least one record unless `FILLDIR_FLAG_NOINTR` is set.
- Dead directories return `-ENOENT`.
- Corrupt names are treated as hard errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/remap_range.c -->
# File Research: sources/os/linux/linux-stable/fs/remap_range.c

## Purpose
Implements generic VFS preparation and validation for file range remapping, reflink/clone, and deduplication.

## Main Responsibilities
- `generic_remap_checks()`: validates block alignment, offset overflow, EOF handling, write limits, block-aligned length, overlap rules, and shortening policy.
- `remap_verify_area()`: validates range signs/overflow, LSM permissions, and fsnotify area permissions.
- `generic_remap_check_len()`: prevents partial EOF block remaps into invalid destination positions, shortening when allowed.
- Dedupe comparison helpers read and lock folios from source/destination and compare bytes safely.
- `__generic_remap_file_range_prep()`: performs common clone/dedupe checks, waits for direct I/O, flushes dirty ranges, verifies dedupe equality, checks final length, and calls `file_modified()` for clone/remap writes.
- `generic_remap_file_range_prep()`: public wrapper without DAX ops.
- `vfs_clone_file_range()`: same-superblock reflink entry point using filesystem `remap_file_range`.
- `vfs_dedupe_file_range_one()` and `vfs_dedupe_file_range()`: per-destination and multi-destination dedupe APIs.

## Dedupe Rules
- Source file must be readable and regular.
- Destination must pass write permission or ownership/admin checks.
- Source and destination must be on the same superblock.
- Data must compare identical; mismatches report `FILE_DEDUPE_RANGE_DIFFERS`.
- Single dedupe requests are capped at 1 GiB.

## Edge Cases
- Rejects immutable outputs and swapfiles.
- Rejects directories and non-regular files.
- DAX dedupe comparison is supported only if DAX read ops are supplied.
- Zero-length clone to EOF is expanded; zero-length dedupe returns immediately.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/remap_range.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/resctrl/Kconfig

## Purpose
Defines Kconfig options for the CPU Resource Control filesystem, `resctrl`.

## Options
- `RESCTRL_FS`: mountable resource-control filesystem, depends on `ARCH_HAS_CPU_RESCTRL`, selects `KERNFS`, and selects `PROC_CPU_RESCTRL` when procfs is enabled.
- `RESCTRL_FS_PSEUDO_LOCK`: internal option for cache pseudo-locking support, depends on `RESCTRL_FS`.
- `RESCTRL_RMID_DEPENDS_ON_CLOSID`: architecture-selected option for systems where RMID allocation depends on CLOSID.

## User-Visible Behavior
When enabled, userspace can mount `resctrl` to group tasks and manage hardware cache/memory bandwidth monitoring and control resources. If unused, controls remain quiescent and permissive.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/resctrl/Makefile

## Purpose
Build rules for resctrl filesystem objects.

## Behavior
- Builds `rdtgroup.o`, `ctrlmondata.o`, and `monitor.o` when `CONFIG_RESCTRL_FS=y`.
- Builds `pseudo_lock.o` when `CONFIG_RESCTRL_FS_PSEUDO_LOCK=y`.
- Adds `-I$(src)` to `monitor.o` compile flags to support recursive `define_trace.h` include behavior.

## Role
Connects resctrl Kconfig selections to the filesystem implementation object files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/resctrl/Makefile -->