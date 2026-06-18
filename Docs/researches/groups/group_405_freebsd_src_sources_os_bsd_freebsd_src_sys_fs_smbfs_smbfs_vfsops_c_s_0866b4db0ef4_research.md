# Group Research: group_405_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_smbfs_smbfs_vfsops_c_s_0866b4db0ef4

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/freebsd-src`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_vfsops.c

FreeBSD SMBFS VFS operation layer for mounting, unmounting, root lookup, quota stubs, initialization, and filesystem statistics.

Key responsibilities:
- Registers the `smbfs` VFS with `VFCF_NETWORK` and module dependencies on `netsmb`, `libiconv`, and `libmchain`.
- Exposes `vfs.smbfs.version` and writable `vfs.smbfs.debuglevel` sysctls.
- Converts legacy `smbfs_args` from `smbfs_cmount()` into nmount-style options after validating `SMBFS_VERSION`.
- Mounts an already-established netsmb session via the `fd` option, resolves it to an `smb_share`/`smb_dev`, stores a new `struct smbmount`, and synthesizes `f_mntfromname` as `//user@server/share`.
- Parses mount policy options for uid, gid, file mode, directory mode, case conversion, and long-name behavior.
- Creates and caches the root smbnode using `smbfs_smb_lookup(NULL, NULL, 0, ...)` and `smbfs_nget()`, marking the root vnode with `VV_ROOT`.
- Unmounts by repeatedly calling `vflush()` while parent references are being released, then drops the SMB share/device references and frees mount-private state.
- Initializes and destroys the global `smbfs_pbuf_zone` with `pbuf_zsecond_create()` and `uma_zdestroy()`.
- Implements `smbfs_statfs()` by delegating space queries to `smbfs_smb_statfs()` and using the VC transmit maximum as the I/O size.

Dependencies:
- VFS mount, vnode, sysctl, UMA, pbuf, module, and mount option infrastructure.
- netsmb session/share/device APIs: `smb_dev2share()`, `smb_share_unlock()`, `smb_share_lock()`, `smb_share_put()`, `sdp_trydestroy()`, `SSTOVC()`, and `smb_makescred()`.
- SMBFS node and subroutine helpers: `VFSTOSMBFS`, `smbfs_nget()`, `smbfs_smb_lookup()`, `smbfs_smb_statfs()`, and SMB credential allocation/free helpers.

Notable risks:
- Mount depends on a userspace-provided session file descriptor; option validation and lifetime transfer through `smb_dev2share()` are critical.
- Error paths must keep `smb_share`, `smb_dev`, `smbmount`, and SMB credential lifetimes balanced.
- `smbfs_unmount()` relies on `sm_didrele` progress to resolve child-to-parent vnode references; incorrect release accounting could leave busy mounts.
- `f_mntfromname` construction uses bounded `strncpy()` and pointer arithmetic; truncation is intended but must avoid overruns.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_vnops.c

SMBFS vnode operation implementation for access checks, open/close, attributes, file I/O, namespace operations, directory reads, pathconf, strategy I/O, DOS extended attributes, byte-range locking, and lookup/namecache behavior.

Key responsibilities:
- Defines and registers `smbfs_vnodeops`, including access, open, close, getattr, setattr, read, write, create, remove, rename, mkdir, rmdir, readdir, strategy, lookup, pathconf, advisory locking, and DOS attribute extended-attribute reads.
- Synthesizes Unix access control from mount uid/gid plus configured file/dir mode and rejects writes to regular files, directories, and symlinks on read-only mounts.
- Opens regular files over SMB with `DENYNONE` sharing, preferring read-write handles on writable mounts and falling back to read-only opens when needed; directories are locally marked open.
- Invalidates buffers and attributes when cached modification times show server-side changes or local writes changed data.
- Implements `getattr()` through the SMBFS attribute cache, refreshing with `smbfs_smb_lookup()` on cache miss and preserving open-file local size.
- Implements `setattr()` for file truncation, DOS readonly/hidden/system/archive flag mapping, mode-to-readonly mapping, and timestamp updates through dialect/capability-specific SMB calls.
- Implements create, mkdir, remove, rmdir, and rename by issuing SMB create/delete/mkdir/rmdir/rename calls, then updating vnode/name caches and node `NGONE`/`NMODIFIED` flags.
- Leaves hard links, symlinks, and mknod unsupported with `EOPNOTSUPP`.
- Routes regular-file and directory reads through `smbfs_readvnode()` and writes through `smbfs_writevnode()`.
- Implements pathconf answers for max file size bits, name length, path length, truncation behavior, and hidden/system support based on SMB capabilities.
- Provides local-plus-remote advisory lock behavior: validates `flock` ranges, uses `lf_advlock()` locally, and mirrors set/unlock operations through `smbfs_smb_lock()`.
- Validates SMB path components, including backslash rejection and 8.3-era bad character/name length rules for old LANMAN dialects.
- Implements lookup with namecache integration, stale vnode type detection, dot/dotdot handling with mount busying, create/rename/delete last-component semantics, and `smbfs_nget()` vnode instantiation.
- Exposes the `dosattr` extended attribute as a six-character string representing readonly, hidden, system, volume, directory, and archive bits.

Dependencies:
- FreeBSD vnode operation, namecache, lockf, buffer, VM object, and directory lookup infrastructure.
- SMBFS node/mount state: `struct smbnode`, `struct smbmount`, `NOPEN`, `NMODIFIED`, `NGONE`, size/mtime/DOS attribute fields, parent references, and directory search sequence state.
- SMB wire helpers for open, close, lookup, create, delete, mkdir, rmdir, rename, set size, set attributes/times, read/write strategy I/O, and SMB byte-range locks.

Notable risks:
- Local Unix permissions are synthesized and do not necessarily match server ACL enforcement; the server remains authoritative.
- `setattr()` has several dialect-specific timestamp and attribute paths, including Win95 and non-NT-SMB behavior.
- `remove()` refuses open or multiply referenced regular vnodes, which avoids deleting active SMB nodes but differs from POSIX unlink semantics.
- Rename deletes the destination before renaming the source in the common path, so failure after deletion is not atomic.
- Lookup correctness depends on cache invalidation when server-side type changes are detected.
- Directory locking is not supported over SMB and returns `EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs.h

Internal kernel header for FreeBSD tarfs, a read-only filesystem backed by a tar archive with optional decompression and sparse-file block maps.

Key responsibilities:
- Declares tarfs malloc types, sysctl root, and core forward declarations.
- Defines `struct tarfs_node`, the in-memory node representation for directories, regular files, symlinks, device nodes, FIFOs, and hard-link aliases.
- Stores per-node attributes including inode, type, archive offset, logical/physical sizes, name, owner/group/mode, flags, link count, timestamps, generation, parent, vnode pointer, and block map.
- Defines directory state as an ordered `TAILQ` plus cached readdir cookie/node, symlink target state, device `rdev`, and regular-file hard-link target pointer.
- Defines `struct tarfs_blk` sparse map entries with physical input offset, logical output offset, and length.
- Defines decompression support structures: fixed-size `tarfs_zbuf`, mount-level `tarfs_zio`, zstd state pointer, input/output positions, and compression-frame index.
- Defines `struct tarfs_mount`, holding all nodes, root, backing vnode, VFS mount, inode allocator, I/O sizing, stat counters, archive mtime, and optional decompression vnode.
- Defines tarfs file handles for NFS export support using length, generation, and inode.
- Provides lock macros, tar block sizing/alignment macros, preferred I/O-size tuning constants, reserved inode values, directory cookie constants, and the debug `.tar` znode name.
- Declares node allocation, block-map loading, lookup, read, I/O init/fini/read, buffer read, and file-flag parsing helpers.

Dependencies:
- FreeBSD kernel-only types and facilities: vnodes, mounts, component names, malloc types, sysctls, mutexes, TAILQ, device numbers, file ids, and vnode operation vectors.
- `tarfs_vnodeops` is defined in `tarfs_vnops.c`; I/O and decompression functions are implemented in `tarfs_io.c`; archive parsing and mount operations are in `tarfs_vfsops.c`.

Notable risks:
- `TARFS_ALLNODES_LOCK(tnp)` and unlock macros take a parameter named `tnp` but reference `tmp`; call sites rely on a visible `tmp` variable.
- Hard links are represented through `other` pointers and adjusted link counts, so teardown must avoid double-freeing shared file data.
- Sparse block-map correctness is central to read behavior and `bmap`/readahead hints.
- Reserved inode numbers for root and decompression znode must not collide with allocated archive node inodes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_dbg.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_dbg.h

Compile-time optional debug logging header for tarfs.

Key responsibilities:
- Declares `tarfs_debug` when `TARFS_DEBUG` is enabled.
- Defines bitmask categories for allocation, checksum, filesystem, lookup, vnode, I/O, decompression I/O, decompression index, sparse map, and bounce-buffer diagnostics.
- Provides `TARFS_DPF(category, fmt, ...)` and conditional `TARFS_DPF_IFF(category, cond, fmt, ...)` macros that print only when the matching category bit is enabled.
- Compiles both macros to no-ops when `TARFS_DEBUG` is not enabled.

Dependencies:
- Kernel-only header guarded by `_KERNEL`.
- Runtime sysctl exposure of `tarfs_debug` is in `tarfs_subr.c`.

Notable risks:
- Debug macro category names are concatenated into `TARFS_DEBUG_<category>`, so all call sites must use exactly one of the defined suffixes.
- Debug-only expression arguments are not evaluated in non-debug builds; side effects must never be placed in debug macro arguments.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_dbg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_io.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_io.c

Tarfs backing-file I/O and optional zstd decompression layer, including a synthetic vnode used to expose the decompressed byte stream internally.

Key responsibilities:
- Defines debug-only decompression sysctls and counters for inflated, consumed, and bounced bytes, plus a reset handler.
- Defines allocator hooks for zstd decompression state when `ZSTDIO` is compiled in.
- Implements `tarfs_io_read()` to read either the raw backing vnode or the decompressed synthetic znode, applying vnode range locks and vnode locks as needed.
- Implements `tarfs_io_read_buf()` for kernel-buffer reads using a one-element `uio`.
- Detects archive compression signatures for xz, gzip/zlib, and zstd; only zstd is supported when `ZSTDIO` is enabled, while xz and zlib return `EOPNOTSUPP`.
- Maintains a decompression frame index mapping compressed input offsets to decompressed output offsets, allowing zstd stream reset/skip for backward or far-forward reads.
- Implements znode vnode operations: read-only access delegation to the backing vnode, synthesized attributes, zstd-backed reads, reclaim cleanup, and strategy reads into buffers.
- Implements `tarfs_zread_zstd()` with input buffering, optional user-space bounce buffer, stream reset, frame-boundary indexing, EOF/error detection, and counter updates.
- Creates the synthetic znode in `tarfs_zio_init()` with inode `TARFS_ZIOINO` and operation vector `tarfs_znodeops`.
- Tears down znode, zstd stream, index, and zio allocation in `tarfs_io_fini()`.

Dependencies:
- FreeBSD vnode locking, range locking, `VOP_READ`, `VOP_GETATTR`, buffer strategy, sysctl, counter, malloc, and UIO APIs.
- Optional in-kernel zstd library through `contrib/zstd/lib/zstd.h`.
- Tarfs mount fields `vp`, `znode`, `zio`, `iosize`, `root`, and debug macros.

Notable risks:
- Decompression is stateful and serialized by taking the znode lock exclusively for non-raw reads.
- Random access before the current decompressed position requires stream reset to the nearest recorded frame index; indexing quality affects performance.
- Non-kernel-space reads allocate a full-length bounce buffer, which can be expensive for large reads.
- Error paths reset zstd state and current index to the first entry to recover from failed decompression.
- xz and zlib magic are detected but unsupported despite a module dependency on xz elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_subr.c

Tarfs support routines for sysctl tuning, node lookup/allocation/freeing, sparse block-map loading, file reads through sparse maps, and tar file flag parsing.

Key responsibilities:
- Defines malloc types for tarfs names and sparse block maps.
- Creates `vfs.tarfs` sysctl node, tunable `vfs.tarfs.ioshift`, and optional debug mask sysctl.
- Clamps preferred I/O shift between tar block size and page size, with zero mapping back to the default.
- Implements directory name lookup using the node's child `TAILQ`, with hard-link following for regular nodes whose `other` pointer is set.
- Implements directory cookie lookup with a one-entry readdir cache and a linear scan by inode cookie.
- Allocates nodes for directories, symlinks, regular files, FIFOs, block devices, and character devices, initializing attributes, generation, timestamps, block maps, names, parent links, and all-node list membership.
- Maintains parent directory contents, sizes, and link counts when inserting child nodes.
- Loads GNU sparse file block maps stored in file data: reads map blocks, parses entry count and offset/length pairs, validates alignment, ordering, and physical/logical bounds, and replaces the dummy block map.
- Frees nodes with type-specific cleanup for hard-link targets, parent directory references, symlink target buffers, names, block maps, and allocated inode numbers.
- Implements sparse-aware file reads by copying zeroes for holes and delegating actual data extents to `tarfs_io_read()`.
- Parses comma-separated file flags such as `nodump`, `uchg`, `uappnd`, `opaque`, `arch`, `schg`, and related names for PAX `SCHILY.fflags`.

Dependencies:
- Tarfs structures from `tarfs.h`, debug macros, kernel malloc, vnode/mount/namei types, sysctl, timestamps, `zero_region`, UIO, and inode number allocator APIs.
- `tarfs_io_read_buf()` and `tarfs_io_read()` for reading sparse maps and file content.

Notable risks:
- Sparse map parsing reads incrementally until enough newlines are present; malformed maps must not trigger unbounded allocation beyond the archive member size.
- The map parser uses signed `strtol()` into `long` before assigning offsets/lengths; overflow and negative values are rejected but remain sensitive to host limits.
- `tarfs_read_file()` must correctly advance both caller `uio` and local residuals across holes and data extents.
- Node freeing uses link counts to avoid freeing hard-linked data early; incorrect link accounting can leak or double-free nodes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_vfsops.c

Tarfs VFS mount, unmount, archive parser, vnode lookup by inode, file-handle conversion, and statfs implementation.

Key responsibilities:
- Defines POSIX ustar header layout and validates that it is exactly one 512-byte tar block.
- Defines tar type flags, ustar/GNU magic constants, default directory mode, mount options, malloc types, and read-only VFS registration.
- Parses tar numeric fields as signed octal or base-256 two's complement values.
- Verifies tar headers using both standard unsigned and legacy signed checksum calculations.
- Resolves archive paths in the in-memory node tree, optionally creating missing ancestor directories while rejecting invalid `..` traversal above root.
- Frees complete mount state by walking all nodes, finalizing I/O/decompression, deleting the inode allocator, clearing `mnt_data`, and freeing the mount object.
- Parses archive entries in `tarfs_alloc_one()`, including POSIX extended headers, path/linkpath/size overrides, GNU sparse metadata, SCHILY file flags, prefix/name concatenation, hard links, symlinks, device nodes, directories, and regular files.
- Rejects unsupported or malformed formats, including GNU tar magic, invalid checksums, invalid numeric fields, duplicate non-directory entries, unsupported entry types, and inconsistent sparse metadata.
- Allocates mount state from a regular backing vnode, initializes I/O/decompression, creates the root node, then walks all archive headers to populate the tree.
- Implements `tarfs_mount()` with `from`, optional display name `as`, root uid/gid/mode overrides for privileged callers, optional `verify` open flag, source vnode open/close, permission checks, read-only/local mount flags, fsid assignment, and mounted-from string.
- Implements forced/non-forced unmount using `vflush()`, source vnode close, and mount cleanup.
- Implements root vnode lookup through `VFS_VGET()` and marks it `VV_ROOT`.
- Reports `statfs` data from archive block count, preferred I/O size, node count, and zero free space/files.
- Implements `tarfs_vget()` using `vfs_hash_get()`/`vfs_hash_insert()`, all-node inode lookup, znode special case, vnode construction, mount queue insertion, and tarfs vnode op assignment.
- Implements NFS export file-handle conversion through inode and generation checks.

Dependencies:
- FreeBSD VFS, vnode, namei, sbuf, mount option, privilege, GEOM/VFS, malloc, mutex, UIO, stat, and file open/close infrastructure.
- Tarfs node/I/O helpers and `tarfs_vnodeops`.

Notable risks:
- Archive parsing is intentionally strict; many non-POSIX or GNU tar cases return `EINVAL`/`EFTYPE`.
- Extended header parsing mutates the header buffer by writing NUL terminators into line/key separators.
- Hard links are only accepted to existing regular file nodes that are not themselves hard-link aliases.
- The mount parser unlocks the backing vnode inside `tarfs_alloc_mount()` and later relies on caller cleanup paths knowing whether it is locked.
- `tarfs_vget()` linearly scans all nodes on vnode cache miss, which is simple but can be costly for large archives.
- `tarfs_fhtovp()` rejects stale handles by checking inode range, generation, mode, and link count.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_vnops.c

Tarfs vnode operation implementation for read-only archive nodes, including lookup, readdir, regular reads, symlink reads, buffer strategy, file handles, and attributes.

Key responsibilities:
- Registers `tarfs_vnodeops` with access, bmap, cached lookup, open, close, getattr, read, readdir, readlink, reclaim, strategy, print, and vptofh operations.
- Allows opening regular files and directories, creates VM objects sized to the tarfs node, and rejects other vnode types.
- Enforces read-only semantics by rejecting writes to regular files, directories, and symlinks while using `vaccess()` for ordinary permission checks.
- Implements `bmap()` for logical block mapping and run-ahead/run-behind hints based on sparse block extents and holes.
- Synthesizes vnode attributes from `struct tarfs_node`, including fileid, generation, flags, device number, rounded physical byte count, and timestamps.
- Implements cached lookup for `.`, `..`, ordinary entries, and debug-only root `.tar` znode access; non-last path components must be directories or symlinks.
- Uses `VFS_VGET()` and `vn_vget_ino()` to instantiate lookup targets and populates the namecache when allowed.
- Generates `.` and `..` directory entries, then iterates child `TAILQ` entries using inode cookies and per-directory last-cookie cache.
- Supports NFS directory cookies by returning an array of next offsets that matches emitted entries.
- Reads regular files through `tarfs_read_file()` until EOF or no progress, clipping reads to node logical size.
- Reads symlinks directly from the immutable stored link target.
- Reclaims vnodes by removing them from the VFS hash and clearing the node-vnode backpointer.
- Implements buffer strategy reads by constructing a kernel `uio`, clipping to EOF, and calling `tarfs_read_file()`.
- Encodes file handles using inode and generation.

Dependencies:
- FreeBSD vnode operation framework, namecache, `struct dirent`, UIO, buffer strategy, vnode hash, FIFO print helper, and VFS inode lookup.
- Tarfs node tree, block maps, directory cookies, sparse read helper, and file-handle structure.

Notable risks:
- Directory cookies are inode numbers plus reserved values; correctness depends on stable node inodes during mount lifetime.
- `tarfs_readdir()` uses a per-directory single-entry cache and assumes coherent directory traversal under vnode locking.
- `bmap()` and strategy must handle holes consistently with `tarfs_read_file()` zero-fill behavior.
- The debug-only `.tar` znode path exposes the decompressed archive stream at the root when `TARFS_DEBUG` is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tarfs/tarfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs.h

Core tmpfs internal header defining directory entries, nodes, mount state, file handles, cookies, locking rules, helper prototypes, and conversion helpers.

Key responsibilities:
- Defines tmpfs VM object flags `OBJ_TMPFS` and `OBJ_TMPFS_VREF` for identifying tmpfs-backed pager objects and vnode references from writable mappings.
- Defines `struct tmpfs_dirent`, which can be a normal RB-tree entry, a synthetic duplicate-hash head, or a duplicate entry on linked lists.
- Defines directory cookie values and bit flags for `.`, `..`, EOF, normal hash cookies, duplicate cookies, and duplicate-head markers.
- Defines extended attribute records with namespace, name, value, and size.
- Defines `struct tmpfs_node`, including inode id, type, attach state, status/access bits, size, attributes, generation, vnode association state, node interlock, refcount, extended attributes, and type-specific union.
- Documents lock ownership for node fields across vnode locks, node interlock, mount all-node lock, and VM object lock.
- Defines type-specific node state for device numbers, directory parent/RB tree/duplicate index/readdir cache/whiteout size, symlink target/SMR allocation flag, and regular-file anonymous VM object/page accounting.
- Defines vnode state bits for allocation, waiters, doomed nodes, and reclaim waits.
- Defines `struct tmpfs_mount`, including max size/pages, pages used, root node, node limit, inode allocator, node count, EA memory accounting, refcount, max file size, used-node list, all-node lock, read-only flag, namecache disable flag, mmap mtime policy, and page-cache read mode.
- Defines packed NFS file-handle data and directory cursor state.
- Declares tmpfs support functions for node/vnode/dirent allocation, directory lookup/iteration, whiteouts, resizing, hole punching, attribute changes, timestamps, memory accounting, init/uninit, and extended attribute cleanup.
- Provides inline conversion helpers from VM objects, mounts, and vnodes to tmpfs objects, plus `tmpfs_use_nc()` and lazy getattr timestamp update.

Dependencies:
- FreeBSD kernel queue/RB tree primitives, malloc declarations, vnode/mount/VM object types, namecache symlink storage, SMR vnode data loading, and tmpfs vnode/fifo operation implementations.

Notable risks:
- Directory cookies are only 31-bit compatible for normal entries and use special duplicate-cookie ranges; collision handling must preserve stable readdir restart behavior.
- Regular-file data is represented by a VM object, so page accounting crosses VFS and VM subsystem boundaries.
- Symlink target storage may be namecache/SMR-backed or malloc-backed; destruction must match the allocation path.
- Node/vnode bidirectional association is protected by `tn_interlock` and state bits; races here affect vnode aliasing and reclaim safety.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_fifoops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_fifoops.c

Tmpfs vnode operation vector specialization for named pipes.

Key responsibilities:
- Implements `tmpfs_fifo_close()` to mark the tmpfs node accessed, update timestamps, then delegate close behavior to `fifo_specops.vop_close`.
- Defines `tmpfs_fifoop_entries`, using `fifo_specops` as the default operation vector while overriding close, reclaim, access, getattr, setattr, pathconf, print, add-writecount, and fast-path lookup handlers.
- Registers the FIFO vnode operation vector with `VFS_VOP_VECTOR_REGISTER`.

Dependencies:
- Tmpfs node conversion and timestamp helpers from `tmpfs.h`.
- Tmpfs generic vnode operations from `tmpfs_vnops.h`.
- FreeBSD FIFO special vnode operations `fifo_specops`.

Notable risks:
- FIFO operations are mostly delegated, so tmpfs-specific metadata updates must happen in the few overridden hooks.
- Fast-path lookup execute/symlink operations return `VOP_EAGAIN`, forcing fallback to locked lookup paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_fifoops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_fifoops.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_fifoops.h

Kernel-only declaration header for tmpfs FIFO vnode operations.

Key responsibilities:
- Enforces kernel-only inclusion.
- Includes generic tmpfs vnode operation declarations.
- Declares the external FIFO vnode operation vector `tmpfs_fifoop_entries`.

Dependencies:
- `fs/tmpfs/tmpfs_vnops.h` for shared tmpfs vnode operation declarations.

Notable risks:
- This header is intentionally small but is part of the vnode operation wiring for FIFO nodes allocated in tmpfs.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_fifoops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_subr.c

Tmpfs support implementation for the VM pager integration, memory accounting, node lifecycle, vnode lifecycle, directory indexing, readdir, whiteouts, resizing/hole punching, attribute mutation, timestamps, and initialization.

Key responsibilities:
- Creates `vfs.tmpfs` sysctls and tunables for reserved memory and percent of available memory usable by unlimited tmpfs mounts.
- Defines tmpfs directory-entry malloc type, UMA node pool, VFS SMR zone use, and dynamic VM pager type.
- Implements a tmpfs pager backed by swap objects, with callbacks for allocation, writable mapping count changes, vnode lookup, free-space accounting, page insert/remove accounting, and page-allocation admission.
- Maintains `tm_pages_used` and per-node `tn_pages` as swap/page cache state changes through pager callbacks.
- Keeps vnodes with writable mappings referenced and on the lazy list so mmap writes can update mtimes.
- Initializes and tears down the dynamic pager type and UMA node zone in `tmpfs_subr_init()` and `tmpfs_subr_uninit()`.
- Computes available memory from swap plus free pages minus a reserved threshold, and checks per-mount page limits through `tmpfs_pages_check_avail()`.
- Allocates tmpfs nodes for all supported vnode types, including parent link handling for directories, SMR-safe symlink storage, and regular-file VM object creation with tmpfs backpointers.
- Frees nodes with reference counting, detach/list removal, extended attribute cleanup, VM object flag clearing/accounting, symlink storage cleanup, mount refcount release, and SMR UMA free.
- Allocates and frees dirents, updating target node link counts.
- Allocates/reuses vnodes for nodes with `tn_vpstate` coordination, handles existing/doomed/allocating vnode races, attaches regular-file VM objects to vnodes, swaps FIFO vnode ops, and inserts vnodes into the mount queue.
- Destroys vnode-object association for reclaimed or failed vnodes, including clearing `OBJ_TMPFS_VREF` references created by writable mappings.
- Allocates new filesystem objects by creating a node, dirent, vnode, and finally attaching the dirent atomically to the parent directory.
- Implements RB-tree directory iteration with collision lists for duplicate hash cookies and a sorted duplicate index.
- Implements directory lookup by name/hash, duplicate-cookie lookup for readdir restart, attach/detach with duplicate-head conversion, and full directory destruction.
- Generates `.` and `..` dirents and emits real entries with stable `d_off` cookies, whiteout handling, readdir cache updates, access timestamp marking, and optional NFS cookie arrays.
- Implements whiteout add/remove/clear support for union mounts.
- Implements regular-file resize/truncate by zeroing partial pages, removing full pages, changing VM object size, and updating node size.
- Implements hole punching by zeroing partial boundary pages and removing full pages while returning adjusted offset/length.
- Detects dirty mmap writes by comparing VM object generation and clean generation, marking nodes modified/changed.
- Implements chflags, chmod, chown, chsize, chtimes, timestamp syncing, access/status marking, and final truncation wrapper with read-only, immutable, append-only, privilege, securelevel, and rlimit checks.
- Generates the directory RB-tree comparator and implementation.

Dependencies:
- FreeBSD VM pager, swap pager, VM object/page, vnode, mount, SMR, UMA, sysctl, random harvesting, namecache, privilege, securelevel, UIO, dirent, whiteout, and lock/refcount APIs.
- Tmpfs VFS and vnode state from `tmpfs.h`, FIFO vnode ops, and generic tmpfs vnode ops.

Notable risks:
- Pager callbacks and vnode lifecycle code cross VM/VFS locking domains; lock ordering and reference handoff are critical.
- Writable mmap tracking keeps extra vnode references through `OBJ_TMPFS_VREF`; forced unmount and reclaim paths must clear them.
- Directory cookie collision handling is intricate: normal RB entries can become duplicate heads, duplicate entries receive separate cookie values, and readdir restart depends on both RB and duplicate-index state.
- `tmpfs_free_node_locked()` may unlock the mount while deallocating VM objects, so callers must respect its boolean return contract.
- Mount/node refcounts let VM objects outlive the mount after unmount; page accounting must remain valid until the final object is gone.
- Timestamp updates are lazy and can be triggered by getattr/sync/mmap dirty generation checks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vfsops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vfsops.c

Tmpfs VFS operation implementation for mount/remount, unmount, root lookup, NFS file handles, statfs, sync, module init/uninit, and DDB diagnostics.

Key responsibilities:
- Defines tmpfs mount option names for size, max file size, inode count, uid/gid/mode, extended attribute memory, namecache policy, mmap mtime policy, symlink following, page-cache read mode, and union/export options.
- Implements lazy and full mmap mtime update scans over mount vnodes.
- Scans all process VM maps to find tmpfs writable mappings for a mount and optionally revoke write protections by clearing `VM_PROT_WRITE` and calling `pmap_protect()`.
- Converts a read-write tmpfs mount to read-only by suspending writes, checking writable mappings, setting mount/tmpfs read-only state, revoking writable mappings in forced mode, updating mtimes, and flushing vnodes.
- Handles remounts by rejecting changes to fixed parameters such as uid/gid/mode, inode limit, size, max file size, nonc, and pgread, while allowing `easize`, `nomtime`, and RO/RW transitions.
- Computes default mount size, page limit, and inode limit from available memory/swap, explicit options, and per-page node density.
- Initializes `struct tmpfs_mount`, inode allocator, root node, mount flags, fast-lookup flags, filesystem id, mount-from string, and name length.
- Unmounts by suspending writes, flushing vnodes until empty or returning `EBUSY`, destroying remaining directory contents/nodes under the all-node lock, clearing `mnt_data`, freeing mount state, and resuming writes.
- Frees mount structures only when the mount refcount drops to zero; VM objects may outlive unmount, so page-used count is not asserted at final mount free.
- Implements cached root lookup through `tmpfs_alloc_vp()`.
- Implements NFS file-handle to vnode conversion by matching inode and generation in the used-node list and taking a transient node reference.
- Reports statfs blocks from page limits/current memory availability and files from node limits/current node count.
- Implements sync handling for suspend state and lazy mtime updates.
- Initializes tmpfs support via `tmpfs_subr_init()` and installs tmpfs file close operation wrapper into `tmpfs_fnops`; uninitializes through `tmpfs_subr_uninit()`.
- Registers tmpfs as a jail-allowed VFS with root/statfs/fhtovp/sync/init/uninit operations.
- Provides DDB `show tmpfs` output for mount memory, inode, extended attribute, refcount, size, read-only, namecache, and mtime policy state.

Dependencies:
- FreeBSD VFS mount/update/unmount, vnode traversal, write suspension, allproc/proc/vmspace locking, VM map entries, pmap protection, jail/VFS flags, DDB, and tmpfs support APIs.
- Tmpfs root/node allocation, vnode allocation, directory destruction, memory accounting, and file operation wrappers from `tmpfs_subr.c`.

Notable risks:
- RW-to-RO remount touches process address spaces system-wide; races are controlled through process/vmspace references and VM map locks.
- Forced RO conversion can revoke write permissions from existing mappings, which may surprise mapped writers but is required to complete the transition.
- Unmount must coordinate VFS write suspension with node destruction so no concurrent creator can attach new nodes.
- File-handle lookup is linear over used nodes and returns `EINVAL` for stale/missing handles rather than `ESTALE`.
- `tmpfs_free_tmp()` allows lingering VM objects after unmount, so mount lifetime is tied to regular-file object references.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs_vfsops.c -->