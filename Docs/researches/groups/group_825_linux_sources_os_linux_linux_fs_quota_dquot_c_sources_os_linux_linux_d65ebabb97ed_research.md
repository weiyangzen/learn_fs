# Group Research: group_825_linux_sources_os_linux_linux_fs_quota_dquot_c_sources_os_linux_linux_d65ebabb97ed

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/dquot.c -->
# File Research: sources/os/linux/linux/fs/quota/dquot.c

Core VFS disk-quota implementation. This file owns generic `struct dquot` lifecycle, quota accounting, dirty/writeback paths, quota-on/off state transitions, and the default `dquot_operations` / `quotactl_ops` exported to filesystems.

Key responsibilities:
- Registers and unregisters quota formats via `register_quota_format()` / `unregister_quota_format()`, including lazy module loading in `find_quota_format()`.
- Maintains global dquot lists and hash table: `inuse_list`, `free_dquots`, `releasing_dquots`, per-info dirty lists, and `dquot_hash`.
- Implements dquot reference management through `dqget()`, `dqgrab()`, and `dqput()`.
- Uses delayed work plus `synchronize_srcu(&dquot_srcu)` in `quota_release_workfn()` so inode-held dquot pointers can be cleared safely before final release.
- Implements read/commit/release of dquots with `dquot_acquire()`, `dquot_commit()`, `dquot_release()`, and writeback with `dquot_writeback_dquots()` / `dquot_quota_sync()`.
- Handles inode quota pointer initialization/drop through `__dquot_initialize()`, `dquot_initialize()`, `dquot_drop()`, `add_dquot_ref()`, and `remove_dquot_ref()`.
- Performs quota accounting for blocks, reserved space, and inodes via `__dquot_alloc_space()`, `dquot_alloc_inode()`, `dquot_claim_space_nodirty()`, `dquot_reclaim_space_nodirty()`, `__dquot_free_space()`, and `dquot_free_inode()`.
- Transfers quota usage during ownership changes via `dquot_transfer()` and `__dquot_transfer()`.
- Enables, disables, suspends, resumes, and mounts quota files through `dquot_disable()`, `dquot_quota_off()`, `dquot_load_quota_sb()`, `dquot_load_quota_inode()`, `dquot_resume()`, `dquot_quota_on()`, and `dquot_quota_on_mount()`.
- Implements generic get/set quota state and limits: `dquot_get_dqblk()`, `dquot_get_next_dqblk()`, `dquot_set_dqblk()`, `dquot_get_state()`, and `dquot_set_dqinfo()`.
- Exposes `/proc/sys/fs/quota/*` counters via `fs_dqstats_table`.

Important synchronization:
- Documented spinlock order is `dq_data_lock > dq_list_lock > i_lock > dquot->dq_dqb_lock`, with `dq_list_lock > dq_state_lock`.
- `dq_data_lock` protects inode dquot pointer updates and `mem_dqinfo`.
- `dq_state_lock` protects quota loaded/enforced/suspended state.
- `dq_list_lock` protects global dquot lists, format list, and hash table.
- `dquot->dq_lock` serializes on-disk read/write/release for a single dquot.
- `dquot_srcu` protects readers of inode dquot pointers while quotaoff clears references.

Notable behavior:
- Quota warnings are prepared inside accounting sections but flushed afterward, avoiding calls into tty or netlink while holding low-level quota locks.
- `ignore_hardlimit()` lets privileged callers bypass hard limits except when old-format root squash forbids it.
- Quota files are marked `S_NOQUOTA` and stripped of dquot references to avoid recursive quota accounting and deadlocks.
- External quota file enablement flushes and invalidates page/buffer cache so direct quota IO observes user changes.
- `DQUOT_QUOTA_SYS_FILE` supports filesystems with hidden quota metadata, where quotactl can enable or disable enforcement but not accounting.
- The shrinker reclaims clean free dquots from `free_dquots`.

Interfaces exported:
- Format registration: `register_quota_format`, `unregister_quota_format`.
- Dquot lifecycle/accounting: `dqget`, `dqput`, `dqgrab`, `dquot_initialize`, `dquot_drop`, allocation/free/transfer helpers.
- Quota operations: `dquot_operations`, `dquot_quotactl_sysfile_ops`.
- Quota file control: `dquot_quota_on`, `dquot_quota_off`, `dquot_quota_on_mount`, `dquot_resume`.

Research notes:
- This is the central quota engine; `quota.c` is the user ABI dispatcher, while `quota_v1.c`, `quota_v2.c`, and `quota_tree.c` provide backing formats.
- The file is sensitive to lock ordering, SRCU lifetime, and memory reclaim recursion; most quota IO paths use `memalloc_nofs_save()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/dquot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/kqid.c -->
# File Research: sources/os/linux/linux/fs/quota/kqid.c

Small helper file for kernel quota identifiers, `struct kqid`.

Key responsibilities:
- `qid_eq()` compares quota identifiers, dispatching by quota type to UID, GID, or project-ID comparison.
- `qid_lt()` provides ordering first by quota type, then by typed ID.
- `from_kqid()` maps a kernel quota ID into a user namespace, returning `(qid_t)-1` on unmapped IDs.
- `from_kqid_munged()` maps with overflow fallback, guaranteeing a printable/user-visible ID.
- `qid_valid()` validates the typed ID payload.

Supported quota types:
- `USRQUOTA`: uses `kuid_t`.
- `GRPQUOTA`: uses `kgid_t`.
- `PRJQUOTA`: uses `kprojid_t`.

Research notes:
- Invalid quota types call `BUG()`, so callers must validate `qid.type`.
- These helpers are exported and used by quota core, netlink warning emission, and on-disk quota format code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/kqid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/netlink.c -->
# File Research: sources/os/linux/linux/fs/quota/netlink.c

Generic netlink notification support for quota warnings.

Key responsibilities:
- Defines the `VFS_DQUOT` generic netlink family with one multicast group, `events`.
- Implements `quota_send_warning()`, exported for quota core and other filesystems.
- Sends warning attributes:
  - quota type,
  - exceeded quota ID,
  - warning type,
  - device major/minor,
  - current UID that caused the event.

Important behavior:
- Uses `GFP_NOFS` allocation because warnings are emitted from filesystem write/accounting paths, where filesystem reclaim recursion can deadlock.
- Uses `from_kqid_munged(&init_user_ns, qid)` and `from_kuid_munged()` so messages can always carry usable IDs.
- Registers the generic netlink family at `fs_initcall`.

Research notes:
- This file is notification-only; the actual warning decision logic is in `dquot.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/netlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/quota.c -->
# File Research: sources/os/linux/linux/fs/quota/quota.c

System-call and ABI translation layer for quota control. It handles `quotactl(2)` and `quotactl_fd(2)`, translates legacy/Linux/XFS quota structures into VFS `qc_*` structures, checks permissions, locates target superblocks, and dispatches to `sb->s_qcop`.

Key responsibilities:
- `check_quotactl_permission()` enforces command permissions and LSM `security_quotactl()`.
- `quota_sync_all()` implements device-less `Q_SYNC` across all superblocks.
- `quota_quotaon()` / `quota_quotaoff()` route to either traditional quota file operations or sysfile enforcement toggles.
- Legacy quota ABI:
  - `quota_getfmt()`
  - `quota_getinfo()` / `quota_setinfo()`
  - `quota_getquota()` / `quota_getnextquota()`
  - `quota_setquota()`
- XFS-style ABI:
  - `quota_getxstate()` / `quota_getxstatev()`
  - `quota_setxquota()`
  - `quota_getxquota()` / `quota_getnextxquota()`
  - `quota_rmxquota()`
- `do_quotactl()` validates quota type and dispatches all quota commands.
- `quotactl_block()` resolves a block-device path to a mounted superblock and handles freeze/exclusive locking semantics.
- `SYSCALL_DEFINE4(quotactl)` implements path/block-device based quota control.
- `SYSCALL_DEFINE4(quotactl_fd)` implements fd-based quota control.

Important conversions:
- Converts block units between legacy `QIF_DQBLKSIZE` and byte-based `qc_dqblk`.
- Converts XFS basic blocks using local `quota_bbtob()` / `quota_btobb()`.
- Supports `FS_DQ_BIGTIME` high timer fields when translating XFS-style quota timers.
- Handles compat alignment fixups for older quota structs.

Important behavior:
- `Q_GETQUOTA` and `Q_GETNEXTQUOTA` are treated as write-like commands because reading can instantiate dquots or update on-disk references in some filesystems.
- Quota-on/off commands acquire `s_umount` for write; other commands acquire it for read.
- `Q_QUOTAON` resolves the quota file path before grabbing `s_umount` to avoid autofs/pathwalk deadlocks.
- `quotactl_fd()` uses mount write access for write-like commands.

Research notes:
- This file intentionally remains present even when full VFS quota support is disabled, because syscall plumbing and command validation still need definitions.
- Actual generic quota state is implemented in `dquot.c`; this file is mostly ABI adaptation and dispatch.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/quota_tree.c -->
# File Research: sources/os/linux/linux/fs/quota/quota_tree.c

Quota-file radix tree support for VFS quota v2 formats. It manages the tree of ID-to-dquot-entry mappings, free block lists, free-entry lists, quota entry insertion/removal, lookup, read/write, and next-ID enumeration.

Key responsibilities:
- Computes per-level indexes for quota IDs with `__get_index()` / `get_index()`.
- Reads and writes quota blocks with `read_blk()` and `write_blk()`.
- Validates block headers and block-number ranges with `check_dquot_block_header()` and `do_check_range()`.
- Manages free empty blocks:
  - `get_free_dqblk()`
  - `put_free_dqblk()`
- Manages blocks that contain free entries:
  - `remove_free_dqentry()`
  - `insert_free_dqentry()`
- Detects unused disk entries with exported `qtree_entry_unused()`.
- Finds a free dquot slot with `find_free_dqentry()`.
- Inserts quota entries into the tree via `dq_insert_tree()` / `do_insert_tree()`.
- Writes an in-memory dquot to disk with exported `qtree_write_dquot()`.
- Frees/removes quota entries with `free_dqentry()`, `remove_tree()`, and exported `qtree_delete_dquot()`.
- Looks up quota entries with `find_dqentry()` / `find_tree_dqentry()` / `find_block_dqentry()`.
- Reads quota entries into memory with exported `qtree_read_dquot()`.
- Releases fake unused dquots with exported `qtree_release_dquot()`.
- Enumerates next quota IDs with exported `qtree_get_next_id()`.

On-disk model:
- Block `QT_TREEOFF` is the tree root.
- Internal tree blocks store little-endian block references.
- Leaf/data blocks begin with `struct qt_disk_dqdbheader`, followed by fixed-size format-specific dquot entries.
- `dqi_free_blk` tracks fully free blocks.
- `dqi_free_entry` tracks blocks that still have at least one free dquot entry.

Safety checks:
- `MAX_QTREE_DEPTH` limits recursion.
- Range checks reject corrupt block references.
- Cycle checks detect quota-tree loops.
- Header checks validate free-list links and entry counts.
- Paranoia checks reject duplicate insertions and impossible full-block states.

Research notes:
- Format-specific conversion is delegated through `struct qtree_fmt_operations`, supplied by `quota_v2.c`.
- This file is generic tree mechanics; it does not define the v2 disk dquot payload fields.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/quota_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/quota_tree.h -->
# File Research: sources/os/linux/linux/fs/quota/quota_tree.h

Header for quota-tree block layout.

Defines:
- `struct qt_disk_dqdbheader`, the 16-byte header at the start of quota data blocks.
  - `dqdh_next_free`: next block in free-entry list.
  - `dqdh_prev_free`: previous block in free-entry list.
  - `dqdh_entries`: number of valid entries in the block.
  - padding fields to keep the header at 16 bytes.
- `QT_TREEOFF`, the block offset of the quota tree root.

Research notes:
- The 16-byte header size is chosen so a standard v2 data block has predictable room for quota entries.
- Used by `quota_tree.c` and v2 quota format support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/quota_tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/quota_v1.c -->
# File Research: sources/os/linux/linux/fs/quota/quota_v1.c

Old VFS quota file format support. The v1 format stores a flat array of `struct v1_disk_dqblk` records indexed directly by numeric user/group ID.

Key responsibilities:
- Converts space units between bytes and 1 KiB quota blocks with `v1_stoqb()` / `v1_qbtos()`.
- Converts disk records to/from `struct mem_dqblk` using `v1_disk2mem_dqblk()` and `v1_mem2disk_dqblk()`.
- Reads a quota record at `v1_dqoff(id)` through `v1_read_dqblk()`.
- Writes a quota record through `v1_commit_dqblk()`.
- Detects old-format files and refuses files that appear to contain newer v2 magic via `v1_check_quota_file()`.
- Reads/writes global quota info from the root quota record with `v1_read_file_info()` and `v1_write_file_info()`.
- Registers the `QFMT_VFS_OLD` quota format at module init.

Important behavior:
- A zero-limit dquot is marked `DQ_FAKE_B`.
- Root user/group entries carry grace times in the v1 format.
- File info maximums are limited by 32-bit on-disk counters.
- Uses `dqio_sem` and `memalloc_nofs_save()` around quota IO.

Research notes:
- Supports user and group quota magics for v2 detection but is itself the legacy flat-array format.
- No project quota support is apparent in this old format file.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/quota_v1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/quota_v2.c -->
# File Research: sources/os/linux/linux/fs/quota/quota_v2.c

VFS quota v2 format support. This file validates v2 quota headers, reads/writes v2 file info, translates v2r0/v2r1 disk dquot records, and plugs the generic quota tree operations into the quota format interface.

Key responsibilities:
- Defines qtree conversion operations for:
  - v2r0: 32-bit limits/counters where applicable.
  - v2r1: 64-bit limits/counters.
- Reads and validates `struct v2_disk_dqheader` with `v2_read_header()` and `v2_check_quota_file()`.
- Reads v2 info header with `v2_read_file_info()`:
  - validates version against `QFMT_VFS_V0` / `QFMT_VFS_V1`,
  - allocates `struct qtree_mem_dqinfo`,
  - initializes tree block size, free lists, block count, depth, entry size, and conversion ops,
  - validates free block and free-entry pointers against file size.
- Writes info header with `v2_write_file_info()`.
- Converts v2r0/v2r1 records to/from `struct mem_dqblk`.
- Implements ID matching callbacks `v2r0_is_id()` and `v2r1_is_id()`.
- Wraps `quota_tree.c` operations:
  - `v2_read_dquot()`
  - `v2_write_dquot()`
  - `v2_release_dquot()`
  - `v2_get_next_id()`
- Frees format-private qtree state with `v2_free_file_info()`.
- Registers both `QFMT_VFS_V0` and `QFMT_VFS_V1`.

Important behavior:
- Uses an “escaped” all-zero entry by setting `dqb_itime = 1` when a real dquot would otherwise look unused to `qtree_entry_unused()`.
- v2r0 maximums are bounded by 32-bit quota-block values; v2r1 uses signed 63-bit limits in the generic quota core.
- Allocation of new dquot tree entries takes `dqio_sem` for write; overwriting existing entries takes it for read.
- All quota IO paths use `memalloc_nofs_save()`.

Research notes:
- `quota_tree.c` owns tree mechanics, while this file owns v2-specific header validation and disk payload conversion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/quota_v2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/quotaio_v1.h -->
# File Research: sources/os/linux/linux/fs/quota/quotaio_v1.h

On-disk structure definitions for the old v1 quota format.

Defines:
- Default soft-limit grace times:
  - `MAX_IQ_TIME`: one week for inode quota.
  - `MAX_DQ_TIME`: one week for block quota.
- `struct v1_disk_dqblk`, the flat-array quota record:
  - block hard/soft limits,
  - current block count,
  - inode hard/soft limits,
  - current inode count,
  - block and inode grace timers.
- `v1_dqoff(UID)`, the byte offset of a quota record in the flat file.

Research notes:
- Timer fields use `unsigned long`, explicitly noted as architecture-width dependent.
- The file is included by `quota_v1.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/quotaio_v1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/quota/quotaio_v2.h -->
# File Research: sources/os/linux/linux/fs/quota/quotaio_v2.h

On-disk structure definitions and constants for v2 quota files.

Defines:
- `V2_INITQMAGICS` for user, group, and project quota files.
- `V2_INITQVERSIONS`, currently version 1 for each quota type.
- `struct v2_disk_dqheader`, the file magic/version header.
- `struct v2r0_disk_dqblk`, v2 revision 0 quota entry with 32-bit limit fields and 64-bit space/timer fields.
- `struct v2r1_disk_dqblk`, v2 revision 1 quota entry with 64-bit limit/counter fields.
- `struct v2_disk_dqinfo`, global info header containing grace times, flags, total blocks, free block head, and free-entry head.
- `V2_DQINFOOFF`, the offset of the info header after the file header.
- `V2_DQBLKSIZE_BITS`, setting v2 quota tree blocks to 1024 bytes.

Research notes:
- These definitions are consumed by `quota_v2.c` and interpreted by the generic tree code in `quota_tree.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/quota/quotaio_v2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ramfs/Makefile -->
# File Research: sources/os/linux/linux/fs/ramfs/Makefile

Build rules for ramfs.

Key behavior:
- Always builds `ramfs.o` into the kernel object list with `obj-y += ramfs.o`.
- Composes `ramfs.o` from `inode.o` and a file-operations object.
- Defaults `file-mmu-y` to `file-nommu.o`.
- Overrides `file-mmu-y` to `file-mmu.o` when `CONFIG_MMU` is enabled.

Research notes:
- This Makefile selects mutually exclusive MMU vs NOMMU file operation implementations while keeping common inode/superblock code in `inode.o`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ramfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ramfs/file-mmu.c -->
# File Research: sources/os/linux/linux/fs/ramfs/file-mmu.c

MMU-enabled ramfs file operation definitions.

Key responsibilities:
- Provides `ramfs_mmu_get_unmapped_area()`, delegating to `mm_get_unmapped_area()`.
- Defines `ramfs_file_operations`:
  - generic read/write iterators,
  - generic mmap preparation,
  - noop fsync,
  - splice read/write,
  - generic llseek,
  - MMU unmapped-area lookup.
- Defines `ramfs_file_inode_operations`:
  - `simple_setattr`,
  - `simple_getattr`.

Important behavior:
- ramfs relies on the VFS page cache rather than private on-disk or in-memory file data structures.
- The file is intentionally minimal and serves as a simple read-write filesystem example.

Research notes:
- NOMMU behavior is separated into `file-nommu.c`; only one implementation is linked by the Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ramfs/file-mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ramfs/file-nommu.c -->
# File Research: sources/os/linux/linux/fs/ramfs/file-nommu.c

NOMMU ramfs file operation and mmap support. It implements direct/shared mappings from physically contiguous ramfs pages, plus NOMMU-specific truncate/resize behavior.

Key responsibilities:
- Defines `ramfs_file_operations` for NOMMU:
  - mmap capabilities,
  - NOMMU mmap prepare,
  - NOMMU unmapped-area lookup,
  - generic read/write,
  - splice read/write,
  - generic llseek.
- Defines `ramfs_file_inode_operations` with NOMMU-specific `setattr`.
- `ramfs_nommu_expand_for_mapping()` expands a zero-size inode into a contiguous page allocation for shared mapping.
- `ramfs_nommu_resize()` handles truncate growth/shrink, including `nommu_shrink_inode_mappings()` on shrink.
- `ramfs_nommu_setattr()` handles size-changing attributes and timestamp updates.
- `ramfs_nommu_get_unmapped_area()` checks that requested file pages exist and are physically contiguous.
- `ramfs_nommu_mmap_prepare()` accepts only NOMMU shared mappings and installs `generic_file_vm_ops`.

Important behavior:
- Growth from zero assumes the file is being prepared for shared mmap and allocates a high-order contiguous page range.
- Extra pages from the high-order allocation are freed after splitting.
- Pages are inserted into the file mapping, marked dirty and uptodate, and kept unevictable by ramfs inode setup.
- If requested pages are missing or non-contiguous, `get_unmapped_area` returns `-ENOSYS`.

Research notes:
- This file is linked only when `CONFIG_MMU` is not set.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ramfs/file-nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ramfs/inode.c -->
# File Research: sources/os/linux/linux/fs/ramfs/inode.c

Common ramfs inode, directory, mount, and filesystem registration code.

Key responsibilities:
- Defines ramfs mount-private state:
  - `struct ramfs_mount_opts`
  - `struct ramfs_fs_info`
- `ramfs_get_inode()` allocates and initializes inodes:
  - sets `ram_aops`,
  - sets high-user GFP mask,
  - marks mapping unevictable,
  - installs file, directory, symlink, or special inode operations.
- Creates filesystem objects:
  - `ramfs_mknod()`
  - `ramfs_mkdir()`
  - `ramfs_create()`
  - `ramfs_symlink()`
  - `ramfs_tmpfile()`
- Defines directory inode operations using simple VFS helpers.
- Shows mount options via `ramfs_show_options()`.
- Defines superblock operations:
  - `simple_statfs`,
  - `inode_just_drop`,
  - `show_options`.
- Parses mount options through fs_context:
  - supports octal `mode=`,
  - accepts source-like parameters,
  - ignores unknown options for historical compatibility.
- `ramfs_fill_super()` initializes superblock fields and creates the root inode/dentry.
- Provides fs_context operations and lifecycle:
  - `ramfs_init_fs_context()`,
  - `ramfs_get_tree()`,
  - `ramfs_free_fc()`,
  - `ramfs_kill_sb()`.
- Registers `ramfs` at `fs_initcall`.

Important behavior:
- `sb->s_d_flags = DCACHE_DONTCACHE`, matching ramfs’s simple/persistent dentry model.
- `FS_USERNS_MOUNT` allows user-namespace mounts.
- Default root mode is `0755`.
- File data lives in page cache; ramfs has no backing store and no reclaimable persistent storage.

Research notes:
- File operation details are supplied by either `file-mmu.c` or `file-nommu.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ramfs/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ramfs/internal.h -->
# File Research: sources/os/linux/linux/fs/ramfs/internal.h

Small internal ramfs header.

Defines:
- External declaration for `ramfs_file_inode_operations`.

Research notes:
- Included by ramfs implementation files so common inode code can refer to the file inode operations supplied by the selected MMU/NOMMU file implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ramfs/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/read_write.c -->
# File Research: sources/os/linux/linux/fs/read_write.c

Core VFS read/write, seek, vector IO, sendfile, copy_file_range, and generic write/copy validation implementation.

Key responsibilities:
- Defines `generic_ro_fops`, a read-only generic file-operations table.
- Implements generic seek helpers:
  - `vfs_setpos()`
  - `generic_file_llseek_size()`
  - `generic_llseek_cookie()`
  - `generic_file_llseek()`
  - `fixed_size_llseek()`
  - `no_seek_end_llseek()`
  - `noop_llseek()`
  - `default_llseek()`
  - `vfs_llseek()`
- Implements seek syscalls:
  - `lseek`
  - compat `lseek`
  - `llseek` where required.
- Validates read/write access with `rw_verify_area()`, including offset overflow, LSM permission, and fsnotify area permission.
- Implements kernel internal reads/writes:
  - `__kernel_read()`
  - `kernel_read()`
  - `__kernel_write_iter()`
  - `__kernel_write()`
  - `kernel_write()`
- Implements user scalar IO:
  - `vfs_read()`
  - `vfs_write()`
  - `ksys_read()` / `read`
  - `ksys_write()` / `write`
  - `pread64`
  - `pwrite64`
- Implements vector and positioned vector IO:
  - `vfs_iocb_iter_read()`
  - `vfs_iter_read()`
  - `vfs_iocb_iter_write()`
  - `vfs_iter_write()`
  - `readv`, `writev`, `preadv`, `pwritev`, `preadv2`, `pwritev2`
  - compat variants.
- Implements sendfile with `do_sendfile()`, `sendfile`, `sendfile64`, and compat variants.
- Implements `vfs_copy_file_range()` and `copy_file_range` syscall.
- Provides generic write/copy validation:
  - `generic_write_check_limits()`
  - `generic_write_checks_count()`
  - `generic_write_checks()`
  - `generic_file_rw_checks()`
  - `generic_atomic_write_valid()`

Important behavior:
- Caps user IO sizes at `MAX_RW_COUNT`.
- Uses `file_start_write()` / `file_end_write()` around write paths and copy paths as needed.
- Updates task accounting (`add_rchar`, `add_wchar`, `inc_syscr`, `inc_syscw`) and fsnotify events on successful IO.
- Uses local position copies for normal read/write syscalls so position updates occur only after successful VFS calls.
- Supports `preadv2` / `pwritev2` with `pos == -1` as current-position vector IO.
- `copy_file_range` first tries filesystem `copy_file_range`, then same-superblock remap/clone, then splice fallback where allowed.
- `generic_copy_file_checks()` rejects immutable output, swapfiles, overflowed offsets, overlapped same-file copies, and cross-superblock cases unless an allowed path exists.
- `generic_write_check_limits()` enforces `RLIMIT_FSIZE`, `O_LARGEFILE`, superblock max bytes, and sends `SIGXFSZ` when appropriate.
- `generic_atomic_write_valid()` requires user buffer iterator, power-of-two length, aligned offset, and direct IO.

Research notes:
- This file is a major syscall-to-filesystem adaptor. Filesystems implement lower-level `file_operations`; this file supplies common validation, accounting, fallback, and syscall glue.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/read_write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/readdir.c -->
# File Research: sources/os/linux/linux/fs/readdir.c

Core VFS directory iteration and `getdents` syscall implementation.

Key responsibilities:
- `wrap_directory_iterator()` adapts filesystems that need exclusive inode locking to the shared `iterate_shared` calling convention.
- `iterate_dir()` performs permission checks, fsnotify permission checks, shared inode locking, `IS_DEADDIR` checks, position transfer, and calls `file->f_op->iterate_shared`.
- `verify_dirent_name()` rejects invalid directory entry names with nonpositive length, path-sized length, or embedded `/`.
- Implements old `readdir` support when `__ARCH_WANT_OLD_READDIR` is enabled.
- Implements `getdents` using `struct linux_dirent` and `filldir()`.
- Implements `getdents64` using `struct linux_dirent64` and `filldir64()`.
- Implements compat old readdir and compat `getdents` under `CONFIG_COMPAT`.

Important behavior:
- Uses `unsafe_put_user` / `unsafe_copy_to_user` within scoped user-write regions for efficient dirent emission.
- Each fill callback validates name and inode-number overflow for ABI-sized inode fields.
- `getdents` and `getdents64` write the final directory offset into the previous record’s `d_off` after iteration.
- Honors `FILLDIR_FLAG_NOINTR` masking and can stop on pending signals after at least one record.
- Updates `file->f_pos`, triggers `fsnotify_access()`, and calls `file_accessed()` after successful iteration.

Research notes:
- This file is the VFS ABI bridge between filesystem `iterate_shared` callbacks and userspace directory-entry record layouts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/remap_range.c -->
# File Research: sources/os/linux/linux/fs/remap_range.c

Generic VFS helpers for reflink/clone and dedupe range operations.

Key responsibilities:
- `generic_remap_checks()` validates alignment, range overflow, EOF bounds, write limits, same-file overlap, and shortening rules.
- `remap_verify_area()` validates range sign/overflow and checks LSM plus fsnotify area permissions.
- `generic_remap_check_len()` handles partial EOF block rules for clone and dedupe.
- Dedupe data comparison:
  - `vfs_dedupe_get_folio()`
  - `vfs_lock_two_folios()`
  - `vfs_unlock_two_folios()`
  - `vfs_dedupe_file_range_compare()`
- `__generic_remap_file_range_prep()` performs common clone/dedupe preparation:
  - rejects immutable output and swapfiles,
  - rejects unsupported inode types,
  - handles zero-length clone-to-EOF behavior,
  - waits for direct IO,
  - writes back dirty page-cache ranges,
  - compares data for dedupe,
  - calls `file_modified()` for non-dedupe writes.
- `generic_remap_file_range_prep()` wraps the prep helper without DAX ops.
- `vfs_clone_file_range()` validates same-superblock clone and invokes `remap_file_range`.
- `may_dedupe_file()` checks whether the caller may dedupe into a destination.
- `vfs_dedupe_file_range_one()` dedupes one destination file/range.
- `vfs_dedupe_file_range()` handles multi-destination dedupe requests and fills per-destination statuses.

Important behavior:
- Clone requires same superblock.
- Dedupe also requires same superblock and readable source, and the destination must be writable or owned/permitted unless caller has `CAP_SYS_ADMIN`.
- Non-DAX dedupe comparison reads folios, locks them in stable order, checks mappings/uptodate state, flushes dcache, and `memcmp`s page-sized chunks.
- DAX dedupe comparison is delegated if DAX read ops are provided.
- Single dedupe requests are capped to 1 GiB.
- Per-destination dedupe reports `FILE_DEDUPE_RANGE_DIFFERS` when data comparison fails with `-EBADE`.

Research notes:
- Filesystems provide the actual remap operation through `->remap_file_range`; this file supplies common VFS safety and permission checks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/remap_range.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/resctrl/Kconfig -->
# File Research: sources/os/linux/linux/fs/resctrl/Kconfig

Kconfig options for the CPU resource control filesystem.

Defines:
- `RESCTRL_FS`
  - User-visible boolean: “CPU Resource Control Filesystem (resctrl)”.
  - Depends on `ARCH_HAS_CPU_RESCTRL`.
  - Selects `KERNFS`.
  - Selects `PROC_CPU_RESCTRL` when `PROC_FS` is enabled.
  - Provides a mountable `resctrl` filesystem for grouping tasks and controlling/monitoring memory-system resources such as cache and memory bandwidth.
- `RESCTRL_FS_PSEUDO_LOCK`
  - Internal boolean depending on `RESCTRL_FS`.
  - Enables software pseudo-locking to pin data in a cache portion.
- `RESCTRL_RMID_DEPENDS_ON_CLOSID`
  - Internal boolean depending on `RESCTRL_FS`.
  - Used when RMID allocation depends on CLOSID, causing CLOSID allocation to search for a clean RMID.

Research notes:
- This file is configuration only; implementation objects are selected in the sibling Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/resctrl/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/resctrl/Makefile -->
# File Research: sources/os/linux/linux/fs/resctrl/Makefile

Build rules for the resctrl filesystem.

Key behavior:
- When `CONFIG_RESCTRL_FS` is enabled, builds:
  - `rdtgroup.o`
  - `ctrlmondata.o`
  - `monitor.o`
- When `CONFIG_RESCTRL_FS_PSEUDO_LOCK` is enabled, builds:
  - `pseudo_lock.o`
- Adds `-I$(src)` to `monitor.o` so `define_trace.h` recursive include requirements are satisfied.

Research notes:
- This file only controls compilation; it contains no runtime logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/resctrl/Makefile -->