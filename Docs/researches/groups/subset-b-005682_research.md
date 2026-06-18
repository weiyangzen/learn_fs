# subset-b-005682 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.c

## Purpose
`jfs_xtree.c` implements JFS extent allocation descriptor B+-trees. It maps logical file blocks to physical aggregate extents, inserts and extends extents, converts allocated-but-not-recorded ranges to recorded data, truncates file and metadata extents, initializes inline xtree roots, and exposes optional xtree statistics.

## Important APIs, types, and functions
The exported API is `xtLookup`, `xtInsert`, `xtExtend`, `xtUpdate`, `xtAppend`, `xtInitRoot`, `xtTruncate`, and `xtTruncate_pmap`. Internal structure centers on `xtpage_t`/`xtroot_t` pages from `jfs_xtree.h`, `xad_t` entries, `struct xtsplit` split descriptors, `struct btstack` search paths, metapages, and transaction locks. Core helpers are `xt_getpage`, `xtSearch`, `xtSplitUp`, `xtSplitPage`, and `xtSplitRoot`.

## Control flow
Lookups validate EOF unless bypassed, call `xtSearch`, then return the mapped physical address, flags, and contiguous length or the hole length up to the next extent. Search walks the root and internal pages by binary search, keeps a traversal stack, uses sequential access hints from `JFS_IP(ip)->btindex/btorder`, and pins the leaf containing the hit or insertion point. Inserts allocate data blocks when needed, mark new entries with `XAD_NEW`, and either shift a leaf or split leaf/internal/root pages upward. Append mode allocates bottom-up from a caller-specified contiguous region so bmap growth can consume the new area in order. `xtExtend` grows the preceding contiguous extent and inserts a continuation when `MAXXLEN` would be exceeded. `xtUpdate` replaces a subrange of a not-recorded extent, coalesces with neighboring recorded extents when logically and physically contiguous, and performs two- or three-way splits if the recorded range sits inside an existing extent.

Truncation is a backward bottom-up tree walk. `xtTruncate` frees or logs data and index extents depending on `COMMIT_PWMAP` versus `COMMIT_WMAP`, updates `nextindex`, collapses empty roots back to leaves, invalidates directory metapages on full directory truncation, and caps a transaction at `MAX_TRUNCATE_LEAVES` to avoid tlock/metapage deadlock. `xtTruncate_pmap` handles deleted-but-open files by freeing persistent-map resources in bounded transactions while leaving working-map access possible until final close.

## State and persistence behavior
Persistent state is the on-disk xtree encoded in inode inline roots and metapage index blocks. Entries store flags, logical offsets, physical addresses, and lengths. Runtime state includes pinned metapages, transaction locks (`tlckXTREE`, `tlckGROW`, `tlckNEW`, `tlckFREE`, `tlckTRUNCATE`), quota reservations, B+-tree search hints, and optional statistics. The code coordinates persistent map (`PMAP`) and working map (`WMAP`) semantics so unlink, truncate, and delayed close can commit in stages.

## Dependencies and integration points
It depends on JFS btree macros, metapages, block allocator `dbAlloc/dbFree/dbAllocBottomUp`, quota accounting, transaction manager `txLock/txFreeMap`, inode flags such as `COMMIT_Nolink`, and directory metadata invalidation helpers. Callers include file block mapping, symlink creation, bmap resize growth, unlink/rename zero-link cleanup, and generic truncate paths.

## Risks and test signals
High-risk areas are corrupt-page validation, split propagation while pins are transferred, quota rollback on split allocation failure, coalescing rules in `xtUpdate`, `MAXXLEN` overflow boundaries, root expansion/shrink interaction with inline EA space, and partial truncation requiring repeated transactions. Useful tests include sparse lookup holes, sequential and random extent insertion, root and internal splits, append-only bmap growth, conversion of not-recorded extents at left/middle/right positions, huge fragmented truncation, deleted-open-file cleanup, and fault injection for metapage/block allocation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.h

## Purpose
`jfs_xtree.h` defines the on-disk/in-memory layout and public interface for the JFS extent allocation descriptor tree used by regular files, long symlinks, special metadata files, and some directory truncation paths.

## Important APIs, types, and functions
The central type is `xad_t`, a 16-byte descriptor containing flags, a 40-bit logical offset, and a `pxd_t` location with length and physical address. Macros `XADoffset`, `XADaddress`, `XADlength`, `offsetXAD`, `addressXAD`, and `lengthXAD` encode/decode endian-sensitive fields. `struct xadlist` batches descriptors. Tree page layout is `struct xtheader`, `xtroot_t`, and `xtpage_t`, with slot constants `XTROOTINITSLOT_DIR`, `XTROOTINITSLOT`, `XTROOTMAXSLOT`, `XTPAGEMAXSLOT`, and `XTENTRYSTART`. Public functions declared here are `xtLookup`, `xtInitRoot`, `xtInsert`, `xtExtend`, `xtUpdate`, `xtTruncate`, `xtTruncate_pmap`, and `xtAppend`.

## Control flow
The header has no execution flow by itself. It establishes the contract consumed by `jfs_xtree.c` and by higher-level inode, directory, symlink, resize, and truncate code. Callers construct or inspect `xad_t` records through macros instead of directly composing split endian fields.

## State and persistence behavior
The structs mirror persistent JFS metadata. `xtroot_t` lives inline in the JFS inode; non-root `xtpage_t` instances live in metapages. `xad_t` flags distinguish newly allocated, extended, compressed, not-recorded, and copy-on-write extents. The maximum length `MAXXLEN` bounds a single extent at 24 bits, forcing callers to split longer mappings.

## Dependencies and integration points
It includes `jfs_btree.h` for common B+-tree definitions and uses `pxd_t` helpers for physical extent encoding. The declarations are the shared API between xtree management and the rest of JFS allocation, resize, symlink, truncate, and write paths.

## Risks and test signals
Risks are ABI/layout drift, endian conversion mistakes, direct field access bypassing macros, and single-extent length overflow. Test signals are on-disk metadata compatibility, fsck validation of xtree roots/pages, block mapping beyond 32-bit logical offsets, and builds across endian architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_xtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/namei.c -->
# sources/distributed-fs/ceph-client/fs/jfs/namei.c

## Purpose
`namei.c` implements JFS VFS namespace operations: create, mkdir, unlink, rmdir, link, symlink, rename, mknod, lookup, NFS filehandle recovery, directory file operations, and optional case-insensitive dentry operations for OS/2-compatible mounts.

## Important APIs, types, and functions
The VFS entry points are installed through `jfs_dir_inode_operations`, `jfs_dir_operations`, and `jfs_ci_dentry_operations`. Major functions include `jfs_create`, `jfs_mkdir`, `jfs_rmdir`, `jfs_unlink`, `jfs_link`, `jfs_symlink`, `jfs_rename`, `jfs_mknod`, `jfs_lookup`, `jfs_fh_to_dentry`, `jfs_fh_to_parent`, and `jfs_get_parent`. Resource cleanup is split through `commitZeroLink`, `jfs_free_zero_link`, and `free_ea_wmap`.

## Control flow
Creation paths initialize quota, convert dentries to JFS Unicode component names, allocate inodes before directory search to avoid blocking with dtree pages pinned, start a transaction, lock parent/child commit mutexes, initialize ACL/security xattrs, initialize an xtree or dtree root, insert a directory entry with `dtInsert`, set VFS operations, dirty inodes, and commit. Removal paths delete dtree entries, adjust link counts and timestamps, free EA/ACL extents, and commit delete metadata. For unlinked regular files and long symlinks, `commitZeroLink` starts persistent-map truncation; callers then loop with `xtTruncate_pmap` and synchronous commits until the bounded truncation completes.

`jfs_symlink` stores short targets in the inode inline area and long targets in a single xtree extent written through metapages. `jfs_rename` validates source and destination inumbers before the transaction, supports only `RENAME_NOREPLACE`, updates or inserts the destination, removes the old entry, adjusts directory link counts and `..` for cross-directory moves, and handles victim zero-link truncation like unlink. Lookup resolves `dtSearch` results to inodes via `jfs_iget` and returns `d_splice_alias`.

## State and persistence behavior
Persistent updates include directory dtree entries, inode allocation records, link counts, timestamps, inline symlink data, xtree-backed symlink data, EA/ACL descriptors, and deleted-file pmap truncation records. Runtime state includes transaction ids, commit mutex ordering, JFS component-name buffers, VFS dentries, IWRITE locks for unlink/rename victims, and cflags such as `COMMIT_Nolink`, `COMMIT_Freewmap`, and `COMMIT_Stale`.

## Dependencies and integration points
This file is the bridge between Linux VFS namespace methods and JFS internals: dtree search/insert/delete/modify, inode allocation and iget, transaction manager, xtree truncate/insert, ACL and LSM initialization, quota, exportfs, metapage cache invalidation, and casefold-style dentry hashing/comparison for OS/2 mounts.

## Risks and test signals
Risks include deadlocks from commit mutex ordering, pinned dtree pages across blocking allocation, partially completed zero-link truncation, directory `..` updates during rename, stale dentry behavior under case-insensitive mode, and error cleanup of newly allocated inodes with inline/extent EAs. Tests should cover create/mkdir/mknod failures at each stage, long and short symlinks, unlink of open large fragmented files, rename over files/directories and across parents, NFS filehandle generation checks, OS/2 case-insensitive lookup/revalidate, quota failures, and crash-recovery around delete/create transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/resize.c -->
# sources/distributed-fs/ceph-client/fs/jfs/resize.c

## Purpose
`resize.c` implements online JFS filesystem growth through `jfs_extendfs`. It expands the usable aggregate, relocates/reformats inline log and fsck workspaces as needed, grows the block allocation map, optionally extends inode allocation map structures, and commits the new superblock geometry.

## Important APIs, types, and functions
The sole exported function here is `jfs_extendfs(struct super_block *sb, s64 newLVSize, int newLogSize)`. It uses `jfs_sb_info`, bmap and imap special inodes, `struct jfs_log`, `struct bmap`, superblock buffers, `lmLogFormat/lmLogShutdown/lmLogInit`, `txQuiesce/txResume`, `dbExtendFS/dbFinalizeBmap/dbSync`, `diExtendFS/diSync`, `xtAppend`, and special inode read/write helpers. Constants define bmap page sizing, megabyte units, and `BLKTODMAPN`.

## Control flow
The function first rejects non-growth, invalid device size, and read-only filesystems. It computes new inline log size, fsck workspace size/address, and filesystem size, ensuring the filesystem does not shrink. If the new inline log will not overlap the old volume area, it may preformat the log before quiescing. The filesystem is quiesced, the direct inode size is refreshed, and inline-log mounts shut down the old log, mark the superblock `FM_EXTENDFS`, record transitional descriptors, format/initialize the new log, then proceed to map growth.

Map growth is incremental. It extends the existing bmap coverage with `dbExtendFS`, grows the bmap file if more dmap pages are needed, appends bmap file extents from the newly added region using `xtAppend`, commits forced transactions, and loops until the new map size is covered. It finalizes the bmap, extends/syncs the imap only if AG size changed, syncs the bmap control page, copies the primary bmap inode to the secondary copy, and finally updates primary and secondary superblocks with clean final descriptors, new AG size, log serial, and fsck workspace metadata before resuming transactions.

## State and persistence behavior
Persistent state includes superblock size/log/fsck descriptors, `FM_EXTENDFS` transition marker, bmap file xtree and control pages, secondary bmap inode, imap AG metadata, inline log contents, and fsck workspace descriptors. Runtime state includes quiesced transaction state, log activation state, temporary buffers, and whether the inline log was already formatted.

## Dependencies and integration points
The function is invoked from remount/reconfigure parsing in `super.c`. It integrates with block-device sizing, buffer-head I/O, JFS log manager, transaction manager, xtree append logic, block map and inode map managers, special inode persistence, quota-neutral metadata growth, and crash recovery expectations in logredo/fsck.

## Risks and test signals
Risks include geometry arithmetic overflow, new log/fsck overlap, failure while `FM_EXTENDFS` is set, partial bmap growth requiring recovery, AG-size transitions, secondary-superblock write mistakes, and handling devices that cannot report size. Tests should grow with and without inline logs, specify explicit and default log sizes, cross dmap/AG boundaries, inject failures during log formatting, bmap append, imap sync, and superblock writes, and verify fsck/logredo can complete interrupted resize states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/resize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/super.c -->
# sources/distributed-fs/ceph-client/fs/jfs/super.c

## Purpose
`super.c` is the JFS filesystem registration, mount, remount, superblock, quota, freeze, sync, and module lifecycle implementation. It converts fs_context parameters into `jfs_sb_info`, mounts block devices, starts/stops JFS service threads, and wires JFS into VFS superblock/export/quota operations.

## Important APIs, types, and functions
Key functions are `jfs_error`, `jfs_alloc_inode`, `jfs_free_inode`, `jfs_statfs`, `jfs_put_super`, `jfs_parse_param`, `jfs_reconfigure`, `jfs_fill_super`, `jfs_freeze`, `jfs_unfreeze`, `jfs_get_tree`, `jfs_sync_fs`, `jfs_show_options`, quota helpers, `jfs_init_fs_context`, `init_jfs_fs`, and `exit_jfs_fs`. Important state includes `jfs_inode_cachep`, `commit_threads`, `jfsCommitThread[]`, `jfsIOthread`, `jfsSyncThread`, `struct jfs_context`, `jfs_super_operations`, `jfs_export_operations`, and `jfs_fs_type`.

## Control flow
Mount option parsing handles integrity, charset, resize, error policy, quota flags, uid/gid/umask, and discard thresholds. `jfs_fill_super` allocates `jfs_sb_info`, transfers parsed options, validates discard support, creates the direct-mapping metadata inode, runs `jfs_mount`, optionally runs `jfs_mount_rw`, installs xattr/quota/export operations, loads the root inode, and sets max file size/time granularity. Reconfigure syncs the filesystem, updates options, optionally calls `jfs_extendfs`, transitions read-only to read-write or back through quota suspend/resume and mount/unmount-rw helpers, and remounts when the integrity mode changes. Freeze quiesces transactions, shuts down the log, and marks the superblock clean; unfreeze marks mounted, reinitializes the log, and resumes transactions.

Module initialization creates the JFS inode slab, initializes metapages and transaction manager, starts IO, lazy commit, and sync kthreads, initializes proc entries when configured, and registers the filesystem. Exit reverses these resources and waits for RCU inode frees before destroying the slab.

## State and persistence behavior
Persistent state managed here includes superblock clean/dirty/mounted flags, journal flush state, quota file data, and mount option effects persisted via inode flags for quota files. Runtime state includes `jfs_sb_info`, NLS tables, direct inode page cache, thread lifetimes, inode cache objects, fs_context private data, and error-policy bits controlling continue/remount-ro/panic behavior.

## Dependencies and integration points
It depends on VFS fs_context, block-device mounting, quota core, exportfs, xattr handlers, buffer_head/direct metadata mapping, JFS mount/log/metapage/transaction subsystems, POSIX ACL configuration, NLS, kthreads, procfs statistics, and the resize implementation.

## Risks and test signals
Risks include option lifetime for NLS tables, remount error paths that alter flags in the wrong order, read-only/read-write quota transitions, freeze failure leaving transactions blocked, service-thread startup cleanup, direct inode cache invalidation after fsck, and quota I/O bypassing page cache. Tests should cover all mount/remount options, resize-on-remount only, rw/ro transitions with quotas, discard unsupported devices, freeze/unfreeze under load, mount failure unwinding, statfs estimates, NFS export handles, and module init failure injection at each thread/subsystem boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/jfs/symlink.c

## Purpose
`symlink.c` defines the inode operation tables used by JFS symbolic links. It separates fast symlinks stored inline in the inode from normal symlinks whose content is page-cache backed through JFS address-space operations.

## Important APIs, types, and functions
The file exports `jfs_fast_symlink_inode_operations` and `jfs_symlink_inode_operations`. Fast symlinks use `.get_link = simple_get_link`; normal symlinks use `.get_link = page_get_link`. Both support `.setattr = jfs_setattr` and `.listxattr = jfs_listxattr`.

## Control flow
There is no function body here. `namei.c` selects the fast operation table when a symlink target fits in `IDATASIZE` and stores the pointer in `inode->i_link`; otherwise it selects the page-backed operation table after allocating an xtree extent and setting JFS address-space operations.

## State and persistence behavior
Fast symlink state persists in the JFS inode inline area. Long symlink state persists as file data mapped by the inode xtree. Both forms share inode metadata, mode, xattrs, and setattr behavior.

## Dependencies and integration points
It depends on Linux symlink helpers, `jfs_setattr`, `jfs_listxattr`, and the construction decisions in `jfs_symlink`. It is a narrow VFS integration point rather than a storage implementation.

## Risks and test signals
Risks are mismatches between chosen operations and where the target was stored, xattr listing on symlink inodes, and setattr behavior on inline versus page-backed symlinks. Tests should create targets just below, at, and above the inline threshold, read links after remount, list xattrs on symlinks, and verify truncation/unlink cleanup of long symlink extents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/xattr.c -->
# sources/distributed-fs/ceph-client/fs/jfs/xattr.c

## Purpose
`xattr.c` implements JFS extended attributes and security-xattr initialization. It reads, validates, lists, creates, replaces, removes, and persists EA lists either inline in the inode or in allocated extents, while translating legacy OS/2 attribute names into Linux xattr namespaces.

## Important APIs, types, and functions
The internal buffer descriptor is `struct ea_buffer` with flags `EA_INLINE`, `EA_EXTENT`, `EA_NEW`, and `EA_MALLOC`. Storage helpers include `ea_write_inline`, `ea_write`, `ea_read_inline`, `ea_read`, `ea_get`, `ea_release`, and `ea_put`. Public JFS-facing APIs are `__jfs_setxattr`, `__jfs_getxattr`, `jfs_listxattr`, `jfs_xattr_handlers`, and, under security config, `jfs_init_security`. Namespace helpers are `is_known_namespace`, `name_size`, `copy_name`, and the OS/2-specific get/set handlers.

## Control flow
Reads acquire `xattr_sem`, call `ea_get`, validate EA-list size, scan entries with `FIRST_EA/NEXT_EA/END_EALIST`, detect malformed bounds, and return value size or data. Listing first computes filtered output size, hides `trusted.*` from callers without `CAP_SYS_ADMIN`, prefixes unknown on-disk names with `os2.`, then copies names if the caller supplied a buffer. Sets start a transaction in the VFS wrapper, lock `commit_mutex`, acquire `xattr_sem`, load or allocate a large enough EA buffer, remove an existing entry if replacing, append the new entry if a value is supplied, validate size accounting and `USHRT_MAX` value limits, update the list size, and commit through `ea_put`.

`ea_put` chooses inline storage, preallocated extent storage, or fresh extent writing, invalidates and frees old extent blocks through transaction EA map locks, updates `JFS_IP(inode)->ea`, adjusts inline-space availability, and refunds quota for old blocks. Security initialization iterates LSM-provided xattrs and writes them under the `security.` prefix inside the creating transaction.

## State and persistence behavior
Persistent EA state is a `jfs_ea_list` referenced by the inode `dxd_t` EA descriptor, either `DXD_INLINE` in `i_inline_ea` or `DXD_EXTENT` in allocated blocks. Runtime state includes the xattr rwsem, transaction locks, metapage buffers, kmalloc scratch buffers for large lists, quota reservations, and inline EA availability (`INLINEEA` mode bit). Unknown non-Linux-prefixed on-disk names are preserved but exposed under `os2.`.

## Dependencies and integration points
The implementation depends on VFS xattr handlers, POSIX ACL xattr formats, LSM security initialization, JFS block allocator, quota, transaction EA logging (`txEA`), metapage I/O, inode inline storage, and namespace constants from Linux xattr headers. `super.c` installs `jfs_xattr_handlers`; `namei.c` calls security initialization during inode creation and cleanup paths free EA extents.

## Risks and test signals
Risks include corrupt EA-list size causing overreads, large allocation failures, quota rollback on new extent allocation, inline-area ownership conflicts with xtree root expansion, value length overflow, namespace translation surprises, and synchronous metapage write errors that are hard to propagate. Tests should cover inline-to-extent and extent-to-inline transitions, create/replace/remove flags, zero-length values, `USHRT_MAX` boundary rejection, malformed EA images, permission filtering for trusted names, OS/2 unknown-prefix round trips, security xattr initialization, and fault injection for dbAlloc/metapage/quota failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernel_read_file.c -->
# sources/distributed-fs/ceph-client/fs/kernel_read_file.c

## Purpose
`kernel_read_file.c` provides generic helpers for reading regular files into kernel memory with LSM mediation. It supports direct `struct file` callers plus convenience wrappers for path, init namespace path, and file descriptor inputs.

## Important APIs, types, and functions
The exported functions are `kernel_read_file`, `kernel_read_file_from_path`, `kernel_read_file_from_path_initns`, and `kernel_read_file_from_fd`. Important dependencies are `kernel_read`, `deny_write_access/allow_write_access`, `security_kernel_read_file`, `security_kernel_post_read_file`, `vmalloc/vfree`, `filp_open`, `file_open_root`, `get_fs_root`, and the fd cleanup `CLASS(fd, f)` helper.

## Control flow
`kernel_read_file` rejects unsupported partial-read forms, non-regular files, write-access denial failures, empty files, files larger than `SSIZE_MAX`, and whole-file reads that cannot fit in the caller buffer. It asks LSMs whether the read may proceed, reports full file size if requested, allocates a vmalloc buffer when `*buf` is NULL, loops with `kernel_read` until the requested buffer size or EOF, and for whole-file reads verifies the final position reached `i_size` before calling post-read LSM hooks. On errors after internal allocation it frees the buffer and nulls the caller pointer. All exits release write denial.

Path wrappers validate nonempty paths, open the file, call the core helper, and drop the file. The init namespace wrapper obtains `init_task`'s root under task lock and opens relative to that root. The fd wrapper validates a readable fd and delegates.

## State and persistence behavior
The function has no persistent storage. Runtime side effects are temporary write denial on the file, optional vmalloc ownership transfer to the caller, LSM audit/measurement hooks, and file position via the local `pos` variable rather than changing `file->f_pos`.

## Dependencies and integration points
It is used by kernel subsystems that load firmware-like blobs, certificates, policies, or module-adjacent data and need a consistent LSM inspection point. The `enum kernel_read_file_id` classifies the read for security policy.

## Risks and test signals
Risks include stale `i_size` if files change during partial reads, pointer arithmetic on `void *` relying on kernel compiler behavior, whole-file post-read checks skipped for chunked reads, and cleanup ownership when callers pass preallocated buffers. Tests should cover LSM allow/deny and post-read denial, allocated versus caller buffers, partial offset reads, too-small buffers, empty/non-regular/huge files, fd mode validation, init namespace path resolution, and concurrent modification during reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernel_read_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/kernfs/Kconfig

## Purpose
This Kconfig fragment declares `CONFIG_KERNFS`, the internal pseudo-filesystem infrastructure used by sysfs-like kernel filesystems.

## Important APIs, types, and functions
It defines one boolean symbol, `KERNFS`, with default `n`. There are no functions or types in this file.

## Control flow
`KERNFS` is intended to be selected by users rather than manually enabled. Build inclusion is controlled by other Kconfig entries that depend on kernfs services.

## State and persistence behavior
There is no runtime state or persistent data. The symbol controls whether kernfs objects from this directory are compiled into the kernel.

## Dependencies and integration points
Subsystems such as sysfs or cgroupfs-style users select this symbol to receive the kernfs object model, mount support, inode/file/dir/symlink operations, and namespace-aware directory infrastructure.

## Risks and test signals
Risks are build configuration mistakes: forgetting to select `KERNFS` from a user, or exposing it as a user-facing option unintentionally. Test signals are allyesconfig/allmodconfig builds, minimal configs containing sysfs/cgroup users, and dependency audits ensuring every kernfs caller selects the symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/kernfs/Makefile

## Purpose
This Makefile defines the object list for the kernfs pseudo-filesystem implementation.

## Important APIs, types, and functions
It builds `mount.o`, `inode.o`, `dir.o`, `file.o`, and `symlink.o` into built-in kernel objects through `obj-y`. There are no code-level APIs in this file.

## Control flow
When `CONFIG_KERNFS` is selected and this directory is descended into by kbuild, all listed objects are compiled as built-in components rather than separate modules.

## State and persistence behavior
The Makefile has no runtime state. It determines which translation units provide kernfs mount, inode, directory, regular file, and symlink behavior.

## Dependencies and integration points
The object list must stay aligned with exported kernfs symbols and internal headers. `dir.o` supplies namespace tree operations, `mount.o` handles superblocks/mounts, `inode.o` bridges to VFS inodes/attributes, `file.o` implements file operations, and `symlink.o` implements links.

## Risks and test signals
Risks are missing objects causing unresolved symbols or dead code assumptions about modularity. Test signals are clean kernfs-user builds, link tests for sysfs/cgroup configurations, and dependency changes that add or remove kernfs translation units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/dir.c -->
# sources/distributed-fs/ceph-client/fs/kernfs/dir.c

## Purpose
`kernfs/dir.c` implements kernfs directory and tree management: node naming/path construction, reference and active-reference lifetime, sibling rbtree indexing, root and directory creation, lookup/readdir VFS operations, activation/hiding/removal, self-removal, namespace-aware find/walk, and rename/move.

## Important APIs, types, and functions
Major exported functions include `kernfs_name`, `kernfs_path_from_node`, `pr_cont_kernfs_name`, `pr_cont_kernfs_path`, `kernfs_get_parent`, `kernfs_get_active`, `kernfs_put_active`, `kernfs_get`, `kernfs_put`, `kernfs_node_from_dentry`, `kernfs_new_node`, `kernfs_find_and_get_node_by_id`, `kernfs_add_one`, `kernfs_find_and_get_ns`, `kernfs_walk_and_get_ns`, `kernfs_create_root`, `kernfs_destroy_root`, `kernfs_root_to_node`, `kernfs_create_dir_ns`, `kernfs_create_empty_dir`, `kernfs_activate`, `kernfs_show`, `kernfs_remove`, `kernfs_break_active_protection`, `kernfs_unbreak_active_protection`, `kernfs_remove_self`, `kernfs_remove_by_name_ns`, and `kernfs_rename_ns`. VFS tables are `kernfs_dops`, `kernfs_dir_iops`, and `kernfs_dir_fops`.

## Control flow
Names and paths are resolved under RCU and, when parent pointers are mutable, `kernfs_rename_lock`. Sibling lookup uses a per-directory red-black tree ordered by a 31-bit hash, namespace id, and name. New nodes allocate an RCU-freed name, a slab node, a cyclic idr id with generation high bits, optional iattrs/security xattrs, and a parent reference; `kernfs_add_one` validates namespace requirements and active parent directory state, links the node, updates parent revision/timestamps, and activates it unless the root requested deactivated creation.

Active references gate kernfs file and syscall operations. `kernfs_get_active` fails once a node is deactivated; removal marks a subtree removing, biases active counts negative, drains active users and open files, clears VFS inode link counts for mounted supers, unlinks siblings, and drops base references in postorder. `kernfs_remove_self` breaks the caller's own active protection to avoid self-deadlock, arbitrates concurrent self-removers with `KERNFS_SUICIDAL/SUICIDED`, and waits for the winning operation to drain. Rename validates active source/target, invariant-parent roots, and duplicate destination, unlinks from the old rbtree, updates parent/name/ns under the rename lock when needed, recomputes hash, and relinks.

VFS lookup searches by namespace and instantiates positive or negative dentries with revision tracking. Dentry revalidation drops stale negatives when parent revisions changed and invalidates positives whose node was deactivated, moved, renamed, or namespace-mismatched. Readdir emits dots, then iterates active children in hash order, retaining the current node in `file->private_data` for seek continuity.

## State and persistence behavior
Kernfs state is in-memory only. Persistent-looking identifiers are runtime inode ids from `root->ino_idr` plus generation bits. Important mutable state includes parent RCU pointers, names, namespace tags, rb nodes, active and base refcounts, flags (`KERNFS_ACTIVATED`, `HIDDEN`, `REMOVING`, `EMPTY_DIR`, `SUICIDAL`, `SUICIDED`), directory child trees, subdir counts, revision counters for dentry invalidation, mounted-super lists, and optional inode attributes/xattrs. RCU frees names/nodes after final `kernfs_put`.

## Dependencies and integration points
This file depends on VFS inode/dentry/file operation hooks, RCU, idr, red-black trees, rwsems/spinlocks, namespace ids, LSM kernfs security initialization, kernfs internal inode/file/symlink helpers, fsnotify-facing inode nlink clearing, and caller-provided `kernfs_syscall_ops` for mkdir/rmdir/rename. It is core infrastructure for sysfs-like and cgroup-like filesystems.

## Risks and test signals
Risks include active-reference leaks or underflows, removal racing lookup/readdir/rename, namespace hash collisions and ordering errors, stale negative dentries after directory changes, self-removal waiting bugs, RCU name lifetime mistakes, invariant-parent violations, and deadlocks involving `kernfs_rwsem`, `kernfs_supers_rwsem`, `kernfs_iattr_rwsem`, rename lock, and open-file draining. Tests should exercise concurrent create/remove/lookup/readdir, namespace-filtered directories, rename across parents and no-op renames, hidden/show activation, deactivated-root batch creation, self-deleting files with concurrent writers, id lookup with generation mismatch, dentry revalidation after move/remove, and fault injection for idr/slab/security allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernfs/dir.c -->
