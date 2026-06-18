# subset-b-005749 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/dquot.c -->
# sources/distributed-fs/ceph-client/fs/quota/dquot.c

Purpose: Implements the generic VFS disk quota core: dquot lifetime, lookup, dirty tracking, quota on/off, quota accounting for inode and block usage, ownership transfers, sysfile quota controls, warning emission, shrinker integration, and `/proc/sys/fs/quota` statistics.

Important APIs, types, and functions: Exports `register_quota_format()`, `unregister_quota_format()`, `dqgrab()`, `dquot_mark_dquot_dirty()`, `mark_info_dirty()`, `dquot_acquire()`, `dquot_commit()`, `dquot_release()`, `dquot_scan_active()`, `dquot_writeback_dquots()`, `dquot_quota_sync()`, `dqput()`, `dquot_alloc()`, `dqget()`, `dquot_initialize()`, `dquot_drop()`, `__dquot_alloc_space()`, `dquot_alloc_inode()`, `dquot_claim_space_nodirty()`, `dquot_reclaim_space_nodirty()`, `__dquot_free_space()`, `dquot_free_inode()`, `__dquot_transfer()`, `dquot_transfer()`, `dquot_load_quota_sb()`, `dquot_load_quota_inode()`, `dquot_resume()`, `dquot_quota_on()`, `dquot_quota_on_mount()`, `dquot_get_dqblk()`, `dquot_set_dqblk()`, `dquot_get_state()`, and `dquot_set_dqinfo()`. Global state includes `quota_formats`, `dquot_cachep`, `quota_unbound_wq`, `dquot_hash`, `inuse_list`, `free_dquots`, `releasing_dquots`, `dqstats`, and locks `dq_list_lock`, `dq_state_lock`, `dq_data_lock`, plus `dquot_srcu`.

Control flow: quota formats register into a linked list and can be module-loaded by format id. `dqget()` validates namespace mappings and active quota state, reuses or allocates a hashed dquot, waits for `dq_lock`, then acquires on-disk state. Inode initialization builds per-type qids from uid/gid/projid, obtains dquots, and installs pointers under `dq_data_lock`. Allocation and free paths update all attached dquots under inode and dquot locks, roll back partial failures, mark dirty dquots, and flush delayed warnings. Quota on pins a quota inode, validates format operations, reads format info, sets quota state flags, and initializes references for open writable inodes. Quota off clears state, drops inode references, flushes and invalidates dquots, writes dirty info, releases format modules, and restores quota file inode state.

State and persistence: In-memory dquots are cached by superblock, type, and qid, move through active, dirty, releasing, and free states, and are reclaimed by a shrinker. Persistent data is delegated to format-specific `quota_format_ops` and filesystem `quota_read`/`quota_write`. Dirty dquots are either tracked on `dqi_dirty_list` or by journal-aware filesystems using `DQUOT_NOLIST_DIRTY`. Quota files are marked `S_NOQUOTA` to avoid self-accounting, page cache is truncated for external quota files, and block-device buffers are invalidated around quota-on/off so userspace and kernel views do not diverge.

Dependencies and integration points: Relies on VFS inode lists, superblock `dq_op` and `s_qcop`, quota format modules, security hooks, uid/gid/projid mapping helpers, workqueues, SRCU, sysctl, shrinkers, blockdev sync/invalidation, and netlink quota warnings. Filesystems integrate by providing dquot operations, quota read/write methods, optional reserved-space and project-id callbacks, and quotactl operations.

Risks and test signals: Highest risks are lock-order inversions, stale inode dquot pointers after quotaoff, dirty-list livelock, quota file corruption after partial writes, namespace mapping mistakes, and incorrect reserved-space accounting. Test with quotaon/off under concurrent writes, remount suspend/resume, ownership changes across uid/gid/project quotas, soft and hard limit transitions, dirty writeback failures, shrinker pressure, external quota file page-cache coherency, root-squash old-format behavior, and `/proc/sys/fs/quota` counter sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/dquot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/kqid.c -->
# sources/distributed-fs/ceph-client/fs/quota/kqid.c

Purpose: Provides generic helpers for comparing, ordering, validating, and exporting kernel quota identifiers (`struct kqid`) across user, group, and project quota types.

Important APIs, types, and functions: Exports `qid_eq()`, `qid_lt()`, `from_kqid()`, `from_kqid_munged()`, and `qid_valid()`. Each function switches on `kqid.type` and delegates to uid, gid, or project-id helpers such as `uid_eq()`, `gid_lt()`, `from_kprojid()`, and `projid_valid()`.

Control flow: Equality first compares quota type, then compares the type-specific union member. Ordering sorts by type before comparing type-specific ids. Namespace conversion maps the selected id into a target `user_namespace`; the munged variant returns the overflow id instead of `(qid_t)-1` for unmapped ids. Invalid quota types trigger `BUG()`, making callers responsible for providing a valid type.

State and persistence: No persistent state is stored here. The file only transforms and validates id values passed by quota core, syscalls, and quota formats.

Dependencies and integration points: Used by dquot hashing and matching, quota tree lookup, netlink warning payload generation, quotactl user-copy paths, and any filesystem that needs type-generic quota ids. It depends on Linux id-mapping primitives and the `USRQUOTA`, `GRPQUOTA`, and `PRJQUOTA` type constants.

Risks and test signals: Key risks are invalid type propagation and namespace conversion errors that expose the wrong id to userspace. Test mixed quota-type sorting, unmapped ids in non-init namespaces, project quota ids, and all exported helpers with boundary ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/kqid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/netlink.c -->
# sources/distributed-fs/ceph-client/fs/quota/netlink.c

Purpose: Implements the generic netlink notification path for quota warnings so kernel quota enforcement can notify userspace listeners about exceeded or recovered limits.

Important APIs, types, and functions: Defines genl family `VFS_DQUOT`, multicast group `events`, and exports `quota_send_warning()`. The warning payload carries quota type, exceeded id, warning code, device major/minor, and the current uid that caused the warning.

Control flow: `quota_send_warning()` allocates a `sk_buff` with `GFP_NOFS`, builds a generic netlink message with a monotonic atomic sequence, appends attributes with `nla_put_*`, finalizes with `genlmsg_end()`, and multicasts. Attribute build failures free the skb and log errors. `quota_init()` registers the family at `fs_initcall`.

State and persistence: State is limited to the registered genl family and a static sequence counter. Messages are transient and not persisted.

Dependencies and integration points: Called by `flush_warnings()` in `dquot.c` and can be used by filesystems that do not use generic dquot. Depends on generic netlink, quota id mapping, current credentials, and device number helpers.

Risks and test signals: Risks include allocation failure in filesystem write paths, malformed attribute sizes, and userspace ABI regressions. Test by triggering block and inode soft/hard warnings, listening on the `VFS_DQUOT` `events` group, validating id/dev attributes, and injecting allocation or attribute failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota.c -->
# sources/distributed-fs/ceph-client/fs/quota/quota.c

Purpose: Implements the `quotactl(2)` and `quotactl_fd(2)` syscall front end, including permission checks, command dispatch, user ABI translation, XFS-compatible quota structures, and global quota sync.

Important APIs, types, and functions: Key routines include `check_quotactl_permission()`, `quota_sync_all()`, `qtype_enforce_flag()`, `quota_quotaon()`, `quota_quotaoff()`, `quota_getfmt()`, `quota_getinfo()`, `quota_setinfo()`, `quota_getquota()`, `quota_getnextquota()`, `quota_setquota()`, XFS ABI converters `copy_from_xfs_dqblk()` and `copy_to_xfs_dqblk()`, `quota_setxquota()`, `quota_getxstatev()`, `do_quotactl()`, `quotactl_block()`, and syscall definitions for `quotactl` and `quotactl_fd`.

Control flow: Syscalls split `cmd` into command and quota type, resolve either a block device path or an fd superblock, obtain the proper `s_umount` lock, optionally resolve quota-on file paths first to avoid deadlock, and call `do_quotactl()`. Dispatch validates `s_qcop` support, supported quota type mask, LSM permissions, and command-specific privileges. User ABI structs are translated to generic `qc_*` structs before calling filesystem quota operations.

State and persistence: This file owns no quota storage. It marshals user requests to superblock quota operations that may change on-disk quota files, internal filesystem quota metadata, and quota enforcement state.

Dependencies and integration points: Depends on VFS superblock lookup, mount write access, frozen-superblock handling, security hooks, user-copy helpers, id mapping, block-device lookup, and filesystem `quotactl_ops`. It bridges legacy VFS quota commands and XFS-style `Q_X*` commands.

Risks and test signals: Risks include privilege bypass for owned quota queries, wrong namespace mapping, freeze/write-lock deadlocks, ABI conversion overflow, compat structure alignment bugs, and incorrect project-vs-group state reporting in older XFS stats. Test all commands through both device path and fd syscalls, compat mode, non-init user namespaces, frozen filesystems, quota-on path resolution, and XFS bigtime timer values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota_tree.c -->
# sources/distributed-fs/ceph-client/fs/quota/quota_tree.c

Purpose: Provides the shared radix-tree-like on-disk storage engine used by VFS v2 quota formats to locate, allocate, update, delete, and enumerate dquot records in quota files.

Important APIs, types, and functions: Exports `qtree_entry_unused()`, `qtree_write_dquot()`, `qtree_delete_dquot()`, `qtree_read_dquot()`, `qtree_release_dquot()`, and `qtree_get_next_id()`. Internal helpers manage tree indexes, quota blocks, free block lists, free-entry lists, block-header validation, insertion recursion, removal recursion, and next-id scans.

Control flow: Reads and writes go through filesystem `quota_read` and `quota_write` at block offsets derived from `qtree_mem_dqinfo`. Writing inserts a missing dquot by walking or allocating tree blocks, finding a leaf data slot, converting memory data to disk format, and writing the entry. Releasing fake zero-usage dquots deletes their entry. Deletion clears the leaf entry, updates data-block entry counts and free lists, then recursively removes empty tree blocks except the root. Reads locate the leaf via tree indexes; missing entries become fake zeroed dquots.

State and persistence: Persistent state is the quota file tree rooted at `QT_TREEOFF`, data-block headers (`qt_disk_dqdbheader`), free-block chain, free-entry chain, and disk dquot entries. In-memory `qtree_mem_dqinfo` mirrors block counts, free list heads, block size, tree depth, entry size, and format operations. Metadata changes call `mark_info_dirty()`.

Dependencies and integration points: Used by `quota_v2.c` under `dqio_sem`. Depends on `qtree_fmt_operations` for format-specific disk conversion and id tests, generic dquot counters, and quota error reporting.

Risks and test signals: Risks include corrupt free-list links, cycles in tree blocks, out-of-range block references, full-block accounting mistakes, partial write handling, and id enumeration skipping entries. Test with dense and sparse ids, free/reallocate cycles, corrupted headers, tree depth limits, fake dquot deletion, full block transitions, and `Q_GETNEXTQUOTA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota_tree.h -->
# sources/distributed-fs/ceph-client/fs/quota/quota_tree.h

Purpose: Defines the on-disk header used at the start of VFS v2 quota data blocks and the block offset of the quota tree root.

Important APIs, types, and functions: Declares `struct qt_disk_dqdbheader` with little-endian `dqdh_next_free`, `dqdh_prev_free`, `dqdh_entries`, and padding fields. Defines `QT_TREEOFF` as block 1.

Control flow: This header is consumed by `quota_tree.c` when interpreting blocks that contain quota entries. Data blocks use the header to participate in the list of blocks with free entries and to count valid entry slots.

State and persistence: The structure is persisted inside quota files. It is intentionally padded to 16 bytes, which aligns the following quota entries and fixes the usable entry count for the historical v2 block layout.

Dependencies and integration points: Included by `quota_tree.c` and `quota_v2.c`. It depends only on basic Linux types and quota definitions.

Risks and test signals: Risks are ABI/layout changes and endian mistakes, since on-disk quota files depend on exact field sizes. Test by validating quota files written on one endian/word-size environment can be read with expected free-list and entry counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota_v1.c -->
# sources/distributed-fs/ceph-client/fs/quota/quota_v1.c

Purpose: Registers and implements the old flat-file VFS quota format (`QFMT_VFS_OLD`) where quota records are stored as an array indexed directly by uid or gid.

Important APIs, types, and functions: Defines `v1_stoqb()`, `v1_qbtos()`, `v1_disk2mem_dqblk()`, `v1_mem2disk_dqblk()`, `v1_read_dqblk()`, `v1_commit_dqblk()`, `v1_check_quota_file()`, `v1_read_file_info()`, `v1_write_file_info()`, `v1_format_ops`, and module init/exit registration.

Control flow: Format checking verifies file size is a multiple of the old record size and rejects files that appear to contain newer v2 magics. Reads zero-fill a disk record, read the id-indexed slot, convert fields into `mem_dqblk`, and mark all-zero limits as fake. Commits convert memory fields back to disk, preserve root grace-time storage semantics for user/group root records, and write the indexed slot. File info reads and writes grace times from id 0.

State and persistence: Persistent records are `struct v1_disk_dqblk` slots at `v1_dqoff(id)`. Limits are stored in 1 KiB quota blocks and inode counts as 32-bit values; grace times are stored in the root record. There is no tree allocator or per-record release path.

Dependencies and integration points: Uses generic dquot core format registration, filesystem quota read/write callbacks, `dqio_sem`, `dq_data_lock`, and `quotaio_v1.h`. It supports user and group quotas only in the old format.

Risks and test signals: Risks include 32-bit limit overflow, word-size-dependent on-disk time fields, accidentally enabling old format on v2 files, and root grace-time compatibility. Test old quota files, bad file sizes, v2 magic rejection, root id grace changes, and large limits near `0xffffffff`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota_v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota_v2.c -->
# sources/distributed-fs/ceph-client/fs/quota/quota_v2.c

Purpose: Registers and implements VFS quota formats v2r0 (`QFMT_VFS_V0`) and v2r1 (`QFMT_VFS_V1`) on top of the shared quota tree storage engine.

Important APIs, types, and functions: Defines qtree format operations for v2r0 and v2r1, header parsing `v2_read_header()`, validation `v2_check_quota_file()`, info load/store `v2_read_file_info()` and `v2_write_file_info()`, disk/memory conversion for `v2r0_disk_dqblk` and `v2r1_disk_dqblk`, dquot operations `v2_read_dquot()`, `v2_write_dquot()`, `v2_release_dquot()`, `v2_get_next_id()`, and registration for both format ids.

Control flow: Quota-on validates magic and version, reads `v2_disk_dqinfo`, allocates `qtree_mem_dqinfo`, sets limits according to version width, chooses record size and conversion ops, and sanity-checks block counts and free-list heads against quota file size. Reads/writes/release/enumeration delegate to `quota_tree.c` under `dqio_sem`; writes take exclusive I/O locking only if a new entry must be allocated.

State and persistence: Persistent state includes v2 header, info header, qtree metadata, and little-endian dquot entries. v2r0 stores 32-bit inode and block limits plus 64-bit current space; v2r1 expands most counters and limits to 64 bits. Both encode all-zero disk records by setting `dqb_itime` to one so unused slots can still be detected.

Dependencies and integration points: Integrates with generic dquot core through `quota_format_ops`, uses `quota_tree` for storage, `quotaio_v2.h` for ABI structs, filesystem quota read/write, `dqio_sem`, and id mapping through init user namespace ids.

Risks and test signals: Risks include accepting corrupt tree metadata, version/format mismatch, all-zero entry escape mistakes, limit truncation in v2r0, and free-list corruption. Test v0 and v1 quota files, project quota magics, corrupted block counters, get-next-id scans, new dquot allocation, zero-limit records, and 64-bit limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quota_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quotaio_v1.h -->
# sources/distributed-fs/ceph-client/fs/quota/quotaio_v1.h

Purpose: Defines the old VFS quota on-disk record layout and default grace-time constants used by `quota_v1.c`.

Important APIs, types, and functions: Defines `MAX_IQ_TIME`, `MAX_DQ_TIME`, `struct v1_disk_dqblk`, and the offset macro `v1_dqoff(UID)`.

Control flow: The macro computes direct array offsets for v1 quota records. `quota_v1.c` reads and writes records at those offsets and interprets id zero as the source of default grace times.

State and persistence: The disk structure stores 32-bit block limits, current blocks, inode limits, inode usage, and `unsigned long` block/inode grace timers. The `unsigned long` fields make the old format architecture-sensitive.

Dependencies and integration points: Included by `quota_v1.c`; depends only on Linux integer types. It represents the persistent ABI for old external quota files.

Risks and test signals: Risks include on-disk incompatibility across 32-bit and 64-bit systems and direct offset overflow for large ids. Test old quota files created by legacy tools, cross-architecture behavior, and exact record offset calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quotaio_v1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quotaio_v2.h -->
# sources/distributed-fs/ceph-client/fs/quota/quotaio_v2.h

Purpose: Defines the v2 quota file on-disk ABI: magic/version headers, v2r0 and v2r1 disk dquot records, info header fields, and fixed offsets/block sizing.

Important APIs, types, and functions: Defines `V2_INITQMAGICS`, `V2_INITQVERSIONS`, `struct v2_disk_dqheader`, `struct v2r0_disk_dqblk`, `struct v2r1_disk_dqblk`, `struct v2_disk_dqinfo`, `V2_DQINFOOFF`, and `V2_DQBLKSIZE_BITS`.

Control flow: `quota_v2.c` uses the header to validate file type and version, then reads the info structure at `V2_DQINFOOFF`. The quota tree uses 1 KiB logical blocks and leaf records with layouts selected by version.

State and persistence: Stores per-type quota file magic, supported version, grace times, flags, total quota-tree blocks, first free block, first block with a free entry, and per-id quota limits/usage. v2r1 widens most counters to 64 bits while retaining a 32-bit id.

Dependencies and integration points: Included by v2 quota format code and paired with `quota_tree.h`. It depends on little-endian integer types and quota type constants.

Risks and test signals: Risks are ABI drift, endian conversion errors, magic/version mismatch, and counter width truncation. Test header validation for all quota types, v2r0/v2r1 conversion, large limits, and malformed info headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/quota/quotaio_v2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/ramfs/Makefile

Purpose: Builds the ramfs object from common inode code and the correct file-operation implementation for MMU or no-MMU kernels.

Important APIs, types, and functions: Uses Kbuild variables `obj-y`, `file-mmu-y`, `file-mmu-$(CONFIG_MMU)`, and `ramfs-objs`.

Control flow: `ramfs.o` is always built into the core kernel object set when this directory is selected. The default `file-mmu-y` points at `file-nommu.o`; when `CONFIG_MMU=y`, Kbuild substitutes `file-mmu.o`. `ramfs-objs` combines `inode.o` with the selected file implementation.

State and persistence: No runtime state. The selected object determines runtime mmap and file operation behavior.

Dependencies and integration points: Integrates with kernel Kbuild and `CONFIG_MMU`. The exported symbols from either file implementation satisfy references in `inode.c` and `internal.h`.

Risks and test signals: Risks are accidentally linking both file-operation implementations or the wrong one for no-MMU builds. Test by building MMU and no-MMU configurations and confirming only one `ramfs_file_operations` definition is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/file-mmu.c -->
# sources/distributed-fs/ceph-client/fs/ramfs/file-mmu.c

Purpose: Supplies ramfs regular-file operations for MMU systems by composing generic page-cache based VFS helpers.

Important APIs, types, and functions: Defines `ramfs_mmu_get_unmapped_area()`, `ramfs_file_operations`, and `ramfs_file_inode_operations`. File operations include generic read/write iterators, mmap preparation, splice read/write, noop fsync, llseek, and get-unmapped-area.

Control flow: Regular-file inodes created by `ramfs_get_inode()` receive these operation tables. Reads, writes, mmap, splice, fsync, and seek are delegated almost entirely to generic VFS/page-cache helpers. The local unmapped-area wrapper calls `mm_get_unmapped_area()`.

State and persistence: ramfs persists file data only in page cache and marks mappings unevictable in `inode.c`; this file adds no private state. `noop_fsync` reflects the lack of backing storage.

Dependencies and integration points: Depends on the MMU memory-management path, generic file helpers, and ramfs inode setup. It is selected by Kbuild when `CONFIG_MMU` is enabled.

Risks and test signals: Risks are mostly integration regressions with generic mmap/read/write helpers and address selection. Test regular file read/write, shared/private mmap, splice, lseek, truncate through setattr, and fsync no-op behavior on ramfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/file-mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/file-nommu.c -->
# sources/distributed-fs/ceph-client/fs/ramfs/file-nommu.c

Purpose: Supplies ramfs regular-file operations for no-MMU systems, including special handling to create physically contiguous page-cache backing for shared mappings.

Important APIs, types, and functions: Defines `ramfs_mmap_capabilities()`, `ramfs_file_operations`, `ramfs_file_inode_operations`, `ramfs_nommu_expand_for_mapping()`, `ramfs_nommu_resize()`, `ramfs_nommu_setattr()`, `ramfs_nommu_get_unmapped_area()`, and `ramfs_nommu_mmap_prepare()`.

Control flow: On size growth from zero, `ramfs_nommu_resize()` treats the operation as preparation for shared mmap and calls `ramfs_nommu_expand_for_mapping()`, which allocates a high-order contiguous page set, splits it, clears it, inserts pages into the mapping, marks them dirty and uptodate, and pins them in ramfs page cache. On shrink, no-MMU mappings are checked by `nommu_shrink_inode_mappings()`. The get-unmapped-area path verifies the requested range is within EOF and backed by physically adjacent folios.

State and persistence: File contents live in ramfs page cache with dirty, uptodate pages. The implementation depends on contiguous physical memory for direct shared mappings and has no disk persistence.

Dependencies and integration points: Selected when `CONFIG_MMU` is disabled. Integrates with no-MMU mmap APIs, folio batches, page cache insertion, generic read/write/splice helpers, and VFS setattr.

Risks and test signals: Risks include high-order allocation failure, partial page-cache insertion leaks, incorrect shrink refusal while mapped, physical-contiguity detection mistakes, and size overflows beyond 32 bits. Test shared mmap setup, truncate up/down, sparse or missing pages, high memory pressure, non-shared mmap fallback, and no-MMU read/write/splice paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/file-nommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/ramfs/inode.c

Purpose: Implements ramfs filesystem registration, mount-context parsing, superblock setup, inode creation, directory operations, tmpfile support, and teardown.

Important APIs, types, and functions: Defines `struct ramfs_mount_opts`, `struct ramfs_fs_info`, `ramfs_get_inode()`, `ramfs_mknod()`, `ramfs_mkdir()`, `ramfs_create()`, `ramfs_symlink()`, `ramfs_tmpfile()`, `ramfs_dir_inode_operations`, `ramfs_show_options()`, `ramfs_ops`, `ramfs_fs_parameters`, `ramfs_parse_param()`, `ramfs_fill_super()`, `ramfs_get_tree()`, `ramfs_free_fc()`, `ramfs_init_fs_context()`, `ramfs_kill_sb()`, and `ramfs_fs_type`.

Control flow: Mount setup allocates `ramfs_fs_info`, defaults mode to 0755, parses `mode=` while ignoring unknown historical options, and calls `get_tree_nodev()`. Superblock fill sets ramfs magic, page-sized blocks, simple super operations, non-caching dentries, and creates a root directory inode. Inode creation assigns ownership, `ram_aops`, high-user GFP, unevictable mapping, timestamps, and type-specific operation tables. Directory operations use simple VFS helpers after security initialization.

State and persistence: All file data and metadata live in memory only. Superblock private info stores mount mode. Inode address spaces are unevictable and have no backing device. `kill_anon_super()` drops the anonymous in-memory superblock.

Dependencies and integration points: Uses VFS fs-context API, simple directory helpers, page symlink helpers, LSM inode initialization, generic ramfs file ops from the selected file implementation, and `FS_USERNS_MOUNT`.

Risks and test signals: Risks include unlimited memory consumption, mount option compatibility, security xattr initialization failures, link-count mistakes, tmpfile completion errors, and user namespace mount behavior. Test mount with and without `mode=`, create/link/unlink/rename/mkdir/rmdir/symlink/tmpfile flows, memory pressure, and teardown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/ramfs/internal.h

Purpose: Provides the minimal private ramfs declaration shared between `inode.c` and the selected file-operation implementation.

Important APIs, types, and functions: Declares external `ramfs_file_inode_operations`.

Control flow: `inode.c` includes this header to assign regular-file inode operations in `ramfs_get_inode()`. The symbol is defined by either `file-mmu.c` or `file-nommu.c`, selected by Kbuild.

State and persistence: No state or persistence is defined here.

Dependencies and integration points: Depends on VFS `struct inode_operations` declarations from included kernel headers through users. It is part of the build-time contract between ramfs inode and file implementations.

Risks and test signals: Risk is symbol mismatch if Kbuild selection changes or one file implementation stops exporting the declaration. Test both MMU and no-MMU builds for clean linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ramfs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/read_write.c -->
# sources/distributed-fs/ceph-client/fs/read_write.c

Purpose: Implements core VFS read, write, seek, vector I/O, sendfile, copy-file-range, and generic write/copy validation helpers used by syscalls and in-kernel callers.

Important APIs, types, and functions: Exports `generic_ro_fops`, `vfs_setpos()`, `generic_file_llseek_size()`, `generic_llseek_cookie()`, `generic_file_llseek()`, fixed/noop/default llseek helpers, `vfs_llseek()`, `rw_verify_area()`, `kernel_read()`, `__kernel_write()`, `kernel_write()`, `vfs_iocb_iter_read()`, `vfs_iter_read()`, `vfs_iocb_iter_write()`, `vfs_iter_write()`, `vfs_copy_file_range()`, `generic_write_check_limits()`, `generic_write_checks_count()`, `generic_write_checks()`, `generic_file_rw_checks()`, and `generic_atomic_write_valid()`. Syscalls include read/write, pread/pwrite, readv/writev, preadv/pwritev variants, sendfile, copy_file_range, lseek, and llseek.

Control flow: Descriptor syscalls acquire fd references, snapshot or pass file positions, validate modes and user buffers, call `rw_verify_area()` for offset, LSM, and fsnotify permission checks, then dispatch to legacy `read`/`write` or iter operations. Iter-vector paths import iovecs and either call `read_iter`/`write_iter` or loop over legacy operations. Write paths bracket filesystem mutation with write-start/end helpers. `sendfile` and `copy_file_range` validate both files, clamp counts, prefer filesystem copy/remap support, and fall back to splice where allowed.

State and persistence: Mutates `file->f_pos`, file contents through filesystem operations, per-task I/O accounting counters, fsnotify state, and writeback/freeze state via write-start helpers. It stores no long-lived private state.

Dependencies and integration points: Central integration layer for syscall ABI, fd management, file operations, security hooks, fsnotify, splice, page cache, mount/freeze write protection, rlimits, compat syscalls, and filesystem-specific copy/remap implementations.

Risks and test signals: Risks include f_pos races, signed offset overflow, compat return truncation, missed permission checks, incorrect short-copy semantics, write freeze deadlocks, splice fallback inconsistencies, and append/nowait/direct-I/O validation errors. Test concurrent read/write/lseek, stream files, compat syscalls, RLIMIT_FSIZE, O_APPEND pwritev, copy_file_range across same and different superblocks, sendfile to files and pipes, and invalid user iovecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/read_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/readdir.c -->
# sources/distributed-fs/ceph-client/fs/readdir.c

Purpose: Implements VFS directory iteration and the `old_readdir`, `getdents`, and `getdents64` syscall ABIs, including compat variants.

Important APIs, types, and functions: Exports `wrap_directory_iterator()` and `iterate_dir()`. Defines directory entry callback state for old, getdents, getdents64, and compat ABIs plus fill functions `fillonedir()`, `filldir()`, `filldir64()`, `compat_fillonedir()`, and `compat_filldir()`.

Control flow: `iterate_dir()` checks `iterate_shared`, read permissions, fsnotify permission, takes shared inode lock, copies `file->f_pos` into `ctx->pos`, calls the filesystem iterator, writes back the new position, and records access. Legacy filesystem iterators can call `wrap_directory_iterator()` to downgrade from shared to exclusive locking. Fill callbacks validate names, compute ABI record lengths, check inode-number overflow, copy entries to user memory with unsafe user-access blocks, defer final `d_off` update until the next entry or syscall completion, and return false on full buffers or errors.

State and persistence: Mutates directory file position and user-provided dirent buffers. No directory contents are persisted here; filesystem iterators provide entries.

Dependencies and integration points: Depends on filesystem `iterate_shared`, VFS inode locks, security and fsnotify hooks, `dir_context`, user-copy primitives, compat ABI structures, and dirent layout definitions.

Risks and test signals: Risks include user-buffer overflow, wrong record alignment, inode-number overflow on 32-bit ABIs, corrupted names with slash or invalid length, signal interruption behavior, and stale position updates. Test small buffers, exact-fit buffers, invalid names from test filesystems, 64-bit inode values on 32-bit getdents, compat syscalls, concurrent directory mutation, and legacy wrapper locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/readdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/remap_range.c -->
# sources/distributed-fs/ceph-client/fs/remap_range.c

Purpose: Implements generic validation and VFS dispatch for file range cloning and deduplication, including data comparison for dedupe and exported helpers for filesystem remap implementations.

Important APIs, types, and functions: Exports `remap_verify_area()`, `generic_remap_file_range_prep()`, `vfs_clone_file_range()`, `vfs_dedupe_file_range_one()`, and `vfs_dedupe_file_range()`. Internal helpers include `generic_remap_checks()`, `generic_remap_check_len()`, folio locking helpers, `vfs_dedupe_file_range_compare()`, and `may_dedupe_file()`.

Control flow: Clone validation checks same-superblock, regular files, read/write modes, remap operation availability, permissions, and destination write bracketing before calling filesystem `remap_file_range`. Dedupe validates source metadata, caps length to 1 GiB, preinitializes per-destination statuses, verifies each destination fd, takes mount write access, checks ownership or write permission, and dispatches with `REMAP_FILE_DEDUP`. Generic prep checks block alignment, offsets, EOF, overlap, write limits, direct I/O completion, dirty page writeback, optional byte-for-byte compare, partial EOF block constraints, and `file_modified()`.

State and persistence: Mutates destination filesystem extent mappings through filesystem remap operations. Dedupe comparison reads page-cache or DAX data but persists only if the filesystem replaces duplicate destination ranges. Per-destination status is written back into the user-provided dedupe request structure before return.

Dependencies and integration points: Depends on generic VFS read/write checks from `read_write.c`, LSM and fsnotify permission checks, page cache folios, DAX compare support, mount write access, filesystem `remap_file_range`, and ioctl-level dedupe callers.

Risks and test signals: Risks include deduping non-identical data, overlapping same-file ranges, partial EOF block corruption, missing write permission on destination, stale page-cache compare races, DAX/non-DAX divergence, and incorrect shortened-length reporting. Test clone and dedupe across filesystems, same-file overlaps, unaligned ranges, partial EOF blocks, dirty data, DAX files, immutable and swapfile inodes, no-write-permission destinations, and multi-destination dedupe statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/remap_range.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/Kconfig -->
# sources/distributed-fs/ceph-client/fs/resctrl/Kconfig

Purpose: Defines configuration switches for the CPU resource control filesystem and related architecture-dependent features.

Important APIs, types, and functions: Defines `RESCTRL_FS`, `RESCTRL_FS_PSEUDO_LOCK`, and `RESCTRL_RMID_DEPENDS_ON_CLOSID`. `RESCTRL_FS` depends on `ARCH_HAS_CPU_RESCTRL`, selects `KERNFS`, and selects `PROC_CPU_RESCTRL` when `PROC_FS` is enabled.

Control flow: During configuration, enabling `RESCTRL_FS` includes the mountable resctrl filesystem for hardware cache and memory-bandwidth control/monitoring. The pseudo-lock and RMID/CLOSID dependency symbols are internal bools selected or depended on by architecture code and resctrl implementation code.

State and persistence: No runtime state is stored here. The selected options decide whether resctrl code is compiled and whether optional pseudo-lock and allocator behavior is available.

Dependencies and integration points: Integrates architecture resource-control capabilities with kernfs, procfs support, and the resctrl build rules. Documentation is referenced at `Documentation/filesystems/resctrl.rst`.

Risks and test signals: Risks include enabling resctrl without architecture support, missing kernfs/proc dependencies, or inconsistent pseudo-lock configuration. Test with architectures that support and do not support CPU resctrl, with and without procfs, and with pseudo-lock capable configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/Makefile -->
# sources/distributed-fs/ceph-client/fs/resctrl/Makefile

Purpose: Builds the resctrl filesystem objects according to Kconfig selections and sets a local include path for trace header generation.

Important APIs, types, and functions: Uses `obj-$(CONFIG_RESCTRL_FS)` for `rdtgroup.o`, `ctrlmondata.o`, and `monitor.o`; uses `obj-$(CONFIG_RESCTRL_FS_PSEUDO_LOCK)` for `pseudo_lock.o`; sets `CFLAGS_monitor.o = -I$(src)`.

Control flow: If `RESCTRL_FS` is enabled, the core group, control/monitor data, and monitor implementation objects are linked. If pseudo-locking is enabled, the pseudo-lock object is added. `monitor.o` receives the source directory include path so `define_trace.h` recursive include expectations are satisfied.

State and persistence: No runtime state is defined here. Build selections determine which resctrl runtime features exist.

Dependencies and integration points: Integrates Kbuild with Kconfig symbols from `fs/resctrl/Kconfig` and with tracepoint header include mechanics.

Risks and test signals: Risks are missing objects under a config, trace include failures, or pseudo-lock object linkage without its dependencies. Test all relevant resctrl config combinations and confirm `monitor.o` trace compilation succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/resctrl/Makefile -->
