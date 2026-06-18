# Group Research: group_1256_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_udf_udf_vnops_c_sources_ce70b7cc247c

Scope: subset A from `Docs/research_subset_a.md`, covering the listed NetBSD `sys/fs` UDF, Unicode, union, unionfs, and v7fs files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_vnops.c

## Scope

This file implements NetBSD UDF vnode operations: vnode lifecycle, buffered read/write through UBC, directory lookup and iteration, attribute access and mutation, symlink encoding/decoding, creation/removal/linking, fsync, advisory locking, block mapping, and the UDF vnode operation vector.

## Public And Internal APIs Covered

- Lifecycle: `udf_inactive()`, `udf_reclaim()`.
- I/O: `udf_read()`, `udf_write()`, `udf_trivial_bmap()`, `udf_vfsstrategy()`, `udf_fsync()`.
- Directory/name operations: `udf_lookup()`, `udf_readdir()`, `udf_create()`, `udf_mknod()`, `udf_mkdir()`, `udf_link()`, `udf_remove()`, `udf_rmdir()`.
- Attribute and permission operations: `udf_getattr()`, `udf_setattr()`, `udf_chsize()`, `udf_pathconf()`, `udf_access()`.
- Symlinks: `udf_symlink()`, `udf_readlink()`, internal `udf_do_symlink()` and `udf_do_readlink()`.
- Locking: `udf_advlock()`.
- Vnode table: `udf_vnodeop_entries`, `udf_vnodeop_opv_desc`, and exported `udf_vnodeop_p`.

## Control Flow And Behavior

- `udf_inactive()` checks descriptor link count and recycles non-system unlinked nodes; otherwise it writes dirty inode metadata with `udf_update()`.
- `udf_reclaim()` unlocks the vnode, deletes allocation for unlinked non-system nodes, updates on close, waits for outstanding node descriptor writeout, and disposes all in-memory node state.
- `udf_read()` validates regular-file semantics unless `IO_ALTSEMANTICS` is set, derives file size from FE/EFE descriptors, reads via `ubc_uiomove()`, and marks access time unless `MNT_NOATIME`.
- `udf_write()` handles append mode, grows files with `udf_grow_node()`, allocates pages with `GOP_ALLOC()`, writes through UBC, lazily flushes chunks, updates file size, marks change/update/access flags, and rolls back size and `uio` state on error.
- `udf_vfsstrategy()` receives file buffers, validates sector alignment, and dispatches to `udf_read_filebuf()` or `udf_write_filebuf()` for virtual-to-physical translation.
- `udf_readdir()` synthesizes `"."`, walks the UDF FID stream with `udf_read_fid_stream()`, skips deleted and invisible entries, and returns directory cookies via `uio_offset`.
- `udf_lookup()` performs access checks, readonly mutation rejection, namecache lookup, special handling for `"."` and `".."`, directory stream lookup via `udf_lookup_name_in_dir()`, vnode instantiation through `udf_get_node()`, sticky-directory delete checks, and namecache insertion.
- `udf_getattr()` maps UDF FE/EFE fields into `struct vattr`, translates anonymous UID/GID, adjusts directory link counts, computes symlink reported size by decoding the target, extracts birth time from extended attributes when available, and handles device-node extended attributes.
- `udf_setattr()` rejects immutable vnode attributes, then sequences `chflags`, truncate, ownership, mode, and time updates through helper routines.
- `udf_chown()`, `udf_chmod()`, and `udf_chtimes()` enforce NetBSD kauth checks and mark UDF inode flags before writing metadata.
- `udf_chsize()` validates file type and readonly state, resizes allocation through `udf_resize_node()`, updates flags, and writes metadata.
- `udf_symlink()` creates a node and writes UDF path-component-encoded symlink contents; `udf_readlink()` decodes UDF path components back into a POSIX path.
- `udf_remove()` and `udf_rmdir()` detach directory entries, update resulting link count context, purge caches, and shrink removed directories to prevent further `".."` traversal.
- `udf_fsync()` flushes pages, updates times, skips metadata writes on readonly or data-only fsync, optionally waits for outstanding vnode and UDF descriptor I/O, then writes out dirty node descriptors.
- The vnode table delegates unsupported/default behavior to genfs helpers and wires UDF-specific operations for metadata and directory behavior.

## State And Data Structures

- Core object is `struct udf_node` stored in `vnode->v_data`.
- Reads and writes consult UDF `file_entry` or `extfile_entry` descriptors for length, ownership, link count, timestamps, allocation, and embedded file data.
- Uses UDF mount state for logical block size, sector size, charset conversion, anonymous UID/GID, and mount path.
- Directory operations use FID descriptors, `struct dirent`, `struct dirhash`, and UDF long allocation descriptors.
- Synchronization state includes `i_flags`, `outstanding_bufs`, `outstanding_nodedscr`, vnode `v_numoutput`, `node_mutex`, `node_lock`, and `lockf`.

## Dependencies

- UDF helpers from `udf_subr.h`, `udf_bswap.h`, and `ecma167-udf.h` provide descriptor conversion, allocation, directory, node, timestamp, charset, and writeout operations.
- NetBSD VFS/VM APIs: vnode ops, UBC, genfs page operations, kauth, dirhash, namecache, lockf, `vn_rdwr()`, and buffer cache.
- Rename is implemented elsewhere in `udf_rename.c` but is registered here in the vnode table.

## Risks And Invariants

- FE/EFE descriptor selection is repeated throughout the file; callers assume exactly one descriptor type is valid.
- Write rollback must keep on-disk allocation, vnode size, and caller `uio` state consistent after partial failure.
- Symlink path decoding treats malformed UDF path components as `EINVAL`; buffer bounds are guarded by `PATH_MAX` and `UDF_SYMLINKBUFLEN`.
- Directory removal depends on a filled dirhash and truncates the removed directory to prevent stale parent traversal.
- `udf_getattr()` has several TODO/bug-alert comments around symlink size, generation numbers, flags, file revisions, and device extended attributes.
- `udf_fsync()` may return early for async outstanding I/O unless wait semantics are requested.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unicode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/unicode.h

## Scope

This header provides small static helper routines for converting 16-bit Unicode code points to and from UTF-8 byte sequences.

## APIs And Behavior

- Declares and defines `wget_utf8(const char **, size_t *)`.
- Declares and defines `wput_utf8(char *, size_t, u_int16_t)`.
- `wget_utf8()` consumes one UTF-8 sequence from a byte pointer and remaining-size pair, advances both, and returns a `u_int16_t` code point.
- Invalid first bytes, missing continuation bytes, or truncated sequences fall back to consuming one byte as an ISO-8859-1-like value.
- Supports 1-, 2-, and 3-byte UTF-8 forms only, matching the 16-bit return type.
- `wput_utf8()` writes a 1-, 2-, or 3-byte UTF-8 encoding for a `u_int16_t` value and returns bytes written.
- `wput_utf8()` returns `0` if the caller-provided output buffer is too small.

## Dependencies

- Requires kernel-style `KASSERT()` and fixed-width integer types.
- Derived from NetBSD libc locale UTF conversion logic and intended for filesystem code that needs compact UTF-8 handling.

## Risks And Invariants

- This is not a complete Unicode scalar-value validator; it handles 16-bit values and does not reject overlong encodings or surrogate code units.
- Invalid UTF-8 is deliberately lossy-tolerant by preserving the first byte as a single character.
- `wget_utf8()` must only be called with `*sz > 0`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/union/Makefile

## Scope

This makefile installs the legacy union filesystem public kernel header.

## Build Behavior

- Sets `INCSDIR` to `/usr/include/miscfs/union`.
- Installs `union.h` through NetBSD’s `bsd.kinc.mk` kernel include framework.

## Dependencies And Role

- Depends on the standard NetBSD kernel include make rules.
- Keeps the legacy `fs/union` user-visible mount argument/header ABI available under the historical `miscfs/union` include path.

## Risks And Invariants

- The install path is part of the exposed include layout; changing it would break consumers expecting `<miscfs/union/union.h>`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/union.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/union/union.h

## Scope

This header defines the legacy NetBSD union filesystem mount ABI, in-kernel mount/node structures, cache flags, macros, and cross-file function prototypes.

## APIs And Data Structures

- Public mount arguments: `struct union_args { char *target; int mntflags; }`.
- Mount modes: `UNMNT_ABOVE`, `UNMNT_BELOW`, `UNMNT_REPLACE`, `UNMNT_OPMASK`, and `UNMNT_BITS`.
- Kernel mount state: `struct union_mount` with upper/lower root vnodes, mount credentials, creation mode, and operation mode.
- Kernel node state: `struct union_node` with vnode lock, cache linkage, reference count, mount pointer, back pointer, upper/lower vnodes, upper parent directory/name for copy-up, parent union vnode, lower open count, cache flags, readdir hook state, directory cache, and tracked upper/lower file sizes.
- Creation defaults: `UN_DIRMODE`, `UN_FILEMODE`.
- Cache flag: `UN_CACHED`.
- Conversion macros: `MOUNTTOUNIONMOUNT()`, `VTOUNION()`, `UNIONTOV()`, `LOWERVP()`, `UPPERVP()`, `OTHERVP()`, `LOCKVP()`.

## Declared Operations

- Node/cache: `union_allocvp()`, `union_freevp()`, `union_diruncache()`, `union_removed_upper()`, `union_newsize()`.
- Copy-up and creation: `union_copyfile()`, `union_copyup()`, `union_mkshadow()`, `union_mkwhiteout()`, `union_vn_create()`, `union_cn_close()`.
- Directory/delete logic: `union_check_rmdir()`, `union_dowhiteout()`, `union_readdirhook()`.
- VFS hooks: `VFS_PROTOS(union)`, `union_init()`, `union_reinit()`, `union_done()`.
- Vnode operation vector pointer: `union_vnodeop_p`.

## Dependencies

- Kernel-only portions depend on NetBSD vnode, mount, componentname, credentials, mutex, and VFS operation definitions.
- Shared by `union_subr.c`, `union_vfsops.c`, and `union_vnops.c`.

## Risks And Invariants

- The lock-order comment documents important invariants: vnode lock precedes `un_lock`; hash lock protects cache linkage/reference counts.
- `un_uppervp` and `un_lowervp` may be individually null, but the implementation assumes not both are null.
- `un_path` and `un_dirvp` are required later for delayed copy-up or whiteout creation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/union.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/union_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/union/union_subr.c

## Scope

This file implements legacy union filesystem support routines: global node hash management, union vnode allocation and loading, upper/lower vnode replacement, file copy-up, shadow directory and whiteout creation, directory stack caching, rmdir emptiness checks, and the `vn_readdir()` hook used to descend through union layers.

## Public And Internal APIs Covered

- Global lifecycle: `union_init()`, `union_reinit()`, `union_done()`.
- Node mutation/lifetime: `union_newlower()`, `union_newupper()`, `union_newsize()`, `union_allocvp()`, `union_freevp()`, `union_loadvnode()`.
- Copy-up: `union_copyfile()`, `union_copyup()`, `union_vn_create()`, `union_vn_close()`.
- Upper removal and whiteout policy: `union_removed_upper()`, `union_dowhiteout()`, `union_mkwhiteout()`, `union_mkshadow()`.
- Directory support: `union_dircache()`, `union_diruncache()`, internal `union_dircache_r()`, `union_check_rmdir()`, `union_readdirhook()`.
- Internal helpers: `union_ref()`, `union_rele()`, `union_do_lookup()`.

## Control Flow And Behavior

- `union_init()` creates a vnode-count-sized hash table and mutex; `union_reinit()` rehashes live nodes after vnode table sizing changes.
- `union_done()` destroys the hash and clears the global union readdir hook.
- `union_allocvp()` either reuses a cached union node by upper/lower vnode pair or allocates a new `union_node`, stores copied component names and parent directory references for later copy-up, inserts into the hash, and attaches it through `vcache_get()`.
- `union_loadvnode()` initializes a newly loaded union vnode, mirrors type/special-device state from the active backing vnode, shares interlocks/VM object locks/kqueue lists, detects root aliases, and seeds tracked upper/lower sizes.
- `union_newupper()` installs an upper vnode after copy-up, transfers locking from the union vnode to the upper vnode, updates shared vnode locks/VM object state, and rehashes the cache key.
- `union_newlower()` installs a lower vnode and rehashes the cache key.
- `union_newsize()` tracks upper/lower file size changes and updates UVM vnode size, preferring upper-layer size when both exist.
- `union_copyup()` creates an upper file, optionally copies content from the lower file, copies permissions and flags, closes/reopens underlying opens, and resets lower open accounting.
- `union_mkshadow()` creates a shadow directory in the upper layer using mount credentials for below mounts and mount umask-derived mode.
- `union_mkwhiteout()` creates a whiteout entry after confirming the upper target name does not already exist.
- `union_removed_upper()` removes a node from the cache after upper deletion and leaves the upper pointer intact until reclaim to avoid a union node with no backing vnode.
- `union_check_rmdir()` verifies that lower-layer directory entries are either absent or whiteouted in the upper layer before permitting rmdir.
- `union_readdirhook()` is installed globally and swaps a file descriptor from an upper directory vnode to the next lower directory vnode when the upper stream reaches EOF and the directory is not opaque.

## State And Data Structures

- Global hash: `uhashtbl`, `uhash_mask`, `uhash_lock`, keyed by upper/lower vnode addresses.
- `union_node` references are protected by `uhash_lock`; per-node mutable upper/lower/size fields use `un_lock` and vnode locks.
- Directory cache stores a NULL-terminated list of referenced backing directory vnodes for stacked readdir traversal.
- Copy-up state uses `un_dirvp`, `un_path`, and `un_openl`.

## Dependencies

- NetBSD vnode cache (`vcache_get()`), vnode locking, VOP lookup/create/open/close/read/write/getattr/setattr/readdir/whiteout, UVM vnode sizing, specfs special node setup, namei component structures, and credentials.
- Shared with legacy `union_vfsops.c` and `union_vnops.c`.

## Risks And Invariants

- Hash cache correctness depends on rehashing whenever upper or lower vnode pointers change.
- Lock transfer in `union_newupper()` is delicate because the union vnode begins by sharing its lock with itself and then shares the upper vnode’s interlock/VM lock/klist.
- Copy-up ignores some close/open errors by design; open-count repair is best-effort.
- Directory cache entries hold vnode references and must be released on inactive/removal/reclaim.
- `union_readdirhook()` mutates `struct file` vnode and offset state, so it depends on consistent open/close behavior in the VFS layer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/union_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/union_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/union/union_vfsops.c

## Scope

This file implements the legacy union filesystem VFS layer: mount, unmount, root lookup, statvfs composition, sync/vget stubs, rename-lock forwarding, module attach/detach, sysctl registration, and the `struct vfsops` definition.

## Public APIs And Operations

- Module declaration: `MODULE(MODULE_CLASS_VFS, union, NULL)`.
- VFS entry points: `union_mount()`, `union_start()`, `union_unmount()`, `union_root()`, `union_statvfs()`, `union_sync()`, `union_vget()`.
- Rename serialization: `union_renamelock_enter()`, `union_renamelock_exit()`.
- Operation vectors: `union_vfsops`, `union_vnodeopv_descs`.
- Module command handler: `union_modcmd()`.
- Sysctl setup: `unionfs_sysctl_setup`.

## Control Flow And Behavior

- `union_mount()` validates mount arguments, supports `MNT_GETARGS`, rejects update mounts, references the covered vnode as the lower root, resolves the target path as the upper root, and requires the target to be a directory.
- Mount mode controls layer order: `UNMNT_ABOVE` puts target above covered vnode, `UNMNT_BELOW` inverts the order, and `UNMNT_REPLACE` exposes only the target.
- Mount setup marks the union mount MP-safe only if all active layers are MP-safe, validates upper-layer whiteout support for writable mounts, stores mount credentials and default shadow-directory mode, copies locality and readonly flags, assigns a new fsid, records lower mount dependency, and formats `f_mntfromname`.
- It installs `vn_union_readdir_hook` if not already present.
- `union_unmount()` repeatedly flushes vnodes to account for parent references, optionally uses `FORCECLOSE`, then releases upper/lower root vnodes, frees mount credentials, and frees `union_mount`.
- `union_root()` returns a locked union vnode wrapping the mount’s upper/lower root pair.
- `union_statvfs()` combines lower used resources with upper total/free resources, with upper filesystem characteristics taking priority.
- `union_sync()` is a no-op because the union layer does not cache independent data.
- `union_vget()` and file-handle operations are unsupported.
- Rename locks are delegated to the upper filesystem because mutations occur there.

## State And Data Structures

- `struct union_mount` is allocated per mount and stored in `mp->mnt_data`.
- Mount flags reflect upper-layer readonly and combined locality.
- Root vnode construction delegates to `union_allocvp()`.

## Dependencies

- NetBSD VFS module framework, namei, vnode locking, mount statistics, kauth credentials, whiteout VOP, lower-mount tracking, genfs suspend control, and legacy union support routines.

## Risks And Invariants

- Writable union mounts require upper-layer whiteout support; otherwise deletions of lower-layer objects cannot be represented.
- `MNT_UPDATE` is unsupported, so readonly/readwrite state is fixed at mount time.
- Unmount may need multiple `vflush()` passes because union nodes hold parent vnode references.
- The sysctl node uses historical hard-coded `CTL_VFS` number 15.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/union_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/union_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/union/union_vnops.c

## Scope

This file implements the legacy union filesystem vnode operation layer, including lookup, creation, copy-up-on-write, attribute forwarding, read/write dispatch, destructive operations with whiteouts, directory iteration handoff, locking, VM page forwarding, and the vnode operation vector.

## Public APIs And Operations

- Vnode operation functions: `union_parsepath()`, `union_lookup()`, `union_create()`, `union_whiteout()`, `union_mknod()`, `union_open()`, `union_close()`, `union_access()`, `union_getattr()`, `union_setattr()`, `union_read()`, `union_write()`, `union_ioctl()`, `union_poll()`, `union_revoke()`, `union_mmap()`, `union_fsync()`, `union_seek()`, `union_remove()`, `union_link()`, `union_rename()`, `union_mkdir()`, `union_rmdir()`, `union_symlink()`, `union_readdir()`, `union_readlink()`, `union_abortop()`, `union_inactive()`, `union_reclaim()`, `union_lock()`, `union_unlock()`, `union_bmap()`, `union_print()`, `union_islocked()`, `union_pathconf()`, `union_advlock()`, `union_strategy()`, `union_bwrite()`, `union_getpages()`, `union_putpages()`, `union_kqfilter()`.
- Internal lookup helper: `union_lookup1()`.
- Operation table: `union_vnodeop_entries`, `union_vnodeop_opv_desc`, exported `union_vnodeop_p`.

## Control Flow And Behavior

- `union_lookup()` probes upper and lower directories, honors whiteouts and opaque directories, forces lower lookup to `LOOKUP`, creates shadow directories for lower directories missing from the upper layer, and returns a cached union vnode through `union_allocvp()`.
- `".."` handling in `union_lookup1()` walks mount boundaries and avoids trapping traversal inside lower mounts.
- `union_open()` opens the upper vnode if present; otherwise it copies regular files up before write opens or opens the lower vnode for read-only access while tracking `un_openl`.
- `union_close()` forwards close to the active backing vnode and repairs upper `v_writecount` for write opens.
- `union_access()` rejects writes on readonly union mounts, can copy up a regular lower vnode before write access checks, and checks lower access using mount credentials for below mounts.
- `union_getattr()` gets upper attributes when present, also consults lower directory attributes to synthesize link counts, updates tracked sizes, and rewrites `va_fsid` to the union mount fsid.
- `union_setattr()` copies up lower regular files when needed, handles truncation, forwards attributes to the upper layer, and treats special lower-only nodes as readonly except for harmless size-zero operations.
- `union_read()` and `union_write()` forward to the active backing vnode and update union UVM size tracking from resulting offsets.
- `union_remove()` and `union_rmdir()` delete upper entries when they exist and create whiteouts when needed to hide lower entries.
- `union_link()` copies up lower-only union source files before linking and may rerun lookup state after dropping/reacquiring parent locks.
- `union_rename()` maps union vnodes to upper vnodes, marks source whiteout when a lower vnode exists, and delegates to upper `VOP_RENAME()`. It does not copy up lower-only sources.
- `union_readdir()` reads the upper directory normally, or a lower hook node created by `union_readdirhook()` when descending the layer stack.
- `union_lock()` locks either the upper vnode or the union vnode depending on the current backing state and retries if copy-up changes the lock target during acquisition.
- VM and buffer operations forward to the active backing vnode while asserting that writable buffers are not directed to lower regular files.
- `union_getpages()` and `union_putpages()` require the union vnode and backing vnode to share the same VM object lock.

## State And Data Structures

- Uses `struct union_node` for upper/lower vnode pointers, lower open count, saved parent/path, directory cache, hook-node flag, and size tracking.
- `NODE_IS_SPECIAL()` permits direct operations on block/char/socket/fifo nodes where copy-up is not applicable.
- The vnode operation table combines union-specific operations with genfs defaults for unsupported fallocate/fdiscard and accessx.

## Dependencies

- Legacy support functions from `union_subr.c`.
- NetBSD VFS/VOP APIs, namecache, genfs locking and VM operations, specfs fsync, UVM page operations, and kauth access checks.

## Risks And Invariants

- Write operations to normal files assume an upper vnode exists; missing upper on non-special writes is a panic condition.
- Lower-only regular files must be copied up before mutation, locking, linking, or truncation to preserve copy-on-write semantics.
- Whiteout creation is required when removing or renaming upper entries that mask lower entries.
- `union_rename()` explicitly notes lower-only source copy-up is not implemented and returns `EXDEV` in those cases.
- Locking must tolerate the active lock target changing when an upper vnode appears.
- Directory listing correctness depends on the global readdir hook and libc/userland duplicate elimination.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/union/union_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/Makefile

## Scope

This makefile installs the newer `unionfs` public kernel header.

## Build Behavior

- Sets `INCSDIR` to `/usr/include/miscfs/union`.
- Installs `union.h` through `bsd.kinc.mk`.

## Dependencies And Role

- Uses the same installed include directory as legacy union, preserving the mount ABI name and header location.
- The source-local header is named `unionfs.h`, but the installed header name is `union.h`.

## Risks And Invariants

- Shared install path reflects compatibility with historical union mount interfaces.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs.h

## Scope

This header defines the newer unionfs filesystem’s mount arguments, mount/node state, copy and whiteout modes, per-thread node status tracking, operation prototypes, diagnostics, and vnode access macros.

## APIs And Data Structures

- Public ABI: `struct union_args`, alias `unionfs_args`, and mount flags `UNMNT_ABOVE`, `UNMNT_BELOW`, `UNMNT_REPLACE`, `UNMNT_OPMASK`, `UNMNT_BITS`.
- Copy modes: `UNIONFS_TRADITIONAL`, `UNIONFS_TRANSPARENT`, `UNIONFS_MASQUERADE`.
- Whiteout modes: `UNIONFS_WHITE_ALWAYS`, `UNIONFS_WHITE_WHENNEEDED`.
- Mount state: `struct unionfs_mount` with lower/upper/root vnodes, mutex, copy/whiteout modes, uid/gid, operation mode, and directory/file permission masks.
- Per-thread status: `struct unionfs_node_status` tracks pid/lwp id, lower/upper open counts, lower open mode, readdir state, and status flags.
- Node state: `struct unionfs_node` stores lower/upper vnodes, parent unionfs vnode, back pointer, status list, saved path, and node flags.
- Node status flag: `UNS_OPENL_4_READDIR`.
- Node flags: `UNIONFS_OPENEXTL`, `UNIONFS_OPENEXTU`.
- Macros: `MOUNTTOUNIONFSMOUNT()`, `VTOUNIONFS()`, `UNIONFSTOV()`, `UNIONFSVPTOLOWERVP()`, `UNIONFSVPTOUPPERVP()`.

## Declared Operations

- Node lifecycle/status: `unionfs_nodeget()`, `unionfs_noderem()`, `unionfs_get_node_status()`, `unionfs_tryrem_node_status()`.
- Copy-up and creation helpers: `unionfs_copyfile()`, `unionfs_create_uppervattr_core()`, `unionfs_create_uppervattr()`, `unionfs_mkshadowdir()`, `unionfs_mkwhiteout()`.
- Delete/relookup helpers: `unionfs_check_rmdir()`, `unionfs_relookup_for_create()`, `unionfs_relookup_for_delete()`, `unionfs_relookup_for_rename()`.
- Diagnostic vnode checks for upper/lower pointers when `DIAGNOSTIC` is enabled.
- Vnode operation vector pointer: `unionfs_vnodeop_p`.

## Dependencies

- Kernel-only vnode, mount, credentials, componentname, mutex, and malloc declarations.
- Shared by `unionfs_subr.c`, `unionfs_vfsops.c`, and `unionfs_vnops.c`.

## Risks And Invariants

- Per-thread node status requires the unionfs vnode to be locked exclusively when retrieved or removed.
- Copy mode controls security-visible upper-layer ownership/mode synthesis.
- Diagnostic macros can add file/line validation for upper/lower vnode extraction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_subr.c

## Scope

This file implements newer unionfs support routines: node allocation/removal, per-thread open/readdir status, upper attribute synthesis, relookup helpers, shadow directory creation, whiteout lookup preparation, copy-up, rmdir emptiness checks, and diagnostic upper/lower vnode accessors.

## Public And Internal APIs Covered

- Node lifecycle: `unionfs_nodeget()`, `unionfs_noderem()`.
- Per-thread status: `unionfs_get_node_status()`, `unionfs_tryrem_node_status()`.
- Attribute synthesis: `unionfs_create_uppervattr_core()`, `unionfs_create_uppervattr()`.
- Relookup: internal `unionfs_relookup()`, public `unionfs_relookup_for_create()`, `unionfs_relookup_for_delete()`, `unionfs_relookup_for_rename()`.
- Upper creation/copy-up: `unionfs_mkshadowdir()`, internal `unionfs_node_update()`, internal `unionfs_vn_create_on_upper()`, internal `unionfs_copyfile_core()`, public `unionfs_copyfile()`.
- Whiteout and deletion checks: `unionfs_mkwhiteout()`, `unionfs_check_rmdir()`.
- Diagnostic accessors: `unionfs_checkuppervp()`, `unionfs_checklowervp()`.

## Control Flow And Behavior

- `unionfs_nodeget()` obtains a vnode with `vcache_get()` keyed by the selected backing vnode, references parent/upper/lower vnodes, allocates a `unionfs_node`, stores optional last-component path, sets vnode type and root flag, and initializes vnode size to zero.
- `unionfs_noderem()` clears backing vnode pointers, releases referenced vnodes and saved path, removes all per-thread status entries, and frees the node.
- `unionfs_get_node_status()` finds or creates a status record for the current process and LWP; `unionfs_tryrem_node_status()` frees it only when no upper or lower opens remain.
- `unionfs_create_uppervattr_core()` builds upper-layer attributes from a lower vattr according to transparent, masquerade, or traditional copy mode.
- `unionfs_relookup()` rebuilds a componentname and calls `relookup()` after temporarily unlocking the parent, returning a `PNBUF` that callers must release.
- `unionfs_mkshadowdir()` creates an upper directory mirroring lower attributes, updates the unionfs node to point at the new upper vnode, and then tries to set uid/gid/mode attributes.
- `unionfs_mkwhiteout()` currently performs create-style relookup and rejects existing targets; this version does not call `VOP_WHITEOUT()` directly after the relookup.
- `unionfs_vn_create_on_upper()` creates, opens, and write-counts a new upper file using the saved lower path and synthesized attributes.
- `unionfs_copyfile()` validates mount writability and parent state, creates an upper file, optionally copies file data from lower to upper, closes and decrements write count, resets attributes, and updates the node to point to the new upper vnode.
- `unionfs_copyfile_core()` performs buffered `VOP_READ()` / `VOP_WRITE()` loops with retrying partial writes.
- `unionfs_check_rmdir()` checks that a lower directory is empty modulo entries hidden by upper whiteouts or existing upper entries.

## State And Data Structures

- Uses `M_UNIONFSPATH` for saved path allocation.
- `unionfs_node_status` records open counts and readdir phase per process/LWP.
- Node update swaps in an upper vnode while the unionfs vnode is locked and lower vnode is exclusively locked.

## Dependencies

- NetBSD vnode cache, VOP create/mkdir/open/close/read/write/access/getattr/setattr/readdir/lookup, `relookup()`, componentname buffers, kauth credentials, and unionfs header definitions.

## Risks And Invariants

- `unionfs_nodeget()` allocates a new node after `vcache_get()` without an explicit hash cache like legacy union; correctness relies on vnode cache keying.
- Saved `un_path` is required for later copy-up and whiteout operations.
- Status records must be removed only after both upper and lower open counts drop to zero.
- Copy-up must not proceed if the mount, upper parent, or upper parent mount is readonly.
- `unionfs_mkwhiteout()` appears incomplete compared with legacy `union_mkwhiteout()` because it only validates name availability and returns without issuing a whiteout VOP.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_vfsops.c

## Scope

This file implements the newer unionfs VFS layer: mount, unmount, root, statvfs, quotactl/extattr stubs, sync/start/done hooks, rename-lock delegation, module attach/detach, sysctl setup/teardown, and `struct vfsops`.

## Public APIs And Operations

- Module declaration: `MODULE(MODULE_CLASS_VFS, unionfs, "layerfs")`.
- VFS functions: `unionfs_mount()`, `unionfs_unmount()`, `unionfs_root()`, `unionfs_quotactl()`, `unionfs_statvfs()`, `unionfs_sync()`, `unionfs_extattrctl()`, `unionfs_init()`, `unionfs_start()`, `unionfs_done()`.
- Rename lock forwarding: `unionfs_renamelock_enter()`, `unionfs_renamelock_exit()`.
- Operation vectors: `unionfs_vfsops`, `unionfs_vnodeopv_descs`.
- Module command handler: `unionfs_modcmd()`.

## Control Flow And Behavior

- `unionfs_mount()` rejects rootfs and update mounts, supports `MNT_GETARGS`, derives default uid/gid/mode from the covered vnode, interprets `UNMNT_ABOVE` vs `UNMNT_BELOW`, resolves the target path with `namei()`, and builds a `unionfs_mount`.
- Default copy mode is `UNIONFS_TRANSPARENT`; default whiteout mode is `UNIONFS_WHITE_ALWAYS`.
- For below mounts, the covered vnode becomes the upper writable layer and the target path becomes the lower layer.
- The mount copies upper readonly state, checks whiteout support for writable mounts, creates the unionfs root vnode with `unionfs_nodeget()`, sets locality and fsid, and formats `f_mntfromname`.
- `unionfs_unmount()` repeatedly calls `vflush()` to drain unionfs vnodes, handles forced close, then frees the mount structure.
- `unionfs_root()` returns a referenced and locked cached root vnode from `um_rootvp`.
- `unionfs_statvfs()` combines lower and upper space/file totals, using upper free counts and upper filesystem characteristics.
- `unionfs_quotactl()` delegates quota operations to the upper filesystem, though the vfsops table currently wires quotactl to `eopnotsupp`.
- `unionfs_extattrctl()` selects upper or lower filesystem based on the provided filename vnode’s active backing vnode, though the vfsops table wires extattrctl to `vfs_stdextattrctl`.
- `unionfs_done()` clears the global union readdir hook.
- Module init attaches VFS ops and creates the historical `vfs.union` sysctl node; module fini detaches and tears sysctl down.

## State And Data Structures

- Per-mount `struct unionfs_mount` contains lower, upper, and root vnodes, copy/whiteout policy, identity/mode policy, and mount operation.
- Sysctl state is tracked by `unionfs_sysctl_log`.
- `M_UNIONFSMNT` is the mount allocation type.

## Dependencies

- NetBSD pathbuf/namei, vnode locking, mount/module/sysctl infrastructure, VFS statvfs and rename-lock APIs, unionfs support routines, and layerfs module dependency.

## Risks And Invariants

- `UNMNT_REPLACE` is rejected in this implementation.
- A likely typo checks `upperrootvp->v_mount->mnt_flag & IMNT_MPSAFE` instead of `mnt_iflag`, affecting MP-safe flag propagation.
- Whiteout support is required on writable upper layers.
- The root vnode is held in `um_rootvp`; unmount depends on `vflush()` and reclaim to release nodes before the mount is freed.
- Some implemented functions are not wired in `unionfs_vfsops`, leaving their behavior unreachable through the table.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_vnops.c

## Scope

This file implements newer unionfs vnode operations: lookup, create/remove/rename, copy-up-on-write, open/close status tracking, access and attribute forwarding, directory iteration over upper and lower layers, symlink operations, locking, VM page forwarding, and the vnode operation vector.

## Public APIs And Operations

- Static vnode operation handlers include `unionfs_parsepath()`, `unionfs_lookup()`, `unionfs_create()`, `unionfs_whiteout()`, `unionfs_mknod()`, `unionfs_open()`, `unionfs_close()`, `unionfs_access()`, `unionfs_getattr()`, `unionfs_setattr()`, `unionfs_read()`, `unionfs_write()`, `unionfs_ioctl()`, `unionfs_poll()`, `unionfs_fsync()`, `unionfs_remove()`, `unionfs_link()`, `unionfs_rename()`, `unionfs_mkdir()`, `unionfs_rmdir()`, `unionfs_symlink()`, `unionfs_readdir()`, `unionfs_readlink()`, `unionfs_inactive()`, `unionfs_reclaim()`, `unionfs_print()`, `unionfs_lock()`, `unionfs_unlock()`, `unionfs_pathconf()`, `unionfs_advlock()`, `unionfs_strategy()`, `unionfs_kqfilter()`, `unionfs_bmap()`, `unionfs_mmap()`, `unionfs_abortop()`, `unionfs_islocked()`, `unionfs_seek()`, `unionfs_putpages()`, `unionfs_getpages()`, `unionfs_revoke()`.
- Operation vector: `unionfs_vnodeop_entries`, `unionfs_vnodeop_opv_desc`, exported `unionfs_vnodeop_p`.

## Control Flow And Behavior

- `unionfs_lookup()` resolves `".."` through the parent unionfs vnode, looks up upper and lower layers, honors whiteouts and opaque upper directories, creates shadow directories for lower-only directories on writable mounts, allocates unionfs vnodes with `unionfs_nodeget()`, and enters positive/negative cache records.
- `unionfs_create()`, `unionfs_mknod()`, `unionfs_mkdir()`, and `unionfs_symlink()` create entries in the upper directory and wrap resulting upper vnodes in unionfs nodes.
- `unionfs_open()` maintains per-thread open status. It copies lower regular files up on write opens, opens lower directories for readdir when upper directories are opened, and records upper/lower open counts.
- `unionfs_close()` chooses the backing vnode from open status, closes it, and closes the auxiliary lower readdir open when the upper directory open count reaches zero.
- `unionfs_access()` rejects writes on readonly mounts, checks synthesized shadow permissions for lower-only regular files/directories under non-transparent copy modes, and converts write access to lower read access because mutation would copy up.
- `unionfs_getattr()` prefers upper attributes, otherwise reads lower attributes and may synthesize uid/gid/mode for the future shadow object.
- `unionfs_setattr()` copies lower regular files up when needed, then forwards attributes to upper.
- `unionfs_read()` and `unionfs_write()` simply forward to upper if present, otherwise lower.
- `unionfs_ioctl()`, `unionfs_poll()`, and `unionfs_fsync()` select the open backing vnode from per-thread status; missing status returns `EBADF`.
- `unionfs_remove()` removes upper entries, setting `DOWHITEOUT` according to whiteout mode or lower presence, or creates a whiteout for lower-only entries.
- `unionfs_link()` is compiled as a panic stub (`panic("XXXAD")`), so hard links through unionfs are not implemented.
- `unionfs_rename()` maps unionfs source/target vnodes to upper-layer vnodes, copies up lower-only regular files or shadow-directories lower-only directories, redoes lookup state when copy-up occurred, marks source whiteout when lower exists, delegates to upper `VOP_RENAME()`, and purges directory caches on successful directory renames.
- `unionfs_rmdir()` checks lower directory emptiness when both layers exist, applies whiteout policy, removes upper directories, or creates a whiteout for lower-only directories.
- `unionfs_readdir()` requires prior open status, reads upper then lower streams, suppresses lower traversal if upper is opaque, tracks readdir phase in node status, and merges cookies.
- `unionfs_advlock()` copies lower-only files up before locking and reopens the upper vnode if the lower vnode had been open.
- `unionfs_lock()` and `unionfs_unlock()` lock/unlock lower then upper vnodes when both exist.
- VM operations forward getpages/putpages to active backing vnodes and require shared VM object locks.

## State And Data Structures

- Uses `struct unionfs_node` for upper/lower/parent vnode links and saved path.
- Uses `struct unionfs_node_status` for per-process/LWP open counts, lower open mode, readdir phase, and auxiliary lower-open flag.
- Readdir state values distinguish upper phase, transition, and lower phase.

## Dependencies

- Support routines from `unionfs_subr.c`, vnode/namecache/VOP APIs, genfs access/page helpers, specfs, kauth, UVM, buffer cache, and componentname relookup helpers.

## Risks And Invariants

- `unionfs_link()` panics if invoked, which is a hard correctness gap in the vnode table.
- `unionfs_readdir()` cookie merge code advances the destination pointer using byte counts against an `off_t *`, which is suspicious and may corrupt merged cookie layout.
- `unionfs_lock()` locks lower then upper without the legacy union retry-on-target-change logic, increasing sensitivity to lock ordering.
- Correct operation of ioctl/poll/fsync depends on per-thread open status being present and accurate.
- Lower-only writes should be prevented by open/copy-up flow, but `unionfs_write()` itself forwards to lower if no upper exists.
- Shadow and whiteout behavior depends on helper routines, including the incomplete-looking `unionfs_mkwhiteout()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/unionfs/unionfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/Makefile

## Scope

This makefile installs public V7FS headers.

## Build Behavior

- Sets `INCSDIR` to `/usr/include/fs/v7fs`.
- Installs `v7fs.h` and `v7fs_args.h` through `bsd.kinc.mk`.

## Dependencies And Role

- Depends on NetBSD kernel include install rules.
- Exposes V7 filesystem on-disk structures and mount arguments to kernel/userland consumers.

## Risks And Invariants

- Header install location is part of the public include contract for V7FS tooling and mount support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs.h

## Scope

This header defines the on-disk 7th Edition Unix filesystem format as used by NetBSD V7FS: scalar types, block geometry, superblock layout, free block/inode caches, directory entries, inode layout, and file type bits.

## APIs And Constants

- V7 scalar types: `v7fs_ino_t`, `v7fs_daddr_t`, `v7fs_time_t`, `v7fs_off_t`, `v7fs_dev_t`, `v7fs_mode_t`.
- Limits: `V7FS_DADDR_MAX`, `V7FS_INODE_MAX`.
- Block geometry: `V7FS_BSIZE`, `V7FS_BSHIFT`, `V7FS_ROUND_BSIZE()`, `V7FS_TRUNC_BSIZE()`, `V7FS_RESIDUE_BSIZE()`.
- Fixed sectors: `V7FS_BOOTBLOCK_SECTOR`, `V7FS_SUPERBLOCK_SECTOR`, `V7FS_ILIST_SECTOR`.
- Superblock layout: `struct v7fs_superblock`.
- Allocation constants and structures: `V7FS_MAX_FREEBLOCK`, `V7FS_MAX_FREEINODE`, `struct v7fs_freeblock`, `V7FS_DADDR_PER_BLOCK`.
- Directory entry format: `V7FS_NAME_MAX`, `V7FS_PATH_MAX`, `V7FS_LINK_MAX`, `struct v7fs_dirent`.
- Inode constants/layout: `V7FS_BALBLK_INODE`, `V7FS_ROOT_INODE`, `V7FS_MAX_INODE()`, `V7FS_INODE_PER_BLOCK`, `V7FS_ILISTBLK_MAX`, `struct v7fs_inode_diskimage`.
- Address indexes: `V7FS_NADDR`, direct count, single/double/triple index positions.
- File type mode bits: classic V7 types and NetBSD/BSD extensions for symlink, socket, and FIFO.

## Data Layout

- Filesystem uses 512-byte blocks.
- Sector 0 is boot block; sector 1 is superblock; sector 2 begins the inode list; data begins at `datablock_start_sector`.
- Inodes are 64-byte packed disk images with 13 three-byte block addresses stored in a 40-byte address array.
- Directory entries are 16 bytes: inode number plus 14-byte name.
- Superblock includes fixed-size free block and free inode caches, lock flags, modified/readonly state, update time, and total free counters.

## Dependencies

- Includes `<sys/types.h>` and `<inttypes.h>` outside the kernel.
- Uses host constants `PATH_MAX` and `LINK_MAX` for exported path/link maxima.
- Structures are `__packed` to match historical disk layout.

## Risks And Invariants

- On-disk fields must remain packed and fixed width; padding would corrupt disk format interpretation.
- V7 block addresses are 24-bit values packed into byte arrays, so consumers must encode/decode carefully.
- Maximum volume and file sizes are constrained by historical V7 address formats.
- BSD and NetBSD file type extensions are explicitly outside original V7 but supported by this header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_args.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_args.h

## Scope

This header defines the mount argument structure for NetBSD V7FS.

## API

- `struct v7fs_args` contains:
  - `char *fspec`: block special device holding the filesystem.
  - `int endian`: target filesystem endian setting.

## Dependencies And Role

- Guarded by `_FS_V7FS_V7FS_ARGS_H_`.
- Used by V7FS mount code and mount tooling to pass the device path and endian mode into the kernel.

## Risks And Invariants

- The structure is part of the mount ABI; field order and types must remain compatible with callers.
- Endianness is explicit because V7FS images may not match host byte order.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_args.h -->