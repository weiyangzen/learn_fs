# Group Research: group_754_linux_sources_os_linux_linux_fs_fhandle_c_sources_os_linux_linux_fs__811822036431

Scope checked against `Docs/research_subset_a.md`; all listed files are under `sources/os/linux/linux`. Every source file in this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fhandle.c -->
# File Research: sources/os/linux/linux/fs/fhandle.c

Read status: complete, 474 lines.

Purpose: implements the Linux file-handle syscalls `name_to_handle_at()` and `open_by_handle_at()`, translating pathnames to exportfs file handles and decoding handles back into paths/files.

Key flow:
- `do_sys_name_to_handle()` validates exportfs encoding support, copies the user `file_handle`, calls `exportfs_encode_fh()`, handles overflow/invalid handle conventions, and writes either legacy or unique mount id.
- `name_to_handle_at()` validates `AT_*` flags, rejects conflicting `AT_HANDLE_CONNECTABLE` combinations, performs `filename_lookup()`, and delegates handle encoding.
- `get_path_anchor()` anchors decode against a mount fd, cwd, pidfs root, or nsfs root.
- `handle_to_path()` copies and validates the user handle, checks filesystem-specific or generic decode permission, strips user-visible handle flags, and calls `exportfs_decode_fh_raw()`.
- `open_by_handle_at()` decodes the handle and opens it via exportfs `open()` or `file_open_root()`.

Important dependencies: exportfs, mount namespace helpers, fd RAII helpers, `CAP_DAC_READ_SEARCH`, `CAP_SYS_ADMIN`, idmapped mount checks, pidfs/nsfs root helpers, and `FD_ADD()` file publishing.

Security/concurrency notes:
- Decoding is strict unless global `CAP_DAC_READ_SEARCH` is present.
- Relaxed decode requires `O_DIRECTORY`, mount/subtree checks, idmap reachability checks, and DAC override in the caller's user namespace.
- Connectable handles encode user-visible bits so decode can enforce subtree and directory-only constraints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fhandle.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/file.c -->
# File Research: sources/os/linux/linux/fs/file.c

Read status: complete, 1531 lines.

Purpose: manages per-process file descriptor tables: allocation, expansion, cloning, fd installation, close/close_range, fd lookup, dup/dup2/dup3, close-on-exec, and descriptor iteration.

Key flow:
- `__file_ref_put()` is the file reference slowpath, handling last-reference transition to `FILE_REF_DEAD`, saturated counts, and imbalanced puts.
- `alloc_fdtable()`, `expand_fdtable()`, and `expand_files()` grow fd arrays and bitmaps while coordinating with lockless `fd_install()` using `resize_in_progress`, RCU grace periods, and memory barriers.
- `dup_fd()` clones a `files_struct`, optionally punching a `close_range()` hole, and clears reserved-but-uninstalled fd slots in the clone.
- `alloc_fd()`, `get_unused_fd_flags()`, `fd_install()`, `put_unused_fd()`, and `file_close_fd_locked()` maintain open fd bitmaps, close-on-exec bitmaps, `full_fds_bits`, and pointer table invariants.
- `close_range()` supports close, cloexec marking, and optional unshare of shared descriptor tables.
- `__fget_files_rcu()`, `fget()`, `fdget()`, and `fdget_pos()` implement RCU-safe fd lookup, borrowed references for unshared tables, and `f_pos` locking for shared atomic-position files/directories.
- `replace_fd()`, `receive_fd()`, `ksys_dup3()`, `dup2()`, `dup()`, `f_dupfd()`, and `iterate_fd()` implement fd replacement, received-fd install, duplication, and table walking.

Important dependencies: `fdtable`, RCU, `file_ref`, process `files_struct`, `RLIMIT_NOFILE`, socket receive hooks, LSM receive checks, and `close_range` flags.

Risk/concurrency notes:
- The file is highly sensitive to RCU ordering and `SLAB_TYPESAFE_BY_RCU` reuse; pointer reloads and refcount acquisition must stay paired.
- `fd_install()` assumes a descriptor slot has been reserved and still contains NULL.
- `do_dup2()` returns `-EBUSY` for races with a reserved-but-not-installed target fd.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/file_attr.c -->
# File Research: sources/os/linux/linux/fs/file_attr.c

Read status: complete, 486 lines.

Purpose: central VFS implementation for miscellaneous file attributes exposed through legacy ioctls and the `file_getattr` / `file_setattr` syscalls.

Key flow:
- `fileattr_fill_xflags()` and `fileattr_fill_flags()` translate between `FS_XFLAG_*` and legacy `FS_*_FL` flags.
- `vfs_fileattr_get()` checks LSM permission and calls filesystem `i_op->fileattr_get`.
- `vfs_fileattr_set()` checks ownership/capability, locks the inode, reads current attributes, fills unspecified fields from old attributes, validates policy in `fileattr_set_prepare()`, calls LSM set hook, invokes filesystem `fileattr_set`, and emits `fsnotify_xattr`.
- Legacy ioctl helpers wrap `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, and `FS_IOC_FSSETXATTR`.
- `file_getattr` and `file_setattr` support pathname or `AT_EMPTY_PATH` fd targeting and copy extensible `struct file_attr` to/from userspace.

Important dependencies: inode operations, LSM hooks, fscrypt flag validation, idmapped mount ownership checks, mount write access, and `copy_struct_*_user`.

Validation/security notes:
- Immutable and append-only flag changes require `CAP_LINUX_IMMUTABLE`.
- Project quota id changes are restricted to the initial user namespace.
- Extent-size, cowextsize, and DAX flags are type-restricted.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/file_attr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/file_table.c -->
# File Research: sources/os/linux/linux/fs/file_table.c

Read status: complete, 667 lines.

Purpose: allocates, initializes, accounts, and releases global `struct file` objects.

Key flow:
- Maintains `/proc/sys/fs/file-nr`, `file-max`, and `nr_open` sysctls with a percpu `nr_files` counter.
- `init_file()` initializes credentials, security state, locks, fsnotify mode, file flags/mode, mapping state, error samples, and `f_ref`.
- `alloc_empty_file()`, `alloc_empty_file_noaccount()`, and `alloc_empty_backing_file()` allocate regular, unaccounted, or backing-file wrappers.
- `file_init_path()`, `alloc_file_pseudo()`, `alloc_file_pseudo_noaccount()`, and `alloc_file_clone()` bind files to paths/inodes/file-ops.
- `__fput()` performs final close teardown: fsnotify close, epoll release, locks, LSM release, fasync, file op release, cdev put, fops put, owner/access/path/mount cleanup, and file cache free.
- `fput()` defers final teardown through task work when possible, with delayed work fallback for interrupts/kernel threads; sync variants run immediate final put.
- `files_init()` creates `filp` and backing-file caches as `SLAB_TYPESAFE_BY_RCU`.

Important dependencies: LSM, fsnotify, epoll, file locks, cdevs, mount lifetime, percpu counters, task work, delayed work, and `SLAB_TYPESAFE_BY_RCU` caches.

Risk/concurrency notes:
- `struct file` cache is `SLAB_TYPESAFE_BY_RCU`; initialization places `f_ref` last so RCU lookup users do not treat partially reinitialized objects as valid.
- Deferred fput paths must avoid deadlocks around umount and kernel thread contexts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/file_table.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/filesystems.c -->
# File Research: sources/os/linux/linux/fs/filesystems.c

Read status: complete, 413 lines.

Purpose: maintains the kernel registry of filesystem types and exposes lookup/listing interfaces.

Key flow:
- `register_filesystem()` validates parser descriptions, rejects duplicate names, links a `file_system_type` into an RCU hlist, and invalidates the cached `/proc/filesystems` string.
- `unregister_filesystem()` removes from the RCU hlist and waits for readers with `synchronize_rcu()`.
- Optional `sysfs(2)` compatibility handlers return filesystem index/name/count.
- `list_bdev_fs_names()` emits registered block-device-backed filesystem names for early boot use.
- `/proc/filesystems` uses a generation-stamped cached string, regenerated lazily and invalidated on registry changes.
- `get_fs_type()` looks up a type, requests `fs-<name>` module autoload on miss, and enforces subtype support after a dot suffix.

Important dependencies: module references, RCU hlist traversal, procfs seq output, kmod autoloading, and filesystem parser validation.

Risk/concurrency notes:
- Readers must take module references before using an fs type after leaving RCU.
- Cached proc output is intentionally best-effort; allocation failure falls back to direct seq iteration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/filesystems.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/freevxfs/Kconfig

Read status: complete, 27 lines.

Purpose: declares `CONFIG_VXFS_FS` for FreeVxFS support.

Content:
- `tristate "FreeVxFS file system support (VERITAS VxFS(TM) compatible)"`.
- Depends on `BLOCK` and selects `BUFFER_HEAD`.
- Documents read-only support for VxFS versions 2, 3, and 4, with tested SCO UnixWare and HP-UX variants.
- Module name is `freevxfs`; mount filesystem type is `vxfs`.

Integration note: this config enables the read-only block-device filesystem driver built by the adjacent Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/Makefile -->
# File Research: sources/os/linux/linux/fs/freevxfs/Makefile

Read status: complete, 9 lines.

Purpose: builds the FreeVxFS module.

Content:
- `obj-$(CONFIG_VXFS_FS) += freevxfs.o`.
- Links `freevxfs.o` from `vxfs_bmap.o`, `vxfs_fshead.o`, `vxfs_immed.o`, `vxfs_inode.o`, `vxfs_lookup.o`, `vxfs_olt.o`, `vxfs_subr.o`, and `vxfs_super.o`.

Integration note: all implementation files in this batch are compiled into one module when `CONFIG_VXFS_FS` is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs.h -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs.h

Read status: complete, 257 lines.

Purpose: defines FreeVxFS superblock structures, endian helpers, inode mode constants, organization types, and superblock-private accessor macros.

Key content:
- Defines `VXFS_SUPER_MAGIC`, `VXFS_ROOT_INO`, and on-disk fixed-width endian-marked types `__fs16`, `__fs32`, `__fs64`.
- `struct vxfs_sb` models the VxFS disk superblock fields used by the driver, including block size, AU geometry, inode sizing, free counts, OLT location, and version fields.
- `struct vxfs_sb_info` stores mounted-state metadata: raw superblock buffer, fileset header inode, inode-list inodes, initial inode-list extent, OLT location/size, and byte order.
- `fs16_to_cpu()`, `fs32_to_cpu()`, and `fs64_to_cpu()` decode on-disk values according to detected byte order.
- Defines VxFS file type bits, internal structural inode types, organization types (`NONE`, `EXT4`, `IMMED`, `TYPED`), and predicate macros.

Important dependencies: Linux endian helpers, `struct super_block`, `struct buffer_head`, and FreeVxFS inode/OLT readers.

Risk note: many on-disk structures are partial models of VxFS and comments state later/variant fields are omitted.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_bmap.c -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_bmap.c

Read status: complete, 271 lines.

Purpose: maps VxFS logical file blocks to physical disk blocks for internal reads and page-cache block mapping.

Key flow:
- `vxfs_bmap_ext4()` handles ext4-style VxFS inode organizations: scans direct extents, then tries indirect extents.
- `vxfs_bmap_indir()` recursively walks typed indirect extent blocks and resolves typed data extents.
- `vxfs_bmap_typed()` scans the inode's inline typed extent descriptors and recurses or resolves data extents.
- `vxfs_bmap1()` dispatches by inode organization: `EXT4` and `TYPED` supported; `NONE` and `IMMED` return unsupported; unknown orgtypes warn and BUG.

Important dependencies: `sb_bread()`, buffer heads, `vxfs_inode_info`, endian helpers, and typed extent format.

Risk notes:
- DEV4 typed extents are detected but unsupported.
- Unknown typed extent headers call `BUG()`, so malformed media can trigger hard failure paths.
- The ext4-style indirect calculation is subtle and depends on on-disk `indsize` correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_dir.h -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_dir.h

Read status: complete, 68 lines.

Purpose: defines VxFS on-disk directory block and directory entry structures.

Key content:
- `struct vxfs_dirblk` contains free-space and hash-chain metadata at the start of each directory block.
- `VXFS_NAMELEN` is 256.
- `struct vxfs_direct` stores inode number, record length, name length, hash-next pointer, and name bytes.
- Directory entry alignment helpers define 4-byte padding, minimum record size, rounded length, and per-block overhead.

Used by: `vxfs_lookup.c` for directory scanning and `vxfs_super.c` for statfs name length.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_extern.h -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_extern.h

Read status: complete, 49 lines.

Purpose: declares cross-file FreeVxFS symbols.

Exports declared:
- Block mapping: `vxfs_bmap1`.
- Fileset setup: `vxfs_read_fshead`.
- Inode operations: `vxfs_blkiget`, `vxfs_stiget`, `vxfs_iget`, `vxfs_evict_inode`, diagnostic `vxfs_dumpi` when built.
- Directory ops: `vxfs_dir_inode_ops`, `vxfs_dir_operations`.
- OLT setup: `vxfs_read_olt`.
- Page/block helpers: `vxfs_aops`, `vxfs_get_page`, `vxfs_put_page`, `vxfs_bread`.

Integration note: this header is the local module boundary tying the FreeVxFS object files together.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_fshead.c -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_fshead.c

Read status: complete, 166 lines.

Purpose: reads VxFS fileset headers and initializes inode-list inodes needed for normal inode lookup.

Key flow:
- `vxfs_getfsh()` reads a fileset header block through `vxfs_bread()`, copies it into kmalloc memory, and releases the buffer.
- `vxfs_read_fshead()` reads the fileset header inode using OLT-derived `vsi_iext` and `vsi_fshino`.
- Validates the fileset header inode is `VXFS_IFFSH`.
- Reads structural and primary fileset headers.
- Reads and validates the structural inode list and primary inode list as `VXFS_IFILT`.
- Stores `vsi_fship`, `vsi_stilist`, and `vsi_ilist` in superblock-private state.

Important dependencies: `vxfs_blkiget`, `vxfs_stiget`, `vxfs_bread`, `vxfs_fsh`, and inode type predicates.

Failure handling: releases partially acquired inodes and allocated header copies before returning `-EINVAL`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_fshead.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_fshead.h -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_fshead.h

Read status: complete, 43 lines.

Purpose: defines the VxFS fileset header on-disk structure used by `vxfs_fshead.c`.

Key content:
- `struct vxfs_fsh` contains version, fileset index, timestamp, inode counts, IAU inode, two ilist inode numbers, and link-count table inode.
- Comments state more fields follow on disk but differ by VxFS version/port and are not modeled.

Integration note: only fields needed to discover inode-list inodes are represented.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_fshead.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_immed.c -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_immed.c

Read status: complete, 53 lines.

Purpose: provides address-space operations for VxFS immediate-data inodes, whose file data is stored inside the inode body.

Key flow:
- `vxfs_immed_read_folio()` locates inline data from `VXFS_INO(folio->mapping->host)->vii_immed.vi_immed + folio_pos(folio)`.
- Copies one or more pages into the folio, marks the folio uptodate, and unlocks it.
- `vxfs_immed_aops` exposes only `.read_folio`.

Risk note: correctness relies on VFS/file-size constraints preventing reads beyond the inline immediate data area; the routine itself does not clamp copy length to inode size or `VXFS_NIMMED`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_immed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_inode.c -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_inode.c

Read status: complete, 314 lines.

Purpose: reads VxFS disk inodes into Linux inodes and assigns VFS operations.

Key flow:
- `vxfs_transmod()` translates VxFS mode/type bits to Linux `S_IF*` mode bits.
- `dip2vip_cpy()` endian-converts stable inode fields, copies organization-specific data raw, and populates VFS uid/gid/nlink/size/timestamps/blocks/generation.
- `vxfs_blkiget()` reads an inode directly from a specified disk extent via buffer cache for mount-time structural metadata.
- `__vxfs_iget()` reads an inode from an inode-list file via page cache.
- `vxfs_stiget()` creates structural inodes from the structural inode list.
- `vxfs_iget()` uses `iget_locked()` for normal inodes, reads from `vsi_ilist`, assigns regular file, directory, symlink, or special inode operations, and handles immediate symlink data.
- `vxfs_evict_inode()` truncates pages and clears the inode.

Important dependencies: inode-list setup from `vxfs_fshead.c`, page helpers in `vxfs_subr.c`, directory ops, immediate and normal address-space ops.

Risk notes:
- Structural inode reads use `new_inode()` with generated inode numbers, distinct from normal cached inode lookup.
- Organization-specific fields are not endian-swapped until interpreted by later mapping code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_inode.h -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_inode.h

Read status: complete, 169 lines.

Purpose: defines VxFS on-disk and in-memory inode structures plus extent descriptor formats.

Key content:
- Constants for disk inode size, direct/indirect extent counts, immediate data size, typed extent count, and typed extent header masks.
- Typed extent descriptor types include indirect/data and DEV4 variants.
- `struct vxfs_dinode` models on-disk inode metadata, timestamps, type/organization, rdev/dotdot/regular/vxspec union, block count, generation, version, and organization-specific data.
- `struct vxfs_inode_info` embeds `struct inode` and stores converted VxFS metadata plus raw organization data.
- `VXFS_INO()` maps a VFS inode to its containing FreeVxFS inode.

Used by: almost every FreeVxFS implementation file.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_lookup.c -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_lookup.c

Read status: complete, 273 lines.

Purpose: implements FreeVxFS directory lookup and readdir.

Key flow:
- Defines directory inode ops with `.lookup = vxfs_lookup` and directory file ops with llseek/read/iterate/setlease.
- `vxfs_find_entry()` scans directory pages, skips each VxFS directory block header/hash overhead, advances by `d_reclen`, and matches name length and bytes.
- `vxfs_inode_by_name()` returns the inode number from a matching directory entry.
- `vxfs_lookup()` rejects names longer than `VXFS_NAMELEN`, resolves inode numbers, and returns `d_splice_alias()`.
- `vxfs_readdir()` emits `.` and `..`, scans directory records similarly to lookup, emits entries as `DT_UNKNOWN`, and updates `ctx->pos`.

Important dependencies: `vxfs_get_page`, `vxfs_put_page`, directory format helpers, and `vxfs_iget`.

Risk notes:
- Directory parsing trusts on-disk `d_reclen`, `d_namelen`, and block overhead enough to drive iteration.
- Error from `vxfs_get_page()` in readdir is reported as `-ENOMEM` regardless of actual underlying error.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_olt.c -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_olt.c

Read status: complete, 105 lines.

Purpose: reads the VxFS Object Location Table to discover core metadata locations.

Key flow:
- `vxfs_oblock()` converts an on-disk block number at filesystem block size to current superblock block units.
- `vxfs_read_olt()` reads the OLT extent, validates `VXFS_OLT_MAGIC`, rejects multi-block OLT extents, then walks OLT records.
- Recognizes `VXFS_OLT_FSHEAD` to set `vsi_fshino` and `VXFS_OLT_ILIST` to set `vsi_iext`.
- Returns success only if both fileset header inode and initial inode-list extent were found.

Important dependencies: superblock-private OLT location/size from `vxfs_super.c`, OLT structure definitions, and endian helpers.

Risk note: only single-block OLT extents are supported.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_olt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_olt.h -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_olt.h

Read status: complete, 120 lines.

Purpose: defines VxFS Object Location Table headers and record formats.

Key content:
- Defines `VXFS_OLT_MAGIC`.
- Enumerates OLT record types: free, fileset header, current usage table, inode list, device, and superblock/log/OLT inode records.
- `struct vxfs_olt` models the OLT extent header.
- Defines common/free/ilist/cut/sb/dev/fshead record structures.

Used by: `vxfs_olt.c` to find the fileset header inode and initial inode-list extent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_olt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_subr.c -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_subr.c

Read status: complete, 152 lines.

Purpose: shared FreeVxFS page-cache, buffer, and block-mapping helpers.

Key flow:
- `vxfs_aops` supplies normal `.read_folio` and `.bmap`.
- `vxfs_get_page()` reads a mapping page via `read_mapping_page()` and kmaps it.
- `vxfs_put_page()` kunmaps and drops a page.
- `vxfs_bread()` maps a logical inode block through `vxfs_bmap1()` and reads the physical block via `sb_bread()`.
- `vxfs_getblk()` maps buffer heads for block reads; returns `-EIO` when mapping is zero.
- `vxfs_read_folio()` delegates to `block_read_full_folio()`.
- `vxfs_bmap()` delegates to `generic_block_bmap()`.

Important dependencies: `vxfs_bmap1`, buffer-head block helpers, and page cache read helpers.

Risk note: this is read-only support; block creation is ignored even though the get_block signature includes `create`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_super.c -->
# File Research: sources/os/linux/linux/fs/freevxfs/vxfs_super.c

Read status: complete, 347 lines.

Purpose: mounts, registers, and tears down the FreeVxFS filesystem.

Key flow:
- Defines module metadata and `vxfs_inode_cachep`.
- `vxfs_put_super()` releases fileset/header/list inodes, raw superblock buffer, and superblock-private allocation.
- `vxfs_statfs()` fills basic statfs fields from the raw VxFS superblock.
- `vxfs_reconfigure()` always syncs and forces read-only.
- Super operations allocate/free private VxFS inodes, evict inodes, put superblock, and statfs.
- `vxfs_try_sb_magic()` reads candidate superblock locations and compares raw magic with expected endian encoding.
- `vxfs_fill_super()` forces read-only, allocates `vxfs_sb_info`, finds little-endian UnixWare or big-endian HP-UX superblock, checks VxFS version 2-4, sets block size, reads OLT, reads fileset headers, loads root inode, and creates root dentry.
- Registers `file_system_type` named `vxfs`, requiring a block device, with fs_context get-tree/reconfigure hooks.
- Module init creates a usercopy-aware inode cache and registers the filesystem; exit unregisters, waits for RCU, and destroys the cache.

Important dependencies: block-device mount helper `get_tree_bdev`, VFS fs_context, `register_filesystem`, OLT/fileset/inode readers.

Risk notes:
- The driver is strictly read-only.
- Superblock discovery is limited to known UnixWare and HP-UX offsets/endianness.
- Some mount failure paths free `s_fs_info` resources locally; normal unmount uses `put_super`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/freevxfs/vxfs_super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fs-writeback.c -->
# File Research: sources/os/linux/linux/fs/fs-writeback.c

Read status: complete, 3082 lines.

Purpose: core Linux writeback engine for dirty inode/page writeout, flusher work scheduling, cgroup writeback ownership, dirtytime expiration, and sync helpers.

Key flow:
- Defines `struct wb_writeback_work`, writeback work queuing, completion waiting, and per-`bdi_writeback` wakeup/delayed wakeup helpers.
- Maintains dirty IO list state across `b_dirty`, `b_io`, `b_more_io`, and `b_dirty_time`, including bandwidth accounting via `WB_has_dirty_io`.
- With `CONFIG_CGROUP_WRITEBACK`, attaches inodes to cgroup-specific writeback contexts, detects foreign dirtier ownership using history plus Boyer-Moore majority voting, and asynchronously switches inode writeback ownership through `inode_switch_wbs_work_fn()`.
- Splits writeback work across per-bdi writeback contexts proportionally to write bandwidth.
- `queue_io()` moves expired dirty and dirtytime inodes into dispatch queues.
- `__writeback_single_inode()` runs `do_writepages()`, optionally waits for data, handles lazytime expiration, clears/reinstates dirty flags with memory barriers, writes inode metadata, and tracks netfs writeback pinning.
- `writeback_sb_inodes()` and `__writeback_inodes_wb()` batch writeback by superblock and inode list, balancing progress, lock dropping, `I_SYNC` handling, and requeue decisions.
- `wb_writeback()`, `wb_do_writeback()`, and `wb_workfn()` are the flusher work loop, processing explicit work, start-all, dontcache, periodic old-data, and background threshold writeback.
- Public wakeup helpers start flusher work for one bdi or all bdis.
- Dirtytime infrastructure periodically wakes writeback for `I_DIRTY_TIME` inodes and exposes `vm.dirtytime_expire_seconds`.
- `__mark_inode_dirty()` notifies filesystems of dirty inode state, handles dirtytime promotion, attaches writeback context, and queues inodes on the correct dirty list.
- Sync helpers include `writeback_inodes_sb_nr()`, `writeback_inodes_sb()`, `try_to_writeback_inodes_sb()`, `sync_inodes_sb()`, `write_inode_now()`, and `sync_inode_metadata()`.

Important dependencies: backing-dev writeback infrastructure, page cache tags, memcg/cgroup writeback, block plug flushing, superblock locks, inode state bits, tracepoints, and sysctl.

Concurrency/security notes:
- Lock ordering spans `wb->list_lock`, `inode->i_lock`, `mapping->i_pages`, `sb->s_umount`, `s_inode_wblist_lock`, and `wb_switch_rwsem`.
- Memory barriers pair dirty marking with dirty clearing so lockless state checks do not lose dirty events.
- Sync paths guard against inode writeback context switching and wait on in-flight page writeback lists.
- Cgroup inode switching pins superblocks during switch work to avoid umount races.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fs-writeback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/fs_context.c -->
# File Research: sources/os/linux/linux/fs/fs_context.c

Read status: complete, 568 lines.

Purpose: implements generic VFS filesystem context allocation, mount option parsing, logging, duplication, cleanup, and disposal.

Key flow:
- `vfs_parse_sb_flag()` handles common superblock flags such as `ro/rw`, `sync/async`, `dirsync`, `lazytime/nolazytime`, and `mand/nomand`.
- `vfs_parse_fs_param()` validates parameter names, handles common flags, lets LSMs consume options, delegates to filesystem `parse_param`, and falls back to generic `source`.
- `vfs_parse_fs_qstr()`, `vfs_parse_monolithic_sep()`, and `generic_parse_monolithic()` provide helper paths for qstr and comma-separated legacy mount data.
- `alloc_fs_context()` allocates and initializes `struct fs_context` for mount, submount, or reconfigure, setting fs type refs, credentials, net namespace, user namespace, root references, and filesystem-specific init.
- `fs_context_for_mount()`, `fs_context_for_reconfigure()`, and `fs_context_for_submount()` create purpose-specific contexts.
- `vfs_dup_fs_context()` copies an existing context, takes references, calls filesystem dup, and duplicates security context.
- `logfc()` either printk logs or stores formatted messages in the context ring buffer.
- `put_fs_context()` releases root/superblock, filesystem private state, security options, namespaces, credentials, logs, fs type, source string, and the context allocation.
- `vfs_clean_context()` and `finish_clean_context()` reset a used context into a reconfiguration-ready state in two phases.

Important dependencies: fs parser, LSM mount hooks, net/user namespaces, filesystem `fs_context_operations`, and mount lifecycle helpers.

Risk/concurrency notes:
- Context cleanup is split so successful mount/remount can report success before a possibly failing reinitialization.
- `logfc()` uses a fixed-size ring and drops the oldest stored message when full.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/fs_context.c -->