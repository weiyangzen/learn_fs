# Group Research: group_772_linux_sources_os_linux_linux_fs_jfs_jfs_xtree_c_sources_os_linux_lin_b6c0f9ea4a56

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_xtree.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_xtree.c

JFS extent allocation descriptor B+tree manager for file data, symlink data, metadata files, and truncate-time block release.

Key responsibilities:
- Implements xtree page access and validation in `xt_getpage()`, rejecting corrupt `nextindex`/`maxentry` combinations.
- Maps logical block ranges to physical extents with `xtLookup()`, including sparse-hole misses and EOF checks.
- Searches xtrees with `xtSearch()`, maintaining traversal stacks, insertion split counts, next-extent hints, and sequential-access heuristics.
- Inserts extents with `xtInsert()`, allocating data blocks when needed, charging quotas, and rolling back allocation on failure.
- Splits full leaf, internal, and root pages through `xtSplitUp()`, `xtSplitPage()`, and `xtSplitRoot()`, including sibling links and router entries.
- Extends an existing adjacent extent in `xtExtend()`, creating a new extent when `MAXXLEN` would be exceeded.
- Updates not-recorded extents in `xtUpdate()`, supporting replacement, left/right coalescing, and two- or three-way extent splitting.
- Provides append-mode growth through `xtAppend()`, used by special sequential files such as the block map during online resize.
- Initializes inline inode roots with `xtInitRoot()`.
- Truncates extents and xtree index pages through `xtTruncate()` and `xtTruncate_pmap()`, with separate persistent-map and working-map behavior.
- Exposes optional statistics via `jfs_xtstat_proc_show()`.

Important interactions:
- Uses JFS metapage helpers through B-tree macros for root-inline and disk-page access.
- Uses block allocator functions such as `dbAlloc()`, `dbAllocBottomUp()`, `dbFree()`, `txFreeMap()`, and maplock structures.
- Uses quota accounting through `dquot_alloc_block()` and `dquot_free_block()`.
- Uses transaction logging through `txLock()`, `tlock`, `xtlock`, `tlckXTREE`, `tlckGROW`, `tlckNEW`, `tlckTRUNCATE`, `tlckFREE`, and relink locks.
- Updates inode state through `JFS_IP(ip)->i_xtroot`, `mode2`, `INLINEEA`, commit flags, and `ip->i_size`.
- Invalidates directory metadata pages when truncating directory xtrees.

Invariants and risks:
- Xtree pages must keep entries ordered by logical offset, with child-router entries pointing to ranges beginning at their keys.
- Root page block number is logically `0`; non-root pages are represented by `pxd_t` self descriptors.
- Insertions must avoid overlap with the next extent; otherwise `xtInsert()` returns `-EEXIST`.
- Split paths must release every pinned metapage exactly once; many error paths are sensitive to page ownership transfer.
- Quota and block-allocation rollback must stay paired, especially around split-page allocation and failed extent insertion.
- Truncate intentionally limits one transaction to `MAX_TRUNCATE_LEAVES` leaf pages to avoid transaction-lock exhaustion; callers may need iterative truncation.
- `COMMIT_Nolink` suppresses xtree logging for files with no directory links, so callers must choose the correct commit mode.
- Root expansion can consume inline EA space, and root shrink can restore `INLINEEA`; incorrect transitions can confuse fsck.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_xtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_xtree.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_xtree.h

Public JFS xtree format and API header.

Key responsibilities:
- Defines `xad_t`, the 16-byte extent allocation descriptor containing flags, 40-bit logical offset, length, and physical address.
- Provides construction and extraction macros for XAD offset, address, and length.
- Defines extent flags: new, extended, compressed, not-recorded, and copy-on-write.
- Defines root and page slot limits, entry start index, and `MAXXLEN`.
- Defines `xtheader`, inline inode root `xtroot_t`, and disk xtree page `xtpage_t`.
- Declares xtree operations for lookup, root initialization, insert, extend, update, truncate, pmap truncate, and append.

Important interactions:
- Depends on `jfs_btree.h` and `pxd_t` layout from JFS metadata definitions.
- Shared by extent allocation, file writeback, truncation, symlink storage, resize, and transaction code.

Invariants and risks:
- The on-disk layout is fixed-size and endian-sensitive.
- Logical offsets are split into `off1` and little-endian `off2`; address and length are delegated to `pxd_t`.
- `XTENTRYSTART` reserves header/router slots and must match B-tree code assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_xtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/namei.c -->
# File Research: sources/os/linux/linux/fs/jfs/namei.c

JFS VFS namespace operation implementation for create, lookup, link, unlink, directory creation/removal, rename, symlink, mknod, and export lookup.

Key responsibilities:
- Implements `jfs_create()`, allocating a new inode, initializing ACL/security xattrs, initializing an xtree root, inserting the parent dtree entry, and committing both inodes.
- Implements `jfs_mkdir()` and `jfs_rmdir()`, including dtree initialization, parent link-count updates, empty-directory checks, and EA/ACL cleanup.
- Implements `jfs_unlink()`, deleting the directory entry, decrementing link count, and using zero-link truncation for the final unlink.
- Implements `commitZeroLink()` and `jfs_free_zero_link()` to split persistent-map freeing from later working-map cleanup for open-but-unlinked files.
- Implements hard link creation in `jfs_link()`, including read-only checks and link-count updates.
- Implements `jfs_symlink()`, storing short symlink targets inline and longer targets in a single xtree-backed extent.
- Implements `jfs_rename()`, including overwrite semantics, directory parent updates, link-count handling, victim cleanup, and iterative pmap truncation.
- Implements `jfs_mknod()` for device/special inode creation.
- Implements `jfs_lookup()` and NFS export helpers `jfs_fh_to_dentry()`, `jfs_fh_to_parent()`, and `jfs_get_parent()`.
- Defines directory inode/file operations and optional case-insensitive dentry operations.

Important interactions:
- Uses JFS dtree operations `dtSearch()`, `dtInsert()`, `dtDelete()`, `dtModify()`, `dtEmpty()`, and `dtInitRoot()`.
- Uses inode allocation/loading helpers `ialloc()` and `jfs_iget()`.
- Uses transaction manager helpers `txBegin()`, `txCommit()`, `txAbort()`, and `txEnd()`.
- Coordinates with xtree truncation through `xtInitRoot()`, `xtInsert()`, `xtTruncate()`, and `xtTruncate_pmap()`.
- Uses quota initialization, ACL initialization, security xattr initialization, and EA/ACL map freeing.
- Uses nested `commit_mutex` ordering for parent, child, second parent, and rename victim inodes.

Invariants and risks:
- Directory dtree pages may be pinned by search, so inode allocation and transaction begin are deliberately done before `dtSearch()` in create paths.
- Failed creates must free uncommitted EA working-map allocations, clear links, and discard the new inode.
- Unlink and rename may require synchronous commits when `xtTruncate_pmap()` only partially frees a large fragmented file.
- `COMMIT_Stale` directory truncation is opportunistic and may need repeated `jfs_truncate_nolock()` calls.
- Rename handles only default and `RENAME_NOREPLACE`; other flags return `-EINVAL`.
- Case-insensitive dentry revalidation intentionally drops negative dentries for create/rename-target intents to preserve user-specified case.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/resize.c -->
# File Research: sources/os/linux/linux/fs/jfs/resize.c

JFS online filesystem extension implementation.

Key responsibilities:
- Implements `jfs_extendfs()` to grow a mounted JFS volume without shrinking existing filesystem space.
- Validates the requested logical-volume size against the block device or by probing the last block.
- Computes new inline-log, fsck workspace, and filesystem data-region sizes.
- Quiesces transactions before changing log and allocation-map state.
- Moves/reformats the inline log when needed and records `FM_EXTENDFS` transition state in the superblock.
- Extends the block allocation map with `dbExtendFS()`, grows the bmap file with append-mode xtree allocation, and finalizes the bmap.
- Extends inode allocation metadata with `diExtendFS()` when allocation-group sizing changes.
- Synchronizes the primary and secondary bmap inodes and updates primary/secondary superblocks.
- Resumes transactions after either success or error.

Important interactions:
- Uses `txQuiesce()` and `txResume()` to block live filesystem transactions.
- Uses log manager operations `lmLogShutdown()`, `lmLogFormat()`, and `lmLogInit()`.
- Uses superblock helpers `readSuper()`, direct buffer writes, and `updateSuper()`-compatible state flags.
- Uses bmap helpers `dbMapFileSizeToMapSize()`, `dbExtendFS()`, `dbFinalizeBmap()`, and `dbSync()`.
- Uses `xtAppend()` to grow the special block-map file in a sequential, replay-safe manner.
- Uses inode-map helpers `diExtendFS()`, `diSync()`, `diReadSpecial()`, `diWriteSpecial()`, and `diFreeSpecial()`.

Invariants and risks:
- Extension refuses read-only filesystems and refuses sizes smaller than the current map size.
- Crash recovery relies on the superblock transition flag and descriptors being written in the expected order.
- Inline-log movement is especially sensitive: the old log is shut down, the new one formatted, and the log serial recorded.
- The bmap file may need iterative growth when a huge extension consumes part of the newly mapped region for map pages.
- Errors after quiesce call `jfs_error()` and still resume transactions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/resize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/super.c -->
# File Research: sources/os/linux/linux/fs/jfs/super.c

JFS filesystem module, mount-context, superblock, quota, freeze, export, and lifecycle implementation.

Key responsibilities:
- Declares module metadata, JFS global worker threads, and the JFS inode slab cache.
- Implements `jfs_error()` and error policy handling: continue, remount read-only, or panic.
- Implements inode allocation/free callbacks for JFS private inode structures.
- Implements `jfs_statfs()` from bmap and imap accounting.
- Parses mount/remount options for integrity, charset, resize, errors policy, quota flags, uid/gid/umask, and discard.
- Implements reconfiguration, including online resize, read-only/read-write transitions, quota suspend/resume, and integrity-mode remounts.
- Implements `jfs_fill_super()` to allocate `jfs_sb_info`, set superblock operations, create the direct-mapping inode, mount JFS metadata, mount RW state, and instantiate the root inode.
- Implements freeze/unfreeze by quiescing transactions, shutting down or reinitializing the log, and updating superblock state.
- Implements sync, show-options, NFS export operations, fs-context operations, and file-system-type registration.
- Implements quota file read/write and quota on/off flag management when quota support is enabled.
- Starts and stops JFS I/O, lazy commit, and sync kernel threads at module init/exit.

Important interactions:
- Calls core JFS mount/unmount routines `jfs_mount()`, `jfs_mount_rw()`, `jfs_umount()`, and `jfs_umount_rw()`.
- Uses transaction, metapage, journal, bmap, imap, inode, xattr, ACL, and export subsystems.
- Installs `jfs_super_operations`, `jfs_export_operations`, `jfs_context_ops`, and `jfs_fs_type`.
- Uses `jfs_extendfs()` for remount-time resize.
- Uses quota VFS interfaces and direct block mapping through `jfs_get_block()` for quota file I/O.

Invariants and risks:
- `direct_inode` backs metadata I/O and must be torn down carefully on mount failure and unmount.
- Mount option parsing transfers ownership of loaded NLS tables between fs context and superblock.
- Quota files are made immutable/noatime while enabled and restored when disabled.
- Freeze failure after quiescing must resume transactions to avoid hangs.
- Module init failure unwinds in reverse order across slab, metapage, transaction manager, worker threads, procfs, and filesystem registration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/symlink.c -->
# File Research: sources/os/linux/linux/fs/jfs/symlink.c

JFS symlink inode operation tables.

Key responsibilities:
- Defines `jfs_fast_symlink_inode_operations` for inline symlink targets using `simple_get_link`.
- Defines `jfs_symlink_inode_operations` for page-cache-backed symlink targets using `page_get_link`.
- Shares JFS setattr and listxattr support across both symlink forms.

Important interactions:
- Selected by `jfs_symlink()` in `namei.c` depending on whether the symlink target fits in the inode inline data area.
- Uses `jfs_setattr()` and `jfs_listxattr()` from JFS inode/xattr subsystems.

Invariants and risks:
- Correct operation table selection depends on the inline target size threshold used during symlink creation.
- Long symlinks rely on normal page-cache address-space operations configured by the creator.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/xattr.c -->
# File Research: sources/os/linux/linux/fs/jfs/xattr.c

JFS extended-attribute service for on-disk EA lists, inline/extent storage, Linux xattr handlers, and security initialization.

Key responsibilities:
- Defines the JFS EA list format and `ea_buffer` state for inline, extent, newly allocated, and malloc-backed buffers.
- Maps unknown on-disk namespaces to Linux-visible `os2.` names while preserving known `system.`, `user.`, `security.`, and `trusted.` prefixes.
- Writes EA lists inline when possible through `ea_write_inline()`, otherwise allocates extent blocks and writes through metapages in `ea_write()`.
- Reads inline or extent-backed EA lists through `ea_read_inline()` and `ea_read()`.
- Loads and optionally expands an EA list through `ea_get()`, validating recorded list size against inode EA descriptors.
- Releases or commits EA buffers through `ea_release()` and `ea_put()`, updating transaction EA locks and freeing old quota blocks.
- Implements `__jfs_setxattr()`, including create/replace semantics, deletion by null value, list compaction, value-size checks, and list-size recalculation.
- Implements `__jfs_getxattr()` and `jfs_listxattr()`, including corrupted-entry bounds checks and trusted-name filtering.
- Exposes xattr handlers for `os2.`, `user.`, `security.`, and `trusted.` namespaces.
- Implements security xattr initialization under `CONFIG_JFS_SECURITY`.

Important interactions:
- Uses inode EA descriptor `JFS_IP(inode)->ea`, inline EA area, `INLINEEA`, and `xattr_sem`.
- Uses block allocator and quota helpers `dbAlloc()`, `dbFree()`, `dquot_alloc_block()`, and `dquot_free_block()`.
- Uses metapage I/O helpers `get_metapage()`, `read_metapage()`, `flush_metapage()`, `release_metapage()`, and `discard_metapage()`.
- Uses transaction helper `txEA()` to log replacement/removal of EA descriptors.
- Integrates with VFS xattr handler dispatch and LSM `security_inode_init_security()`.

Invariants and risks:
- EA list size is stored on disk and must match `DXD` size; mismatch is treated as corruption.
- EA value length is stored in 16 bits, so values at or above `USHRT_MAX` return `-E2BIG`.
- Buffer growth in `__jfs_setxattr()` may release and reacquire storage, so pointer state is rebuilt with a second pass.
- Newly allocated extent buffers must free both quota and blocks if validation or readback fails.
- Inline EA storage competes with xtree root expansion; `INLINEEA` flag transitions must remain consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernel_read_file.c -->
# File Research: sources/os/linux/linux/fs/kernel_read_file.c

Kernel helper implementation for reading regular-file contents into kernel memory with LSM mediation.

Key responsibilities:
- Implements `kernel_read_file()` for full or chunked reads into caller-provided or internally allocated buffers.
- Rejects invalid partial-read combinations, non-regular files, empty files, oversized files, and whole-file reads that cannot fit the provided buffer.
- Temporarily denies write access while reading.
- Calls `security_kernel_read_file()` before reading and `security_kernel_post_read_file()` after complete whole-file reads.
- Allocates with `vmalloc()` when the caller passes `*buf == NULL`, and frees on error.
- Exposes convenience wrappers for paths in the caller namespace, paths relative to init namespace root, and file descriptors.

Important interactions:
- Uses `kernel_read()`, `filp_open()`, `file_open_root()`, `get_fs_root()`, fd-class cleanup, and LSM hooks.
- Exported GPL symbols are used by kernel subsystems that load firmware, certificates, modules, policies, or other kernel-consumed file content.

Invariants and risks:
- `offset != 0` is allowed only for caller-managed partial reads with an existing buffer and `file_size` output.
- Whole-file reads require exact EOF position matching; short reads return `-EIO`.
- `deny_write_access()`/`allow_write_access()` must stay balanced on every exit path.
- File contents can change between chunked calls, so the interface documents chunked reads as discouraged.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernel_read_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/kernfs/Kconfig

Kconfig symbol definition for kernfs.

Key responsibilities:
- Defines `KERNFS` as a boolean config symbol.
- Defaults `KERNFS` to disabled.
- Documents that kernfs should be selected by users rather than directly enabled.

Important interactions:
- Selected by subsystems that need kernfs-backed virtual filesystems, such as sysfs/cgroup-style hierarchies.

Invariants and risks:
- Direct user selection is intentionally avoided; dependency owners must select it when needed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernfs/Makefile -->
# File Research: sources/os/linux/linux/fs/kernfs/Makefile

Build rules for kernfs.

Key responsibilities:
- Adds kernfs core objects to `obj-y`: `mount.o`, `inode.o`, `dir.o`, `file.o`, and `symlink.o`.

Important interactions:
- Builds kernfs as part of the core kernel object set when `fs/kernfs` is included by configuration.

Invariants and risks:
- Object list must remain synchronized with kernfs internal symbol dependencies.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/kernfs/dir.c -->
# File Research: sources/os/linux/linux/fs/kernfs/dir.c

kernfs directory and hierarchy implementation: node naming, path construction, sibling indexing, active-reference lifetime, creation, removal, rename, lookup, and readdir.

Key responsibilities:
- Provides name/path helpers: `kernfs_name()`, `kernfs_path_from_node()`, `pr_cont_kernfs_name()`, and `pr_cont_kernfs_path()`.
- Computes common ancestors and relative paths under RCU and rename locking.
- Hashes and compares sibling names with namespace IDs while avoiding kernel pointer exposure.
- Maintains parent child sets as rbtrees through `kernfs_link_sibling()` and `kernfs_unlink_sibling()`.
- Manages active references with `kernfs_get_active()`, `kernfs_put_active()`, and `kernfs_drain()`.
- Manages base references and RCU freeing with `kernfs_get()`, `kernfs_put()`, and `kernfs_free_rcu()`.
- Allocates nodes through `__kernfs_new_node()` and `kernfs_new_node()`, including IDR inode IDs, inherited gid/setgid behavior, and security initialization.
- Supports ID lookup through `kernfs_find_and_get_node_by_id()`.
- Adds nodes through `kernfs_add_one()` and supports namespace-aware find/walk helpers.
- Creates and destroys roots with `kernfs_create_root()` and `kernfs_destroy_root()`.
- Creates regular directories and permanently empty directories.
- Implements VFS dentry revalidation, lookup, mkdir/rmdir/rename syscall forwarding, directory inode operations, and directory file operations.
- Activates subtrees, hides/shows non-directory nodes, recursively removes subtrees, removes by name, supports self-removal from active operations, and renames/moves nodes.
- Implements stable-ish directory iteration using per-child hash values as `ctx->pos`.

Important interactions:
- Uses root-level locks: `kernfs_rwsem`, `kernfs_iattr_rwsem`, `kernfs_supers_rwsem`, `kernfs_rename_lock`, and `kernfs_idr_lock`.
- Integrates with kernfs inode, file, symlink, mount, xattr, mmap-drain, and syscall operation hooks from `kernfs-internal.h`.
- Calls LSM hook `security_kernfs_init_security()`.
- Uses VFS dentry/inode operations, fsnotify-relevant link clearing, and `dir_emit()` for readdir.
- Namespace filtering uses `struct ns_common::ns_id` instead of raw namespace pointers.

Invariants and risks:
- `kernfs_rwsem` is the central hierarchy mutation lock; many helpers assert it is held read or write.
- Nodes are invisible until active; removal deactivates nodes by adding `KN_DEACTIVATED_BIAS` and waits for active users to drain.
- `kernfs_drain()` temporarily drops hierarchy locks and must pin the target node before doing so.
- Parent pointers and names are RCU-protected; moving across parents also uses `kernfs_rename_lock`.
- `KERNFS_ROOT_INVARIANT_PARENT` forbids cross-parent rename and simplifies path access.
- Self-removal uses `KERNFS_SUICIDAL`/`KERNFS_SUICIDED` to arbitrate concurrent callers and avoid deadlocking on the caller’s own active reference.
- Directory iteration uses hashes as offsets, so hash uniqueness/reserved values and namespace filtering are important for correct traversal.
- Hidden nodes cannot be directories and are deactivated while hidden.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/kernfs/dir.c -->