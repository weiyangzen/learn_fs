# Group Research: group_1251_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nilfs_nilfs_subr_c_sour_5392ab92e748

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_subr.c

Implements core NILFS helper logic for block translation, segment-log reading, super-root discovery, raw node lifecycle, and directory lookup support.

Key points:
- Provides segment arithmetic helpers, metadata-file layout calculations, and a local little-endian CRC32 routine.
- `nilfs_bread()` maps logical file blocks through the NILFS btree, then special-cases metadata/system nodes by translating virtual blocks to physical device blocks through DAT.
- Btree lookup supports direct small maps and large btree maps, including recursive lookup through non-root btree nodes.
- `nilfs_mdt_trans()` maps metadata indexes into metadata-file block/entry locations; `nilfs_nvtop()` resolves virtual-to-physical blocks, with DAT itself treated as physically mapped.
- Mount recovery helpers scan segment summaries from the last partial segment, load/CRC-check super roots, and update in-memory superblock last-segment fields.
- Node allocation initializes `nilfs_node` locks and links to `nilfs_device` / `nilfs_mount`; disposal purges dirhash and destroys synchronization primitives.
- Directory lookup is backed by NetBSD `dirhash`: `dirhash_fill()` walks NILFS directory records, while `nilfs_lookup_name_in_dir()` verifies hash hits against disk directory entries.
- Mutation helpers are effectively read-only: update, resize, create, attach, and detach paths return `EROFS`; delete is empty.

Dependencies and interactions:
- Uses `nilfs_bswap.h` accessors for on-disk endian conversion.
- Reads through `bread()` on either `devvp` or the file vnode.
- Called by NILFS VFS mount code for super-root recovery and by vnode ops for lookup, bmap, strategy, and directory operations.

Risk/notes:
- The file is central to the read-only behavior of this NILFS implementation.
- Write/update hooks are placeholders; vnode operations that route here cannot persist changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_subr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_subr.h

Declares the private NILFS helper and vnode-operation interface shared by `nilfs_subr.c`, `nilfs_vfsops.c`, and `nilfs_vnops.c`.

Key contents:
- `VFSTONILFS()` mount-data cast macro.
- Prototypes for segment arithmetic, metadata layout calculation, CRC, segment-log reading, super-root search, block reading, btree lookup, and DAT translation.
- Prototypes for raw node lifecycle, time/update/resize helpers, directory lookup/create/delete/attach/detach helpers.
- Prototypes for all NILFS vnode operations exported by `nilfs_vnops.c`.

Role:
- This header is the internal NILFS subsystem contract.
- It exposes many mutation-oriented operations even though the corresponding implementations currently return `EROFS` or are stubs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_vfsops.c

Implements the NetBSD VFS layer for NILFS: module registration, mount/unmount, root vnode lookup, stat, vnode loading, and filesystem initialization.

Key points:
- Defines the `nilfs_vfsops` table for `MOUNT_NILFS` and module attach/detach.
- Initializes malloc types, global mounted-device list, and `nilfs_node_pool`.
- Provides genfs callbacks, including mark-update flag propagation; allocation is a no-op placeholder.
- Mount flow validates mount args, locates the block device, opens it, reads both NILFS superblocks, validates CRCs, chooses the newer valid spare if needed, calculates block/metadata constants, finds a super root, creates DAT/CPFILE/SUFILE nodes, selects a checkpoint, and builds the ifile node.
- Supports multiple read-only checkpoint mounts from one device and prevents duplicate checkpoint mounts; read-write mounting is constrained but real writing is not implemented.
- `nilfs_loadvnode()` resolves inode records from the checkpoint ifile, creates a `nilfs_node`, sets vnode type/op table, initializes genfs, marks root, and sets UVM size.
- `nilfs_vget()`, file-handle conversion, root-mount, and snapshot operations are unsupported or return `EOPNOTSUPP`.

Risk/notes:
- Mounting is functional for read-only checkpoint access.
- The code contains TODOs around write sessions, superblock writeout, roll-forward, and NFS/file-handle support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_vnops.c

Implements vnode operations for NILFS files and directories.

Key points:
- Lifecycle is mostly passive: `nilfs_inactive()` does little, while `nilfs_reclaim()` destroys genfs state and disposes the NILFS node.
- `nilfs_read()` validates vnode type and uses `ubc_uiomove()` against the vnode UVM object.
- `nilfs_vfsstrategy()` maps vnode buffers to device I/O through `nilfs_read_filebuf()`.
- `nilfs_read_filebuf()` translates logical blocks to virtual blocks, then virtual to physical blocks, issuing nested device buffers; holes are zero-filled.
- `nilfs_trivial_bmap()` returns NILFS virtual block mappings and contiguous run length; virtual block zero is returned as `-1` for holes.
- Directory operations include `nilfs_readdir()` for NILFS directory entries and `nilfs_lookup()` for `.`, `..`, namecache, dirhash-backed lookup, vnode-cache creation, and negative/create lookup behavior.
- Metadata ops map NILFS inode fields to `vattr`, use generic vnode authorization, and report NILFS pathconf limits.
- Mutation paths are not viable: `nilfs_write()` panics, strategy writes panic, create/mknod/mkdir/link/symlink/rename/remove/rmdir route to `EROFS` helpers or cannot succeed, and `readlink()` returns `EROFS`.

Risk/notes:
- The vnode table advertises many operations, but practical behavior is read-oriented.
- Write attempts are unsafe in some paths because they panic rather than returning an error.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/Makefile

Kernel include installation makefile for NTFS public headers.

Key contents:
- Installs headers under `/usr/include/ntfs`.
- Installs `ntfs.h`, `ntfs_inode.h`, and `ntfsmount.h`.
- Includes NetBSD `bsd.kinc.mk`.

Role:
- This is not the filesystem build file; it controls exported kernel/user-visible include installation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs.h

Defines core NTFS on-disk structures, mount state, constants, conversion hooks, and internal macros.

Key contents:
- On-disk format definitions for the boot sector, MFT file records, fixup headers, attributes, attribute lists, file-name attributes, index root/allocation entries, and attribute definitions.
- NTFS constants for system inode numbers such as `$MFT`, `$Volume`, `$AttrDef`, root, bitmap, boot, bad cluster, and upcase.
- Attribute type constants such as `$STANDARD_INFORMATION`, `$FILE_NAME`, `$DATA`, `$INDEX_ROOT`, and `$INDEX_ALLOCATION`.
- `struct ntfsmount` holds mount pointer, bootfile, device vnode/dev_t, pinned system vnodes, MFT record size, mount uid/gid/mode/flags, free-cluster count, loaded attribute definitions, and Unicode conversion callbacks.
- Macros convert clusters, bytes, blocks, mount/vnode/fnode pointers, and debug printing.

Role:
- Foundational NTFS header shared across VFS, vnode, and subroutine files.
- Mixes public-ish installed definitions with kernel-internal structures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_compr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_compr.c

Implements NTFS compression decompression for compressed attribute reads.

Key points:
- `ntfs_uncompblock()` decompresses one 4 KiB NTFS compression block.
- Handles uncompressed blocks by copying payload and zero-filling the rest.
- Handles compressed tag streams using back-reference offset/length pairs.
- `ntfs_uncompunit()` decompresses a full compression unit of 16 clusters by repeatedly calling `ntfs_uncompblock()`.

Dependencies:
- Uses `NTFS_COMPBLOCK_SIZE` and `NTFS_COMPUNIT_CL` from `ntfs_compr.h`.
- Used by `ntfs_readattr()` when an attribute has compression enabled and a compression algorithm set.

Risk/notes:
- The decoder assumes trusted kernel buffers and uses direct unaligned `u_int16_t` reads through `GET_UINT16`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_compr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_compr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_compr.h

Private kernel header for NTFS compression support.

Key contents:
- Rejects non-kernel inclusion.
- Defines `NTFS_COMPBLOCK_SIZE` as `0x1000`.
- Defines `NTFS_COMPUNIT_CL` as `16`.
- Declares `ntfs_uncompblock()` and `ntfs_uncompunit()`.

Role:
- Small internal interface between the NTFS attribute read path and the compression decoder.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_compr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_conv.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_conv.c

Provides UTF-8 filename conversion callbacks for NTFS.

Key points:
- `ntfs_utf8_wget()` decodes one UTF-8 character to NTFS `wchar` using NetBSD unicode helpers.
- `ntfs_utf8_wput()` encodes an NTFS wide character to UTF-8.
- `ntfs_utf8_wcmp()` compares two wide characters directly.

Role:
- These callbacks are installed into `ntfsmount` during mount.
- Used by lookup and readdir code to compare and emit NTFS Unicode names.

Limitations:
- UTF-8 only; alternate charset support is not implemented here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_ihash.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_ihash.c

Implements the in-core NTFS ntnode hash table.

Key points:
- Maintains a hash table keyed by device and inode number.
- `ntfs_nthashinit()` initializes global hash locks and table.
- `ntfs_nthashreinit()` rebuilds the hash table when vnode sizing changes.
- `ntfs_nthashdone()` frees table and destroys locks.
- `ntfs_nthashlookup()` returns a matching in-core `ntnode` without taking its per-node busy lock.
- `ntfs_nthashins()` inserts an ntnode and marks `IN_HASHED`.
- `ntfs_nthashrem()` removes an ntnode if currently hashed.

Interactions:
- Used by `ntfs_ntlookup()` / `ntfs_ntput()` in `ntfs_subr.c`.
- Coordinates with global `ntfs_hashlock` and local hash-table lock.

Risk/notes:
- Hash lookup itself does not acquire object lifetime ownership; callers handle locking/refcounting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_ihash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_ihash.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_ihash.h

Private kernel header for NTFS ntnode hash support.

Key contents:
- Rejects non-kernel inclusion.
- Declares `ntfs_hashlock`.
- Declares hash lifecycle and operations: init, reinit, done, lookup/get, insert/remove.

Note:
- The header declares `ntfs_nthashget()`, but this grouped file set only includes an implementation for lookup/insert/remove; no `ntfs_nthashget()` body appears in `ntfs_ihash.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_ihash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_inode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_inode.h

Defines NTFS in-memory node structures and file-handle layout.

Key contents:
- Inode-style flags for access/change/update state, locking, hashing, loaded attributes, and preloaded directory data.
- `struct ntnode` represents an NTFS MFT record and stores device vnode/dev_t, hash linkage, mount pointer, inode number, flags, lock/cv state, use/busy counters, loaded attribute list, link count, main record, and file-record flags.
- `struct ntkey` is the vnode-cache key combining inode number, attribute type, and variable-length attribute name.
- `struct fnode` represents a vnode-visible NTFS stream/attribute for an `ntnode`, including vnode pointer, associated ntnode, file-name metadata, size/allocation, key storage, and directory enumeration cache.
- `struct ntfid` is the file-handle format containing inode and attribute identifier.

Role:
- Separates MFT-record state (`ntnode`) from per-vnode attribute-stream state (`fnode`).
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_subr.c

Contains the main NTFS implementation helpers: ntnode loading/lifetime, attribute parsing, directory lookup/enumeration, attribute I/O, compression dispatch, fixups, and uppercase table management.

Key points:
- `ntfs_loadntnode()` reads an MFT record, applies multi-sector fixups, parses attributes, and builds the in-memory `ntvattr` list.
- `ntfs_attrtontvattr()` converts resident and nonresident attributes to internal form, expanding runlists for nonresident data.
- `ntfs_ntvattrget()` finds attributes by type/name/VCN and follows `$ATTRIBUTE_LIST` records when attributes live in extension records.
- `ntfs_ntlookup()` finds or allocates an `ntnode`, initializes locks, inserts into hash, and returns it busy/owned.
- `ntfs_ntget()`, `ntfs_ntput()`, `ntfs_ntref()`, and `ntfs_ntrele()` manage busy state and use counts.
- Unicode/ASCII comparisons use mount callbacks and the `$UpCase` table.
- `ntfs_ntlookupattr()` parses names containing NTFS alternate data stream syntax.
- `ntfs_ntlookupfile()` searches `$INDEX_ROOT:$I30`, descends into `$INDEX_ALLOCATION:$I30`, and can fall back to full-tree scan.
- `ntfs_ntreaddir()` reads index root entries first, then scans active index-allocation blocks based on `$BITMAP:$I30`; it caches the last enumeration position in `fnode`.
- `ntfs_readntvattr_plain()` reads resident data, nonresident run data, and sparse holes.
- `ntfs_readattr()` validates ranges and dispatches compressed reads through `ntfs_uncompunit()`.
- `ntfs_writentvattr_plain()` and `ntfs_writeattr_plain()` support in-place writes to nonresident attributes, but not resident attributes or extension past EOF.
- `ntfs_procfixups()` validates and applies NTFS update-sequence fixups.
- `ntfs_toupper_use()` loads `$UpCase` once globally and reference-counts it across mounts.

Risk/notes:
- This is legacy kernel filesystem code with many direct on-disk structure casts.
- Some write support exists for existing nonresident data, but allocation, truncation, creation, and metadata updates are not implemented in this grouped set.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_subr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_subr.h

Private NTFS helper header defining internal attribute state and helper prototypes.

Key contents:
- `struct ntvattr` represents one NTFS attribute extent.
- Stores vnode/ntnode pointers, type/name, compression state, data/allocation sizes, VCN range, attribute index, and either run arrays or resident attribute-specific pointers.
- Macros expose `ntvattr` union fields.
- Prototypes cover fixup processing, runlist parsing, plain and compressed attribute read/write paths, time conversion, directory lookup/enumeration, attribute conversion/loading/release, ntnode lookup/refcount/lifetime, `$UpCase` table lifecycle, and UTF-8 callbacks.

Role:
- Primary internal contract for `ntfs_subr.c`, VFS mount setup, and vnode ops.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vfsops.c

Implements NTFS VFS operations, module registration, mounting, unmounting, root/stat operations, vnode loading, and file-handle conversion.

Key points:
- Defines `ntfs_vfsops` for `MOUNT_NTFS`.
- Attaches malloc types, ntnode hash, and uppercase-table state during init.
- Registers an NTFS sysctl node during module init.
- `ntfs_mount()` validates args, handles `MNT_GETARGS`, rejects updates, opens the block device, and calls `ntfs_mountfs()`.
- `ntfs_mountfs()` invalidates old buffers, reads the boot block, validates NTFS signature and geometry, computes MFT record size, stores mount ownership/mode/flags, installs UTF-8 conversion hooks, and pins `$MFT`, root, and `$Bitmap` vnodes.
- Loads `$UpCase`, computes free clusters from `$Bitmap`, and reads `$AttrDef` into internal attribute-definition records.
- Unmount flushes non-system vnodes, checks pinned system vnode references, releases system vnodes, invalidates device buffers, closes the device, unuses `$UpCase`, and frees mount data.
- `ntfs_loadvnode()` takes an `ntkey`, loads the `ntnode` if needed, creates an `fnode`, fetches `$FILE_NAME` metadata, determines directory vs regular file, finds stream size/allocation, initializes genfs, and sets vnode identity.
- `ntfs_vgetex()` creates vnode-cache keys that include inode, attribute type, and attribute name.
- `ntfs_fhtovp()` and `ntfs_vptofh()` preserve inode and attribute identity.

Risk/notes:
- Mount update is unsupported.
- System vnodes are deliberately pinned to keep core NTFS metadata accessible.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vfsops.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vfsops.h

Private NTFS VFS header.

Key contents:
- Rejects non-kernel inclusion.
- Declares `ntfs_vgetex()` for fetching vnodes by inode plus attribute type/name.
- Declares `ntfs_calccfree()` for free-cluster calculation from `$Bitmap`.

Role:
- Small bridge from NTFS helper/vnode code back into VFS-level functionality.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vfsops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vnops.c

Implements NTFS vnode operations.

Key points:
- `ntfs_bmap()` is identity/no-op mapping for genfs.
- `ntfs_read()` bounds reads by `fnode` size and delegates to `ntfs_readattr()`.
- `ntfs_strategy()` handles buffer-cache reads through `ntfs_readattr()` and zero-fills partial EOF buffers; write strategy supports in-place writes but rejects file extension.
- `ntfs_write()` permits writes only within current file size and calls `ntfs_writeattr_plain()`.
- `ntfs_getattr()` synthesizes attributes from mount defaults, file-name timestamps, fnode size/allocation, and ntnode metadata.
- `ntfs_reclaim()` releases device vnode refs, destroys genfs state, frees `fnode` key/dir buffer, and releases/puts the ntnode.
- Access checks apply read-only mount restrictions for regular/dir/symlink writes and then use generic authorization with mount-wide uid/gid/mode.
- `ntfs_readdir()` emits synthetic `.` and `..`, then converts NTFS index entries to UTF-8 dirents and optional cookies.
- `ntfs_lookup()` handles namecache, `.`, `..`, parent lookup through `$FILE_NAME`, and normal directory search via `ntfs_ntlookupfile()`.
- `ntfs_fsync()` flushes vnode buffers, except `FSYNC_CACHE` returns `EOPNOTSUPP`.
- Pathconf reports NTFS limits.
- Vnode table wires creation/removal/link/rename/mkdir/rmdir/symlink/setattr/readlink to `genfs_eopnotsupp`.

Risk/notes:
- NTFS here is primarily read-oriented, but it has limited in-place write paths.
- Metadata-changing filesystem operations are intentionally unsupported.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfsmount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfsmount.h

Defines NTFS mount arguments and user-visible mount flags.

Key contents:
- `NTFS_MFLAG_CASEINS`: case-insensitive behavior.
- `NTFS_MFLAG_ALLNAMES`: expose all NTFS name variants.
- `struct ntfs_args` carries device path, compatibility padding, uid, gid, mode, and mount flags.
- `NTFS_MFLAG_BITS` provides the bit-description string.

Role:
- Installed public mount argument header used by mount tools and kernel NTFS mount code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/Makefile

Kernel include installation makefile for ptyfs.

Key contents:
- Installs headers under `/usr/include/fs/ptyfs`.
- Installs `ptyfs.h`.
- Includes NetBSD `bsd.kinc.mk`.

Role:
- Controls export of the ptyfs mount/header interface.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs.h

Defines ptyfs node types, mount arguments, in-memory node/mount state, and kernel helper prototypes.

Key contents:
- `ptyfstype` enum: `PTYFSpts` for slave side, `PTYFSptc` for controlling side, and `PTYFSroot` for filesystem root.
- `struct ptyfskey` is the vnode-cache key using node type and pty index.
- `struct ptyfsnode` stores hash linkage, key, file id, timestamp status, ownership/mode/flags, and timestamps.
- `struct ptyfsmount` stores mount lock, global mount-list linkage, mount pointer, gid/mode/flags, and active-pty bitmap.
- `struct ptyfs_args` is a versioned mount-argument structure containing gid, mode, and flags.
- Macros generate file numbers, construct devices, update timestamps, and cast mount/node pointers.
- Kernel prototypes cover active pty bitmap operations, vnode allocation, hash lifecycle, node lookup, timestamp update, root lookup, vnode ops, and VFS ops.

Role:
- Shared header for ptyfs VFS operations, subroutines, and vnode layer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_subr.c

Implements ptyfs node allocation/cache helpers and active-pty tracking.

Key points:
- `ptyfs_allocvp()` creates vnode-cache keys from type and pty number and calls `vcache_get()`.
- `ptyfs_hashinit()` creates a small global hash table and lock; `ptyfs_hashdone()` destroys them.
- `ptyfs_get_node()` returns or allocates a `ptyfsnode` by type/pty.
- New nodes get unique file numbers, permissions, ownership, status flags, timestamps, and hash linkage.
- Root gets directory-style read/execute permissions; pty nodes get character-device-style read/write permissions.
- `ptyfs_set_active()` grows the per-mount bitmap as needed and marks a pty active.
- `ptyfs_clr_active()` clears an active pty if present.
- `ptyfs_next_active()` scans for the next active pty at or after a given index.

Risk/notes:
- A comment documents a small race where duplicate unused list entries may be inserted when opening the master side concurrently through multiple mount points.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_vfsops.c

Implements ptyfs VFS operations and hooks pty allocation/name generation into the kernel pty subsystem.

Key points:
- Defines module and `ptyfs_vfsops` for `MOUNT_PTYFS`.
- Maintains a global list of ptyfs mounts and a mount count.
- Installs `ptm_ptyfspty` as the active pty handler on first mount and restores the previous handler on last unmount.
- `ptyfs__getmp()` selects a ptyfs mount visible from the caller’s root.
- `ptyfs__getpath()` computes a mount path adjusted for chroot visibility.
- `ptyfs__makename()` returns `/dev/null` for master-side names and mount-relative numeric slave paths for active slaves, with fallback to the previous handler where appropriate.
- `ptyfs__allocvp()` creates ptyfs vnodes for master/slave pty device requests and marks controlling ptys active.
- `ptyfs__getvattr()` supplies ownership/mode defaults for new pty nodes.
- Mount validates versioned `ptyfs_args`, handles `MNT_GETARGS`, rejects update mounts, allocates `ptyfsmount`, initializes lock and active bitmap state, sets local mount flag and statvfs info, inserts into the global mount list, and hooks the pty handler.
- Unmount flushes vnodes, restores the previous pty handler if this was the last ptyfs mount, removes the mount from the list, frees the bitmap, destroys the lock, and frees mount data.
- `ptyfs_loadvnode()` maps keys to root directory or character-device vnodes using `spec_node_init()`.
- Unsupported operations include `ptyfs_vget()`, file handles, snapshots, extattrs, and VFS fsync.
- Creates a VFS sysctl node for `ptyfs`.

Role:
- Mount/control-plane side of ptyfs; actual file operation behavior is in the ptyfs vnode layer outside this grouped file list.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/ptyfs/ptyfs_vfsops.c -->