# Group Research: group_1291_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_ext2fs_ext2fs_lookup_c_ce8392b48550

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_lookup.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_lookup.c

This file implements ext2fs directory lookup, `readdir`, directory entry insertion/removal/rewrite, and empty-directory checks. It adapts UFS directory logic to ext2 on-disk directory records, byte order helpers, optional directory-entry file type fields, and htree indexed directories.

Key responsibilities:
- Convert ext2 directory entries to NetBSD `struct dirent` records.
- Resolve pathname components through namecache, htree lookup, and linear directory scans.
- Record mutation metadata in `inode.i_crap` as `struct ufs_lookup_results` for create, delete, link, mkdir, and rename paths.
- Insert, compact, remove, and rewrite ext2 directory entries.
- Validate directory entries when `dirchk` is enabled.
- Check whether a directory contains only `.` and `..`.

Important functions:
- `ext2fs_dirconv2ffs`: Converts `struct ext2fs_direct` to `struct dirent`, including inode byte order, optional `EXT2F_INCOMPAT_FTYPE` type translation, and recomputed `_DIRENT_SIZE`.
- `ext2fs_readdir`: Reads raw ext2 directory bytes with `UFS_BUFRD`, converts entries one at a time, emits cookies in ext2 directory offsets, adjusts `uio_offset`, and reports EOF from inode size.
- `ext2fs_lookup`: Main VOP lookup implementation. It checks execute permission, readonly mutation restrictions, namecache, exclusive lock requirements, htree lookup, slot accounting, sticky-directory authorization, and DELETE/RENAME/CREATE result semantics.
- `ext2fs_search_dirblock`: Shared scan helper for htree lookup; validates forward progress, accumulates insertion slots, and compares names.
- `ext2fs_dirbadentry`: Validates record length, alignment, name length, block containment, and inode range.
- `ext2fs_direnter`: Builds and inserts a new directory entry, using htree insertion when possible and clearing `EXT2_INDEX` if htree insertion fails.
- `ext2fs_add_entry`: Compacts a discovered free range and writes the new entry.
- `ext2fs_dirremove`: Removes an entry by zeroing the inode at block start or merging its record length into the previous entry.
- `ext2fs_dirrewrite`: Repoints an existing directory entry to another inode and updates the optional file type byte.
- `ext2fs_dirempty`: Reads directory entry headers and accepts only `.` plus `..` pointing to the expected parent.

Important interactions:
- Uses `ext2fs_blkatoff`, `ext2fs_bufwr`, `ext2fs_truncate`, htree helpers, UFS namecache, and UFS vnode/inode infrastructure.
- Consumers in `ext2fs_vnops.c` and `ext2fs_rename.c` validate `i_crap` with UFS lookup-result checks.

Notable behavior and risks:
- Namecache misses require an exclusive directory lock; otherwise lookup returns `ENOLCK`.
- `ext2fs_dirbadentry` panics on invalid entries after printing diagnostics, so its boolean return is effectively unreachable for bad entries.
- Htree insertion failure clears the directory inode's `EXT2_INDEX` flag and returns the original error.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_readwrite.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_readwrite.c

This file implements ext2fs read/write vnode operations and buffer-cache helpers for directories and long symlinks. Regular files use UBC; directories and long symlinks use buffer-cache I/O.

Key responsibilities:
- Read regular files through `ubc_uiomove`.
- Read directories and long symlinks through `ext2fs_bufrd`.
- Write regular files through UBC after `ufs_balloc_range`.
- Write directories and long symlinks through `ext2fs_balloc`.
- Update access, change, and modify timestamps.
- Clear privileged mode bits after writes when credentials lack retention authority.
- Roll back file size and `uio` state on write errors.

Important functions:
- `ext2fs_read`: Validates read type and dispatches directory reads to `ext2fs_bufrd`; regular files are bounded by inode size and copied through UBC.
- `ext2fs_bufrd`: Buffer-cache read path with block mapping, simple readahead via `breadn`, short-read protection, and `uiomove`.
- `ext2fs_post_read_update`: Sets `IN_ACCESS` unless `MNT_NOATIME`; performs synchronous metadata update for `IO_SYNC`.
- `ext2fs_write`: Handles append mode, append-only enforcement, max file size, allocation, UBC writes, UVM vnode size updates, and page flushing.
- `ext2fs_bufwr`: Allocates ext2 blocks, extends inode size, copies data into buffers, and chooses synchronous, async, or delayed writes.
- `ext2fs_post_write_update`: Marks ctime/mtime and optional relatime atime, clears setuid/setgid as needed, truncates on error, and syncs metadata for `IO_SYNC`.

Important interactions:
- Uses `ext2fs_balloc`, `ext2fs_setsize`, `ext2fs_truncate`, `ext2fs_update`, UBC, and UFS buffer I/O conventions.
- Regular file allocation uses shared UFS `ufs_balloc_range`; directory/symlink writes use ext2fs-specific block allocation.

Notable behavior and risks:
- The write path temporarily expands UVM write size before allocation/copy and asserts final vnode size equals ext2 inode size.
- In `ext2fs_post_write_update`, the setuid clearing branch uses `ip->i_e2fs_mode &= ISUID` instead of clearing with `~ISUID`; this appears suspicious because the setgid branch uses `&= ~ISGID`.
- On write error it restores `uio_offset`, `uio_resid`, and truncates back to the original size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_readwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_rename.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_rename.c

This file adapts ext2fs rename to NetBSD's `genfs_sane_rename` framework. It provides ext2fs-specific lookup result handling, directory entry mutation, link-count accounting, ancestry checks, and `..` rewriting.

Key responsibilities:
- Wrap the old VOP rename API through `genfs_insane_rename`.
- Implement `genfs_rename_ops` callbacks for ext2fs.
- Enforce immutable/append flags and credential checks via UFS-like genfs helpers.
- Move directory entries, replace targets, and adjust link counts.
- Prevent invalid directory ancestry moves by walking `..`.
- Recalculate source lookup results when target insertion compaction may move the source entry.

Important functions:
- `ext2fs_sane_rename`: Calls `genfs_sane_rename` with ext2fs operations and lookup-result storage.
- `ext2fs_rename`: VOP entry point delegating to `genfs_insane_rename`.
- `ext2fs_gro_rename`: Main mutation routine; temporarily increments the source link count, creates or rewrites the target entry, handles target link counts, rewrites `..` for reparented directories, recalculates source lookup results if needed, and removes the source entry.
- `ext2fs_rename_ulr_overlap_p`: Detects when target insertion may invalidate source removal offsets.
- `ext2fs_rename_recalculate_fulr`: Re-scans the affected directory block range to rediscover the source entry and previous record length.
- `ext2fs_gro_remove`: Removes a non-directory link when rename degenerates into removing another link to the same object.
- `ext2fs_gro_lookup`: Calls `relookup`, unlocks the returned vnode, and copies `dvp->i_crap`.
- `ext2fs_gro_genealogy`: Walks parent links from target directory to detect ancestry conflicts.
- `ext2fs_read_dotdot`: Reads and validates the `..` entry.
- `ext2fs_rename_replace_dotdot`: Decrements old parent link count and rewrites the child's `..` inode.
- `ext2fs_gro_lock_directory`: Locks a directory and fails if it appears removed.

Important interactions:
- Depends on `ext2fs_direnter`, `ext2fs_dirrewrite`, `ext2fs_dirremove`, `ext2fs_dirempty`, `ext2fs_update`, and `ext2fs_truncate`.
- Uses the same `i_crap` lookup-result mechanism as ext2fs create/remove/link/mkdir.

Notable behavior and risks:
- Many comments mark unresolved recovery questions after partial link-count or directory-entry changes.
- `ext2fs_rename_replace_dotdot` ignores the final write error.
- Some cache purge calls are explicitly questioned in comments.
- Removed directories are detected by zero size, with a comment questioning correctness.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_subr.c

This support file provides a block-at-offset helper and ext2 inode timestamp update logic.

Key responsibilities:
- Read the filesystem block containing a directory/file offset and return a pointer inside it.
- Apply deferred inode timestamp flags to ext2 dinode fields.

Important functions:
- `ext2fs_blkatoff`: Computes logical block number with `ext2_lblkno`, reads the block with `bread`, optionally returns an offset-adjusted pointer, and returns the buffer.
- `ext2fs_itimes`: Applies `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, and `IN_MODIFY` to atime, mtime, and ctime fields using ext2 dinode time macros; updates `i_modrev`; marks accessed/modified state; clears pending timestamp flags.

Important interactions:
- `ext2fs_blkatoff` is used by lookup, directory mutation, and rename recomputation.
- `ext2fs_itimes` is installed in `ext2fs_ufsops` and reached through UFS update paths.

Notable behavior:
- `IN_MODIFY` updates both mtime and ctime.
- Timestamp writes use the ext2 inode size, supporting larger inode layouts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_vfsops.c

This file implements ext2fs VFS operations, module registration, mount/unmount/update/reload, superblock and group descriptor handling, vnode loading/creation, file-handle conversion, sync, and statvfs.

Key responsibilities:
- Register ext2fs as a NetBSD VFS module.
- Define VFS and vnode operation vector descriptors.
- Initialize/destroy the ext2 inode pool and shared UFS support.
- Mount root and non-root ext2 filesystems.
- Validate and populate in-memory superblock data.
- Load and save group descriptors, including non-default descriptor sizes.
- Load existing inodes and create new inodes/vnodes.
- Update superblock and group descriptors.
- Report filesystem statistics and sync dirty vnodes/control data.
- Convert between NFS file handles and vnodes.

Important functions and structures:
- `ext2fs_vfsops`: Main VFS dispatch table.
- `ext2fs_genfsops`: Genfs page-cache behavior, including `ext2fs_gop_alloc`.
- `ext2fs_ufsops`: Supplies ext2 inode times, update, buffer read, and buffer write operations.
- `e2fs_cgload` / `e2fs_cgsave`: Convert group descriptor blocks between on-disk descriptor sizes and in-memory `struct ext2_gd`.
- `ext2fs_set_inode_guid`: Reconstructs full uid/gid from low/high ext2 fields.
- `ext2fs_mount`: Handles new mounts, updates, readonly/readwrite transitions, reloads, device checks, clean/dirty state, and statvfs setup.
- `ext2fs_mountfs`: Reads/validates the superblock, allocates mount structures, loads group descriptors, verifies cylinder groups, and initializes UFS mount fields.
- `ext2fs_reload`: Rereads superblock/group descriptors and reloads active vnode inode contents on read-only mounts.
- `ext2fs_loadvnode_content`: Reads and validates an on-disk dinode, including `extra_isize`.
- `ext2fs_init_vnode`, `ext2fs_loadvnode`, `ext2fs_newvnode`: Allocate/load inode structures and initialize vnode/genfs state.
- `ext2fs_statvfs`: Computes filesystem overhead, free blocks, reserved blocks, and inode stats.
- `ext2fs_sync`: Flushes dirty vnodes, device vnode, and modified control data.
- `ext2fs_sbupdate` / `ext2fs_cgupdate`: Write superblock and group descriptors.
- `ext2fs_sbfill`: Validates ext2 magic, revision, block size, group counts, inode size, descriptor size, and unsupported feature flags.

Important interactions:
- Mount-time fields such as `um_dirblksiz`, `um_maxsymlinklen`, `IMNT_DTYPE`, and `IMNT_SHRLOOKUP` shape lookup, symlink, and vnode behavior.
- Uses shared UFS `vcache`, quota, root, close, reclaim, and vget infrastructure.
- Superblock feature checks gate read-write mounting.

Notable behavior and risks:
- Read-write mounts mark clean filesystems dirty; unclean filesystems are marked with `E2FS_ERRORS`.
- Readonly transition flushes files and marks clean only if metadata update succeeds and no error state is set.
- Supports selected ext2/ext3/ext4-style fields, including 64-bit group descriptors, but rejects unsupported incompat/rocompat features unless compile-time ignore options are enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_vnops.c

This file implements ext2fs vnode operations for metadata, creation, removal, linking, directories, symlinks, fsync, locking support, vnode initialization/reclaim, and operation vector registration.

Key responsibilities:
- Implement create, mknod, open, access, getattr, setattr, remove, link, mkdir, rmdir, symlink, readlink, advlock, fsync, and reclaim.
- Enforce ext2 immutable and append-only flags.
- Translate inode fields to/from NetBSD `vattr`.
- Maintain high/low uid and gid fields.
- Create inodes and install directory entries.
- Register regular, special, fifo, and extended-attribute vnode operations.

Important functions:
- `ext2fs_create` / `ext2fs_mknod`: Create new inodes through `ext2fs_makeinode`.
- `ext2fs_open`: Rejects non-append write opens on `EXT2_APPEND` files.
- `ext2fs_access`: Combines readonly/immutable checks with kauth/genfs permission checks.
- `ext2fs_getattr`: Flushes pending times and exports mode, ownership, size, timestamps, flags, generation, blocksize, bytes, type, and filerev.
- `ext2fs_setattr`: Updates flags, owner/group, size, times, birthtime, and mode with authorization and readonly checks.
- `ext2fs_chmod` / `ext2fs_chown`: Apply authorization, update mode/ownership, and clear setuid/setgid when required.
- `ext2fs_remove`: Uses lookup results to remove non-directory entries and decrement link count.
- `ext2fs_link`: Authorizes and creates hard links with link-count rollback on failure.
- `ext2fs_mkdir`: Creates a directory, initializes `.` and `..`, manages parent link count and `DIR_NLINK`, and installs the parent entry.
- `ext2fs_rmdir`: Verifies emptiness, removes parent entry, adjusts link counts, truncates the directory, and purges caches.
- `ext2fs_symlink` / `ext2fs_readlink`: Store/read short symlinks inline and long symlinks through buffer I/O.
- `ext2fs_fsync`: Flushes buffers, updates inode metadata, and optionally issues device cache sync.
- `ext2fs_vinit`: Assigns special/fifo vnode ops and initializes modrev.
- `ext2fs_makeinode`: Creates a vnode/inode pair, optionally writes inode before direntry, inserts direntry, and enters namecache.
- `ext2fs_reclaim`: Frees deleted inodes, calls UFS reclaim, frees dinode storage, destroys genfs node, and returns the inode to the pool.

Important interactions:
- Uses lookup results from `ext2fs_lookup`.
- Depends on `ext2fs_direnter`, `ext2fs_dirremove`, `ext2fs_dirempty`, `ext2fs_truncate`, `ext2fs_update`, and shared UFS routines.
- Wires xattr operations from `ext2fs_xattr.c` into regular, special, and fifo operation tables.

Notable behavior and risks:
- Directory link count overflow uses `EXT2FS_LINK_INF` and sets the `EXT2F_ROCOMPAT_DIR_NLINK` feature.
- `ext2fs_remove`, `ext2fs_link`, `ext2fs_mkdir`, and `ext2fs_rmdir` rely on valid `i_crap` lookup results.
- Reclaim frees an inode when `i_omode == 1` on writable mounts.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_xattr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_xattr.c

This file implements read-only ext2 extended attribute support for vnode xattr operations. It can read and list attributes stored inside the inode body or in an external attribute block; set and delete are not implemented.

Key responsibilities:
- Map NetBSD extattr namespaces to ext2 xattr prefix indexes.
- Read xattrs from inode extra space.
- Read xattrs from the external `e2di_facl` block, including high block bits for 64-bit filesystems.
- List xattr names with optional length-prefix formatting.
- Reject nonzero `uio_offset` for atomic read/list semantics.
- Return `EOPNOTSUPP` for set/delete.

Important functions:
- `ext2fs_find_xattr`: Iterates xattr entries, filters namespace and prefix index, matches names, validates value bounds, and copies value data with `uiomove`.
- `ext2fs_get_inode_xattr`: Finds the in-inode xattr header after `EXT2_REV0_DINODE_SIZE + extra_isize`.
- `ext2fs_get_block_xattr`: Reads the external xattr block and searches it.
- `ext2fs_getextattr`: Performs credential checks, resolves the longest matching prefix, tries inode xattrs first, then block xattrs.
- `ext2fs_list_xattr`: Formats visible attribute names from prefix plus stored suffix.
- `ext2fs_list_inode_xattr` / `ext2fs_list_block_xattr`: List inode-body and external-block xattrs.
- `ext2fs_listextattr`: Checks `EXT2F_COMPAT_EXTATTR`, credentials, offset semantics, and combines inode/block listings.
- `ext2fs_setextattr` / `ext2fs_deleteextattr`: Stubs returning `EOPNOTSUPP`.

Important interactions:
- Uses structures and iteration macros from `ext2fs_xattr.h`.
- Exposed through vnode op tables in `ext2fs_vnops.c`.
- Uses NetBSD `extattr_check_cred`.

Notable behavior and risks:
- Xattr modification is unsupported.
- `ext2fs_find_xattr` appears to try to clamp transfer length to `uio_resid`, but then calls `uiomove(value, value_len, uio)`; this should be reviewed because it may not enforce the intended `len`.
- Prefix table includes `"security"` without a trailing dot, while related ext2 conventions commonly use `security.`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_xattr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_xattr.h

This header defines ext2 extended attribute on-disk structures, constants, iteration macros, prefix indexes, and vnode operation prototypes.

Key responsibilities:
- Define the ext2 xattr magic value and limits.
- Describe inode-body and external-block xattr headers.
- Describe xattr entry layout.
- Provide aligned entry-size and next-entry macros.
- Define ext2 xattr name prefix indexes.
- Declare ext2fs xattr vnode operation handlers.

Important definitions:
- `EXT2FS_XATTR_MAGIC`: Magic value `0xEA020000`.
- `EXT2FS_XATTR_NAME_LEN_MAX`: Maximum xattr name length.
- `EXT2FS_XATTR_REFCOUNT_MAX`: External xattr block refcount limit.
- `struct ext2fs_xattr_ibody_header`: Header for inode-body xattrs.
- `struct ext2fs_xattr_header`: Header for external xattr blocks, including refcount, block count, hash, checksum, and reserved fields.
- `struct ext2fs_xattr_entry`: Entry header with name length/index, value offset/block/size, hash, and flexible name bytes.
- `EXT2FS_XATTR_IS_LAST_ENTRY`: Stops on zero marker or when the next entry would exceed the end pointer.
- `EXT2FS_XATTR_LEN` / `EXT2FS_XATTR_NEXT`: 4-byte aligned entry traversal.
- `EXT2FS_XATTR_IFIRST` / `EXT2FS_XATTR_BFIRST`: First-entry helpers.
- Prefix constants for none, user, POSIX ACL, trusted, security, system, richacl, and encryption namespaces.

Important interactions:
- Used by `ext2fs_xattr.c` for parsing and listing xattrs.
- Prototypes are referenced by vnode op tables in `ext2fs_vnops.c`.

Notable behavior:
- The header explicitly notes that Linux checks only the zero terminator, while this code also checks that the next entry does not overflow the supplied end pointer.
- Value blocks are documented as unsupported through `e_value_block`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/Makefile

This kernel include Makefile installs public FFS headers.

Key responsibilities:
- Set `INCSDIR` to `/usr/include/ufs/ffs`.
- Install `ffs_extern.h` and `fs.h`.
- Include NetBSD kernel include make rules through `<bsd.kinc.mk>`.

Notable behavior:
- This is packaging/build metadata only; it contains no allocator or filesystem logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_alloc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_alloc.c

This file implements FFS block, fragment, inode, cylinder-group, snapshot, and discard/TRIM allocation accounting. It is the core free-space allocator and deallocator for UFS/FFS.

Key responsibilities:
- Allocate and reallocate data blocks/fragments.
- Allocate and free inodes.
- Choose preferred cylinder groups and block locations.
- Maintain cylinder group summaries, free bitmaps, fragment summaries, cluster accounting, and old UFS1 rotational summaries.
- Support quota checks and WAPBL journaling hooks.
- Support snapshot block/inode accounting variants.
- Batch discard/TRIM requests and then free blocks in filesystem metadata.
- Validate bad allocations and report filesystem full/out-of-inode errors.

Important functions:
- `ffs_check_bad_allocation`: Validates block number, size, fragment alignment, and filesystem bounds.
- `ffs_alloc`: Allocates a block or fragment, checking free space, reserved-space authorization, quota, block preferences, and hash fallback.
- `ffs_realloccg`: Grows a fragment in place if possible; otherwise allocates a new block/fragment, copies buffer state, frees the old allocation, and adjusts quotas and inode block counts.
- `ffs_valloc`: Allocates an inode inside a WAPBL transaction using `ffs_dirpref` for directories and `ffs_hashalloc`/`ffs_nodealloccg`.
- `ffs_dirpref`: Selects a directory cylinder group based on average free inodes/blocks, directory density, root-directory spreading, and contiguous-directory limits.
- `ffs_blkpref_ufs1` / `ffs_blkpref_ufs2`: Compute block allocation preferences for UFS1/UFS2, including contiguous-file hints and section/cylinder group heuristics.
- `ffs_hashalloc`: Tries the preferred cylinder group, then quadratic rehash, then brute-force cylinder group search.
- `ffs_fragextend`: Extends an existing fragment in place and updates fragment summaries.
- `ffs_alloccg`: Allocates a block or fragment from one cylinder group; splits full blocks when fragment allocation requires it.
- `ffs_alloccgblk`: Allocates a full block from a cylinder group, preferring the requested block, then the rotor/search result.
- `ffs_nodealloccg`: Allocates an inode from one cylinder group, lazily initializes UFS2 inode blocks, registers WAPBL inode allocation, and updates inode/directory summaries.
- `ffs_blkalloc` / `ffs_blkalloc_ump`: Explicitly mark a block or fragment allocated, mirroring free logic for snapshot/COW paths.
- `ffs_blkfree`: Frees a block or fragment, with snapshot interception and optional discard batching.
- `ffs_blkfree_snap`: Frees a block in a snapshot cylinder group copy.
- `ffs_blkfree_common`: Shared free-map and summary update logic for normal and snapshot block frees.
- `ffs_vfree`, `ffs_freefile`, `ffs_freefile_snap`, `ffs_freefile_common`: Free inode bitmap entries and update inode/directory summaries.
- `ffs_checkfreefile`: Checks whether an inode is free in a snapshot cylinder group bitmap.
- `ffs_mapsearch`: Searches a cylinder group free bitmap for a fragment pattern.
- `ffs_discard_init`, `ffs_discard_finish`, `ffs_discardcb`, `ffs_blkfree_td`: Manage deferred discard workqueue entries and metadata free completion.
- `ffs_fserr`: Logs filesystem allocation errors with credential/process context.

Important interactions:
- Called by FFS block allocation paths in `ffs_balloc.c` and inode/vnode allocation paths elsewhere.
- Uses `um_lock` heavily; several allocator helpers intentionally release the lock on success and retain/reacquire it on failure according to comments.
- Integrates with quotas via `chkdq`.
- Integrates with WAPBL through allocation/deallocation registration and transaction boundaries.
- Uses `ffs_snapblkfree` and snapshot-specific helpers to preserve snapshot semantics.
- Uses `cg_chkmagic`, `cg_blksfree`, `cg_inosused`, `ffs_clusteracct`, `ffs_fragacct`, and UFS byte-swap helpers.

Notable behavior and risks:
- `B_CONTIG` allocation has special error-path lock handling called “suspect” in comments and may return `ENOSPC` without normal full-filesystem reporting.
- `ffs_mapsearch` panics if the bitmap cannot satisfy a request that summaries said was possible.
- Freeing already-free blocks/fragments generally panics on normal devices, but snapshot paths may silently return for already-free full blocks.
- Discard batching keeps one deferred entry and coalesces backwards deallocations up to a fixed `100*1024` byte limit.
- UFS2 inode allocation may temporarily drop the cylinder group buffer to avoid deadlock while initializing more inode blocks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_appleufs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_appleufs.c

This file implements Apple UFS label checksum, validation, and creation helpers. It is usable in kernel, standalone, and userland-style builds.

Key responsibilities:
- Compute Apple UFS label checksum.
- Validate an on-disk Apple UFS label and convert multi-byte fields from big endian.
- Construct a new Apple UFS label with default name/time/uuid behavior.

Important functions:
- `ffs_appleufs_cksum`: Computes a 16-bit one's-complement checksum over `APPLEUFS_LABEL_SIZE`, matching `in_cksum` style.
- `ffs_appleufs_validate`: Verifies magic, checksum, nonzero name length, clamps maximum name length, NUL-terminates the name, converts fields to host byte order, and returns `EINVAL` for invalid labels.
- `ffs_appleufs_set`: Clears and fills a label, defaulting missing names to `"untitled"`, defaulting time to current time where available, optionally generating a kernel random uuid, writing fields big endian, and storing the checksum.

Important interactions:
- Uses Apple UFS label definitions from `fs.h`.
- Uses `cprng_fast64` in kernel builds for missing UUIDs.
- Provides portable assertions and libc includes for non-kernel, non-standalone builds.

Notable behavior:
- `APPLEUFS_LABEL_SIZE` is assumed even, so the odd trailing byte checksum case is disabled.
- `ffs_appleufs_validate` can validate into a caller-provided output label or a temporary internal label if output is `NULL`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_appleufs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_balloc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_balloc.c

This file implements FFS logical-block allocation for UFS1 and UFS2 files. It maps file offsets to direct, indirect, and external-attribute blocks, allocating fragments/full blocks and indirect metadata as required.

Key responsibilities:
- Dispatch block allocation between UFS1 and UFS2.
- Allocate direct blocks and grow terminal fragments.
- Allocate single/double/triple indirect block chains.
- Write newly allocated indirect blocks synchronously before linking them.
- Support UFS2 external data blocks via `IO_EXT`.
- Run filesystem copy-on-write hooks for buffers.
- Unwind partial allocations on failure and restore quotas/inode block counts.

Important functions:
- `ffs_balloc`: Dispatches to UFS1 or UFS2 implementation and runs `fscow_run` on returned buffers.
- `ffs_extb`: Reads a UFS2 external block pointer with byte-swap handling.
- `ffs_balloc_ufs1`: Handles UFS1 direct and indirect allocation using 32-bit block pointers.
- `ffs_balloc_ufs2`: Handles UFS2 direct, indirect, and `IO_EXT` external-data allocation using 64-bit block pointers.
- Both UFS implementations:
  - Compute `lbn` and requested block size from offset/size.
  - Extend the previous last fragment to a full block when writing beyond it.
  - Allocate or reallocate direct fragments/blocks.
  - Use `ufs_getlbns` to compute indirect paths.
  - Allocate indirect blocks with `B_METAONLY`, zero them, synchronously write them, then link them.
  - Allocate data blocks at the final indirect level.
  - On failure, invalidate allocated indirect buffers, clear linked pointers, free allocated blocks, restore quota, and reduce inode block counts.

Important interactions:
- Uses allocator policy and accounting from `ffs_alloc.c`: `ffs_alloc`, `ffs_realloccg`, `ffs_blkfree`, and block preference helpers.
- Uses `ffs_getblk`, `bread`, `bwrite`, `bdwrite`, `bawrite`, and UFS byte-swap helpers.
- Uses `fscow_run` before modifying existing indirect buffers and after returning allocated buffers.
- External data requires UFS2 and asserts `UFS_EA` support unless not using `IO_EXT`.

Notable behavior and risks:
- Indirect blocks are written synchronously before parent pointers are updated to avoid pointers to garbage.
- Failure unwinding is complex and intentionally writes delayed buffers to resolve dependencies before freeing blocks.
- In the UFS2 path that extends a previous fragment before a later write, the call uses `ffs_getdb(fs, ip, lbn)` where the analogous UFS1 path uses the previous block `nb`; this asymmetry is worth review.
- `IO_EXT` uses negative logical block numbers (`-1 - lbn`) for external attribute data buffers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_balloc.c -->