# Group Research: group_1017_linux_stable_sources_os_linux_linux_stable_fs_minix_inode_c_sources_e95b8ad3e867

Scope: learn_fs subset A, source tree `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/minix/inode.c

## Purpose

Implements MINIX filesystem superblock setup, inode lifecycle, inode disk encoding/decoding, page-cache address-space operations, and module registration. It is the central mount/inode glue for MINIX V1, V2, and V3 formats.

## Main Entry Points

- `minix_fill_super()`: reads and validates the on-disk superblock, loads inode/zone bitmaps, detects V1/V2/V3 layout, and creates the root dentry.
- `minix_reconfigure()`: handles read-only/read-write remount state transitions.
- `minix_iget()`: loads an inode through the V1 or V2/V3 raw inode formats.
- `minix_write_inode()`: writes V1 or V2/V3 inode metadata back to disk.
- `minix_set_inode()`: assigns file, directory, symlink, or special-file operation tables.
- `minix_get_block()`, `minix_writepages()`, `minix_read_folio()`, `minix_write_begin()`: connect MINIX block mapping to generic buffered I/O.
- `minix_truncate()`: dispatches truncation to the version-specific indirect-tree implementation.
- `init_minix_fs()` / `exit_minix_fs()`: create the inode cache and register/unregister the filesystem type.

## Control Flow And State

Mounting allocates `minix_sb_info`, forces the initial MINIX block size, reads block 1, detects the magic/version, sets name length and directory entry size, validates zone and bitmap geometry, reads imap/zmap blocks, marks bitmap bit zero allocated, and then reads `MINIX_ROOT_INO`. Read-write mounts clear the valid-state flag for V1/V2 filesystems and restore it on unmount/remount read-only. V3 has different state handling and supports a superblock-provided block size.

Inode loading branches by `INODE_VERSION()`. V1 inodes use a single timestamp, 16-bit zones, and old device encoding; V2/V3 use separate atime/mtime/ctime and 32-bit zones. Writeback mirrors those layouts and synchronously flushes the raw inode buffer for `WB_SYNC_ALL`.

Address-space operations use the generic block helpers plus MINIX `get_block`, and failed extending writes truncate page cache and filesystem blocks back to `i_size`. Eviction truncates unlinked inodes, synchronizes metadata buffer heads for linked inodes, invalidates tracked metadata buffers, clears the VFS inode, and frees the on-disk inode if link count reached zero.

## Dependencies

Depends on `minix.h`, MINIX bitmap/block/inode allocation helpers, the V1/V2 indirect-tree wrappers, Linux buffer-head and mpage helpers, fs_context block-device mounting, generic inode/page-cache helpers, and the VFS file/directory operation tables declared elsewhere in the MINIX driver.

## Risks

Correctness is dominated by legacy on-disk format handling: magic detection, V1 maximum size limits, bitmap block sufficiency, old device encoding, and V1/V2/V3 state differences. The mount path has many partial-allocation exits and must release bitmap buffers and superblock buffers in the right order. Metadata consistency depends on `mapping_metadata_bhs` tracking indirect blocks dirtied by truncation/allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/itree_common.c -->
# File Research: sources/os/linux/linux-stable/fs/minix/itree_common.c

## Purpose

Provides the shared indirect-block tree implementation included by MINIX V1 and V2/V3 block mapping files. It handles logical-to-physical block lookup, branch allocation, atomic splice into inode metadata, truncation, and block-count estimation.

## Main Entry Points

- `get_block()`: maps a logical block to a disk block, optionally allocating missing blocks.
- `truncate()`: frees blocks beyond `inode->i_size`.
- `nblocks()`: estimates total data plus metadata blocks for stat accounting.
- `get_branch()`: walks direct/indirect pointers and detects races.
- `alloc_branch()`: allocates and initializes a missing chain of indirect/data blocks.
- `splice_branch()`: installs a newly allocated branch after verifying the parent chain.
- `find_shared()` / `free_branches()` / `free_data()`: locate and free truncation targets.

## Control Flow And State

`get_block()` computes version-specific offsets through `block_to_path()`, walks the pointer chain with `get_branch()`, and either maps the existing block or allocates the missing suffix. Allocation builds indirect buffers bottom-up, zeroes them, records metadata buffers through `mmb_mark_buffer_dirty()`, and frees all partial work on failure. `splice_branch()` takes `pointers_lock`, verifies the chain has not changed, installs the new pointer, updates ctime, and marks the inode or indirect block dirty. Races with truncate return `-EAGAIN` and restart lookup.

Truncation converts file size to the first block to keep, truncates partial page data, finds any shared indirect branch that must be split, clears and frees the right-hand side, then frees whole remaining indirect subtrees from the inode’s direct indirect pointers. It updates mtime/ctime and marks modified metadata dirty.

## Dependencies

This file is a template and relies on the including file to define `DEPTH`, `DIRECT`, `block_t`, `block_to_cpu()`, `cpu_to_block()`, `i_data()`, and `block_to_path()`. It calls MINIX block allocator/free routines, buffer-head I/O, inode dirtying, `block_truncate_page()`, and `mapping_metadata_bhs` helpers.

## Risks

The code is concurrency-sensitive: pointer-chain verification, truncate races, and branch splicing all rely on `pointers_lock` and retry behavior. Failed branch allocation must free both newly allocated disk blocks and buffer heads. Lost metadata dirtying would leak or orphan indirect blocks after crash or writeback.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/itree_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/itree_v1.c -->
# File Research: sources/os/linux/linux-stable/fs/minix/itree_v1.c

## Purpose

Specializes `itree_common.c` for MINIX V1 block pointers.

## Main Entry Points

- `V1_minix_get_block()`: maps or allocates a V1 logical block.
- `V1_minix_truncate()`: truncates V1 block trees.
- `V1_minix_blocks()`: computes V1 block usage for stat output.
- `block_to_path()`: converts a logical block into V1 direct/single/double-indirect offsets.

## Control Flow And State

V1 uses seven direct pointers, one single-indirect pointer, and one double-indirect pointer with 16-bit block numbers. `block_to_path()` rejects negative blocks and blocks beyond `s_maxbytes`, maps blocks below 7 directly, the next 512 through the single-indirect slot, and the rest through the double-indirect slot.

## Dependencies

Includes `minix.h`, buffer-head support, and the shared indirect-tree template. Uses `minix_i(inode)->u.i1_data` as the raw in-memory pointer array and assumes V1 block numbers are host-order `u16`.

## Risks

The 16-bit block pointer format and fixed 1 KiB `BLOCK_SIZE` limits make overflow and maximum-size checks important. The common code trusts `block_to_path()` to reject unrepresentable logical blocks before allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/itree_v1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/itree_v2.c -->
# File Research: sources/os/linux/linux-stable/fs/minix/itree_v2.c

## Purpose

Specializes `itree_common.c` for MINIX V2/V3 block pointers.

## Main Entry Points

- `V2_minix_get_block()`: maps or allocates a V2/V3 logical block.
- `V2_minix_truncate()`: truncates V2/V3 block trees.
- `V2_minix_blocks()`: computes V2/V3 block usage for stat output.
- `block_to_path()`: converts logical blocks into direct/single/double/triple-indirect offsets.

## Control Flow And State

V2/V3 use seven direct pointers plus single, double, and triple indirect pointers with 32-bit block numbers. The indirect fanout is derived from the mounted block size with `INDIRCOUNT(sb)`. `block_to_path()` rejects negative and beyond-maximum offsets, then fills offsets for the correct tree depth.

## Dependencies

Includes `minix.h`, buffer-head support, and `itree_common.c`. Uses `minix_i(inode)->u.i2_data` and host-order `u32` block numbers.

## Risks

The triple-indirect path uses larger arithmetic and block-size-dependent fanout, so maximum-size validation and offset calculations must remain consistent with superblock block size. As with V1, the shared allocator assumes invalid logical blocks never reach it.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/itree_v2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/minix.h -->
# File Research: sources/os/linux/linux-stable/fs/minix/minix.h

## Purpose

Defines MINIX filesystem private in-memory structures, version constants, internal helper declarations, operation-table declarations, and bitmap-endianness helpers.

## API Surface

- `struct minix_inode_info`: stores V1/V2 pointer arrays, metadata buffer tracking, and embedded VFS inode.
- `struct minix_sb_info`: stores inode/zone counts, bitmap sizes, first data zone, directory sizing, bitmap buffers, raw superblock buffer, mount state, and version.
- Declares inode/block allocation, raw inode access, directory operations, stat/truncate/block-map helpers, fsync, and operation tables.
- `minix_sb()` and `minix_i()` convert generic VFS objects to MINIX-private objects.
- `minix_blocks_needed()` computes bitmap block requirements.
- Bitmap macros select native-endian, big-endian 16-bit indexed, or little-endian bit operations.

## Dependencies

Includes Linux VFS, pagemap, and public MINIX on-disk format definitions. The endian behavior depends on `CONFIG_MINIX_FS_NATIVE_ENDIAN` and `CONFIG_MINIX_FS_BIG_ENDIAN_16BIT_INDEXED`.

## Risks

This header is the contract across all MINIX source files. A mismatch in bitmap bit numbering or inode private layout would corrupt allocation state. The compile-time error for incompatible endian settings protects a known broken configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/minix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/minix/namei.c

## Purpose

Implements MINIX directory inode operations for lookup, create, mknod, tmpfile, symlink, hardlink, mkdir, unlink, rmdir, and rename.

## Main Entry Points

- `minix_lookup()`: resolves a directory entry name to an inode.
- `minix_create()` / `minix_mknod()` / `minix_tmpfile()`: create regular, special, or unnamed temporary files.
- `minix_symlink()`: creates a page-cache-backed symlink.
- `minix_link()`: creates a hardlink to an existing inode.
- `minix_mkdir()` / `minix_rmdir()`: create and remove directories with link-count updates.
- `minix_unlink()`: removes a non-directory entry.
- `minix_rename()`: renames or replaces entries, including directory `..` updates.
- `minix_dir_inode_operations`: exports the operation table to VFS.

## Control Flow And State

Creation allocates a new MINIX inode, assigns inode operations with `minix_set_inode()`, marks it dirty, and inserts the directory entry through `minix_add_link()`. `add_nondir()` centralizes the instantiate-or-drop path and decrements the new inode link count on insertion failure.

`mkdir()` increments the parent link count, initializes the child as a directory, increments the child link count for `.` and `..`, fills the empty directory, and links it into the parent. Failure unwinds both child and parent link counts. `unlink()` finds the directory entry, deletes it, updates the victim ctime from the directory, and decrements its link count. `rmdir()` checks parent link count sanity, verifies the target is empty, calls unlink, and decrements parent and child directory counts.

`rename()` supports only `RENAME_NOREPLACE`. It finds the old entry and, for directory renames, the child `..` entry. If replacing an existing target it checks emptiness and link-count sanity, rewrites the target entry to the old inode, and drops the replaced inode’s link count. If moving into a new name it adds a new link and adjusts the new parent count for directories. It then deletes the old entry and updates `..` when a directory crosses parents.

## Dependencies

Depends on directory-entry helpers declared in `minix.h`, MINIX inode allocation, page symlink helpers, VFS dentry aliasing and instantiation, folio kmap release helpers, and generic inode link-count helpers.

## Risks

Directory link-count consistency is the main risk. The code explicitly detects corrupted zero or too-low link counts in unlink/rmdir/rename. Rename has many partial states involving old entry, new entry, and directory `..`; failures must release folios and avoid leaking link-count changes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/minix/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/mnt_idmapping.c -->
# File Research: sources/os/linux/linux-stable/fs/mnt_idmapping.c

## Purpose

Implements mount idmapping objects and conversions between kernel inode IDs, VFS IDs exposed through a mount, and filesystem user namespace IDs.

## Main Entry Points

- `make_vfsuid()` / `make_vfsgid()`: map filesystem `kuid_t`/`kgid_t` values into mount-relative `vfsuid_t`/`vfsgid_t`.
- `from_vfsuid()` / `from_vfsgid()`: map mount-relative IDs back into filesystem namespace IDs for inode writes.
- `vfsgid_in_group_p()`: checks group membership using VFS GIDs.
- `alloc_mnt_idmap()`: allocates and copies a user namespace UID/GID map for a mount.
- `mnt_idmap_get()` / `mnt_idmap_put()`: refcount mount idmaps.
- `statmount_mnt_idmap()`: emits mount idmap extents for statmount-style reporting.

## Control Flow And State

The file defines two global singleton idmaps: `nop_mnt_idmap`, an identity mapping, and `invalid_mnt_idmap`, a mapping that converts everything to invalid IDs. Fast paths return immediately for these singletons. Nontrivial mapping first translates through the filesystem user namespace when needed, then maps down or up through the mount’s copied UID/GID maps.

`alloc_mnt_idmap()` copies both UID and GID maps from a user namespace. Small maps are copied inline; large maps duplicate forward and reverse extent arrays. Refcount operations skip the two singletons. `statmount_mnt_idmap()` reports extents relative to the current caller’s user namespace and skips ranges that cannot be resolved for that caller.

## Dependencies

Depends on Linux user namespace UID/GID map internals, credential/group helpers, seq_file output, refcounting, and VFS ID wrapper types from mount idmapping headers.

## Risks

Mapping correctness depends on preserving uid/gid extent ordering and copying immutable namespace maps with the right memory barriers. Invalid or unmapped IDs intentionally propagate as invalid VFS/kernel IDs, and callers must handle those before writing inode ownership. Large map allocation has two arrays that must be freed consistently.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/mnt_idmapping.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/mount.h -->
# File Research: sources/os/linux/linux-stable/fs/mount.h

## Purpose

Defines internal VFS mount and mount-namespace structures plus helper routines shared by mount and pathname-walking code.

## API Surface

- `struct mnt_namespace`: namespace root, mount rbtree, user namespace, poll/event state, fsnotify marks, mount counts, and anonymous namespace state.
- `struct mount`: internal wrapper around `vfsmount`, including parent/child topology, namespace membership, propagation lists, per-superblock linkage, refcounts/writer counts, mountpoint state, fsnotify state, IDs, pins, and overmount pointer.
- `struct mountpoint`: hash/list node for dentries used as mountpoints.
- Helpers include `real_mount()`, `mnt_has_parent()`, `is_mounted()`, `detach_mounts()`, mount lock guards, namespace rbtree helpers, fsnotify queueing, `topmost_overmount()`, and write-hold flag manipulation.

## Control Flow And State

Mount namespaces keep mounts in an rbtree with cached first/last nodes and maintain passive references separate from active mount pins. Mounts maintain both tree topology and namespace membership, plus shared/slave propagation lists. The header exposes mount traversal and lookup hooks used by `fs/namei.c` when crossing mountpoints or following `..`.

The per-superblock previous pointer steals the low bit for `WRITE_HOLD`, with helpers to test, set, and clear that state. Several helpers are intended for use under `namespace_sem`, `mount_lock`, RCU, or fsnotify-specific conditions.

## Dependencies

Depends on Linux mount, namespace, seq_file, poll, fs_pin, fsnotify, rbtree, hlist/list, seqlock, and internal VFS mount functions implemented elsewhere.

## Risks

This is private infrastructure with tight locking and lifetime rules. Misusing RCU-visible namespace pointers, rbtree membership checks, or the low-bit write-hold encoding can corrupt mount topology or writer accounting. Path walking depends on these helpers accurately distinguishing detached, internal, mounted, and anonymous namespace states.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/mpage.c -->
# File Research: sources/os/linux/linux-stable/fs/mpage.c

## Purpose

Provides generic multipage BIO construction for block-mapped filesystems using a `get_block_t` mapper. It batches page-cache reads and writeback into contiguous BIOs while falling back to buffer-head paths for complex mappings.

## Main Entry Points

- `mpage_readahead()`: maps readahead folios and submits read BIOs.
- `mpage_read_folio()`: reads a single folio using the same BIO-building logic.
- `__mpage_writepages()`: iterates dirty folios and writes them through `mpage_write_folio()`.
- `do_mpage_readpage()`: core read mapper/BIO builder.
- `mpage_write_folio()`: core write mapper/BIO builder.
- `mpage_read_end_io()` / `mpage_write_end_io()`: complete folio read/writeback after BIO completion.

## Control Flow And State

Read path refuses folios that already have buffers, maps logical blocks with the filesystem `get_block`, accepts only contiguous disk blocks and holes at the end of a folio, zeroes holes, and chains adjacent folios into one BIO. If it sees non-contiguous blocks, a hole followed by data, an uptodate mapped buffer supplied by the filesystem, allocation failure, or other complexity, it submits any pending BIO and falls back to `block_read_full_folio()`.

Write path either consumes existing cleanly mapped dirty buffers or maps an uptodate bufferless folio by calling `get_block(..., create=1)`. It skips whole folios beyond EOF, zeroes bytes beyond `i_size` in a partial EOF folio, builds contiguous write BIOs, marks buffers clean only after the folio is accepted into the BIO, starts writeback, and submits on boundaries or partial mappings. Complex cases fall back to `block_write_full_folio()`.

## Dependencies

Depends on Linux folios, buffer heads, BIO/block-device APIs, writeback control, backing device accounting, `get_block_t` filesystem callbacks, and generic block read/write fallback helpers.

## Risks

The fast path is intentionally narrow. Incorrectly accepting non-contiguous or partially dirty mappings would corrupt I/O completion accounting, while cleaning buffers before BIO acceptance would lose dirty data on failure. EOF zeroing is repeated during writeback because mmap can dirty bytes beyond file size. Readahead uses no-retry allocation and must degrade cleanly when BIO allocation fails.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/mpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/namei.c

## Purpose

Implements Linux VFS pathname resolution, filename import, permission checks, dcache lookup, symlink following, mount traversal, open/create handling, namespace mutation operations, and generic symlink page-cache helpers.

## Main Entry Points

- Filename handling: `filename_init()`, `getname_flags()`, `getname_uflags()`, `getname_kernel()`, `putname()`, delayed filename helpers.
- Permissions: `generic_permission()`, `inode_permission()`, `may_linkat()`, `may_create_dentry()`, `may_delete_dentry()`.
- Path lookup: `filename_lookup()`, `kern_path()`, `vfs_path_lookup()`, `vfs_path_parent_lookup()`, `user_path_at()`.
- Single-component lookup helpers: `lookup_one*()`, `lookup_noperm*()`, `try_lookup_noperm()`.
- Open path: `do_file_open()`, `do_file_open_root()`, `path_openat()`, `vfs_tmpfile()`, `kernel_tmpfile_open()`, `dentry_create()`.
- Creation and mutation: `vfs_create()`, `vfs_mknod()`, `vfs_mkdir()`, `vfs_rmdir()`, `vfs_unlink()`, `vfs_symlink()`, `vfs_link()`, `vfs_rename()`.
- Syscall implementations: `mknod`, `mkdir`, `rmdir`, `unlink`, `symlink`, `link`, `rename`.
- Symlink helpers: `vfs_readlink()`, `vfs_get_link()`, `page_get_link()`, `page_readlink()`, `page_symlink()`.

## Control Flow And State

Path walking is centered on `struct nameidata`. `path_init()` chooses the starting path from root, cwd, dirfd, or a supplied root and can enter RCU-walk. `link_path_walk()` iterates components, checks directory search permission, hashes each component, handles `.`, `..`, trailing slashes, nested symlinks, and transitions through `walk_component()`. Lookup first tries lockless dcache lookup and revalidation; slow lookup allocates or waits on in-lookup dentries under the parent inode lock.

RCU-walk falls back to ref-walk through `try_to_unlazy()` or `try_to_unlazy_next()` when blocking work, unstable seqcounts, managed dentries, or filesystem revalidation require references. Mount traversal handles mountpoint crossing, automounts, `LOOKUP_NO_XDEV`, `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, scoped lookup escape checks, and `..` across mount roots. Symlink following uses a bounded stack, enforces `MAXSYMLINKS`, handles absolute symlink targets by jumping to root, and supports magic-link jumps through `nd_jump_link()`.

Open handling uses `open_last_lookups()` and `lookup_open()` to resolve the final component, optionally create it, and use filesystem `atomic_open()` when available. `do_open()` completes the walk, enforces `O_EXCL`, `O_DIRECTORY`, sticky-directory protections, `may_open()`, LSM post-open hooks, and `O_TRUNC`.

Filesystem mutation paths first resolve the parent, obtain mount write access, lock parent directories through `start_dirop()` or rename-specific locking, run VFS permission and idmapping checks, call LSM hooks, break delegations when required, invoke the filesystem inode operation, and emit fsnotify events. Rename uses `s_vfs_rename_mutex` and ordered child locking to avoid directory loops and deadlocks, then calls filesystem `->rename()` and updates dcache with `d_move()` or `d_exchange()` unless the filesystem handles it itself.

## Dependencies

Depends on dcache, mount namespace internals from `mount.h`, `mount_lock` and `rename_lock` seqcounts, RCU, POSIX ACLs, LSM hooks, audit, fsnotify, idmapped mounts, device cgroups, file leases/delegations, open flags, user-copy helpers, folio/page-cache helpers, and per-filesystem inode/dentry operation tables.

## Risks

This is one of the most concurrency-sensitive VFS files. Correct behavior depends on matching RCU seqcount validation with reference acquisition, preventing scoped lookup escapes during rename or mount races, preserving mount and dentry lifetimes, enforcing trailing slash and symlink semantics, and maintaining strict rename locking order. Security-sensitive behavior includes sticky directory checks, protected symlink/hardlink/fifo/regular sysctls, idmapped ownership checks, device-node restrictions, noexec/nodev handling, and LSM hook ordering. Delegation retry paths must drop locks before waiting and then repeat lookup safely.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/namei.c -->