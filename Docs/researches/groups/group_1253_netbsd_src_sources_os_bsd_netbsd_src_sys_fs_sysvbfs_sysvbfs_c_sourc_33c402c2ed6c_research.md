# Group Research: group_1253_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_sysvbfs_sysvbfs_c_sourc_33c402c2ed6c

Scope checked against `Docs/research_subset_a.md`; all files are under `sources/os/bsd/netbsd-src`, which is included in subset A. Every listed source file was read completely and summarized separately below.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs.c

Read completely: 154 lines.

This is the sysvbfs VFS module registration and vnode/VFS operation table file. It declares `MODULE(MODULE_CLASS_VFS, sysvbfs, NULL)`, the `sysvbfs_vnodeop_entries` dispatch table, the `sysvbfs_genfsops` table, and the `sysvbfs_vfsops` table used by `vfs_attach`.

The vnode table wires the flat BFS-backed implementation to NetBSD vnode operations: lookup/create/open/close/access/getattr/setattr/read/write/fsync/remove/rename/readdir/inactive/reclaim/bmap/strategy/print/advlock/pathconf come from sysvbfs-specific code, while unsupported or generic operations are delegated to genfs helpers.

Important interactions: `sysvbfs_vfsops.c` implements mount lifecycle and vnode loading; `sysvbfs_vnops.c` implements the vnode operations registered here; `sysvbfs.h` exports the prototypes and `sysvbfs_genfsops`.

Security/reliability notes: no direct parsing logic here. Risk is dispatch correctness: unsupported filesystem features such as links, directories beyond root, symlinks, fallocate, and fdiscard are explicitly rejected via genfs error helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs.h

Read completely: 99 lines.

This is the internal sysvbfs interface header. It defines `struct sysvbfs_node`, which embeds a `genfs_node` and tracks the vnode, BFS inode pointer, mount pointer, advisory lock state, current data block, size, timestamp-update flags, and removal state. It also defines `struct sysvbfs_mount`, containing the NetBSD mount, mounted block-device vnode, and parsed BFS state.

The header declares all sysvbfs vnode operations, VFS operation prototypes through `VFS_PROTOS(sysvbfs)`, the vnode operation vector pointer, genfs operations, `sysvbfs_gop_alloc`, and `sysvbfs_update`.

Important interactions: this header is shared by `sysvbfs.c`, `sysvbfs_vfsops.c`, and `sysvbfs_vnops.c`; it also includes `sysvbfs_args.h` and genfs/specfs headers.

Security/reliability notes: structure fields are mutable vnode state and are protected by normal vnode locking conventions, not by private locks in this header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_args.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_args.h

Read completely: 39 lines.

This public mount-argument header defines `struct sysvbfs_args` with a single `char *fspec` field naming the block special device to mount.

Important interactions: `sysvbfs_mount` validates the provided data length, handles `MNT_GETARGS`, copies back no fspec string, and uses `fspec` through `namei_simple_user` for normal mounts.

Security/reliability notes: the only user/kernel boundary in this header is the device-path pointer. Runtime validation is in `sysvbfs_vfsops.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_args.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_vfsops.c

Read completely: 451 lines.

This implements sysvbfs mount lifecycle and VFS entry points. `sysvbfs_mount` validates mount arguments, resolves the block device, checks block-device type and permissions, handles update mounts, calls `sysvbfs_mountfs`, and fills statvfs metadata. `sysvbfs_mountfs` invalidates device buffers, opens the block device, allocates `struct sysvbfs_mount`, initializes the BFS layer, and sets mount identity and block-size fields.

Other operations include root vnode lookup by `BFS_ROOT_INODE`, statvfs synthesis from BFS metadata, sync over all mounted vnodes, vnode loading via BFS inode lookup, `vcache_get`-based `vget`, unsupported file-handle conversion, pool/malloc initialization and teardown, and a no-op `sysvbfs_gop_alloc`.

Important interactions: depends on `bfs.h` functions such as `sysvbfs_bfs_init`, `bfs_inode_lookup`, `bfs_inode_alloc`, and `sysvbfs_bfs_fini`. Vnode objects are allocated from `sysvbfs_node_pool` and initialized with `genfs_node_init`.

Security/reliability notes: mount validates device type and mount authorization. NFS file handles are unsupported. Unmount closes the device with `FREAD` even if it may have been opened read/write, which is worth preserving or reviewing carefully if changing mount flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_vnops.c

Read completely: 925 lines.

This implements sysvbfs vnode operations for a flat System V BFS filesystem. Lookup recognizes `.` and ordinary root-level files, denies write operations on read-only mounts, checks directory execute/write permissions, and resolves BFS dirents to vnodes. Create delegates to `bfs_file_create`, then loads the new vnode and marks timestamps dirty. Open initializes cached size and data-block state, with non-append writes starting from size zero.

Access, getattr, setattr, and timestamp update map NetBSD vnode attributes onto BFS inode attributes. Read and write use UBC over the vnode object; write resizes contiguous BFS extents through `sysvbfs_file_setsize`. Remove and rename delegate to BFS delete/rename helpers, readdir emits fixed-size `struct dirent` records from the BFS dirent array, and bmap/strategy translate logical file blocks to contiguous device sectors.

Important interactions: relies heavily on the BFS implementation for allocation, dirent lookup, inode lookup/delete, file create/delete/rename, and metadata persistence. Uses `lf_advlock` for byte-range locks and genfs for paging support.

Security/reliability notes: `sysvbfs_rename` computes errors but returns `0` unconditionally at function end, which can hide `EXDEV` or BFS failures. The filesystem model is intentionally limited: one directory, no links, no symlinks, no subdirectories, and 14-byte names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/sysvbfs/sysvbfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/Makefile

Read completely: 7 lines.

This kernel include makefile installs `tmpfs_args.h` under `/usr/include/fs/tmpfs` through `bsd.kinc.mk`.

Important interactions: it exposes only the mount-argument ABI, not tmpfs internal kernel structures.

Security/reliability notes: no runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs.h

Read completely: 350 lines.

This is tmpfs’s main internal data-model header. It defines `tmpfs_dirent_t` for directory entries, `tmpfs_node_t` for inode-like nodes, and `tmpfs_mount_t` for per-mount memory/node accounting and node lists. Nodes store common attributes, timestamps guarded by `tn_timelock`, lockf state, vnode association, link/hold counts, and type-specific data for devices, directories, symlinks, and regular-file UVM anonymous objects.

The header also defines directory-cookie constants, whiteout/generation-bit macros, timestamp-update flags, NFS fid format, conversion helpers from VFS/vnode to tmpfs structures, and prototypes for tmpfs subroutines and memory-accounting helpers.

Important interactions: consumed by all tmpfs implementation files. `tmpfs_vfsops.c` owns mount creation/destruction; `tmpfs_subr.c` owns node/dirent lifecycle and resize logic; `tmpfs_vnops.c` owns vnode behavior.

Security/reliability notes: explicitly kernel/private except for `_KMEMUSER`. Correctness depends on vnode locks protecting most node and dirent fields, with separate locks for mount accounting and timestamp fields.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_args.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_args.h

Read completely: 54 lines.

This public mount-argument header defines `TMPFS_ARGS_VERSION` and `struct tmpfs_args`. Arguments include maximum inode count, maximum size, and root node uid/gid/mode.

Important interactions: `tmpfs_mount` validates the version and data length, derives default memory and node limits when values are small, supports `MNT_GETARGS`, and permits update mounts to adjust limits and root attributes.

Security/reliability notes: mount-time validation rejects bad version, bad uid/gid sentinels, and limit shrink attempts that conflict with current usage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_args.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_fifoops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_fifoops.c

Read completely: 117 lines.

This defines the tmpfs vnode operation vector for FIFOs. Most FIFO behavior comes from `GENFS_FIFOOP_ENTRIES` and calls through `fifo_vnodeop_p`; tmpfs overrides close/read/write plus common metadata operations.

`tmpfs_fifo_read` updates atime before delegating to fifofs read, and `tmpfs_fifo_write` updates mtime before delegating to fifofs write.

Important interactions: included in the tmpfs VFS operation-vector list and selected by `tmpfs_init_vnode` for `VFIFO` nodes.

Security/reliability notes: wrappers are thin and rely on fifofs for FIFO semantics. Metadata updates preserve tmpfs timestamps around delegated operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_fifoops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_fifoops.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_fifoops.h

Read completely: 53 lines.

This kernel-private header declares the tmpfs FIFO vnode operation vector pointer and the FIFO-specific close/read/write wrappers.

Important interactions: included by `tmpfs_fifoops.c` and `tmpfs_subr.c`, where FIFO nodes are assigned `tmpfs_fifoop_p`.

Security/reliability notes: no runtime logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_fifoops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_mem.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_mem.c

Read completely: 238 lines.

This implements tmpfs memory accounting and allocation helpers. Per-mount accounting is initialized, destroyed, and resized through `tm_acc_lock`. Available memory is computed from swap, available memory, file pages, wired pages, and `uvmexp.freetarg`; effective maximum bytes are the smaller of the configured mount limit and currently available system capacity.

The file accounts node structures, dirent structures, regular-file pages, and rounded name allocations against `tm_bytes_used`. It also enforces `tm_nodes_max` with atomic node counters and provides pool-backed allocation/free wrappers for nodes and dirents.

Important interactions: `tmpfs_subr.c` uses these helpers for node, dirent, symlink/name, and regular-file page accounting. `tmpfs_vfsops.c` uses them for mount limits and statvfs.

Security/reliability notes: `tmpfs_mem_incr` rejects allocations when `used + sz >= limit`, leaving one-byte/page headroom by comparison style. Name allocations are rounded to 32-byte quanta and asserted to be no larger than 1024 bytes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_rename.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_rename.c

Read completely: 591 lines.

This implements tmpfs rename through NetBSD’s `genfs_sane_rename`/`genfs_insane_rename` framework. The file provides callbacks for directory-empty checks, rename/remove possible and permitted checks, actual rename/remove mutations, lookup, genealogy analysis, and directory locking.

The actual rename path preallocates a new target name when needed, moves the source dirent between directories, removes/replaces an existing target, updates dirent names, adjusts directory parent/link relationships, updates ctime/mtime on affected nodes, and purges rename cache entries. Genealogy walks parent links from target directory upward to prevent illegal directory cycles and handles directories concurrently removed by rmdir.

Important interactions: delegates policy checks to genfs UFS-like helpers using tmpfs flags, modes, and ownership. Uses `tmpfs_dir_attach`, `tmpfs_dir_detach`, `tmpfs_free_dirent`, `tmpfs_strname_alloc`, and vnode cache lookup.

Security/reliability notes: the implementation is assertion-heavy and explicitly verifies lock state and same-mount invariants. Early name allocation avoids unrecoverable ENOSPC after structural changes have started.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_specops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_specops.c

Read completely: 119 lines.

This defines the tmpfs vnode operation vector for block and character special devices. It combines `GENFS_SPECOP_ENTRIES` with tmpfs metadata operations and wrappers around specfs close/read/write.

`tmpfs_spec_read` updates atime before delegating to `spec_vnodeop_p`; `tmpfs_spec_write` updates mtime before delegating. `tmpfs_spec_close` delegates directly to specfs close.

Important interactions: `tmpfs_init_vnode` selects this vector for `VBLK` and `VCHR` and calls `spec_node_init`.

Security/reliability notes: device I/O semantics remain in specfs; tmpfs only maintains filesystem metadata around those operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_specops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_specops.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_specops.h

Read completely: 53 lines.

This kernel-private header declares the tmpfs special-device vnode operation vector pointer and close/read/write wrappers.

Important interactions: included by `tmpfs_specops.c` and `tmpfs_subr.c`.

Security/reliability notes: no runtime logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_specops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_subr.c

Read completely: 1239 lines.

This is tmpfs’s core lifecycle and helper implementation. It initializes vnodes for tmpfs nodes, loads existing nodes through vcache, creates new nodes, frees nodes, constructs directory entries and files, attaches/detaches dirents, handles directory lookup and cached hints, manages directory sequence cookies, emits readdir entries, resizes regular files, and implements chmod/chown/chflags/chsize/chtimes/update helpers.

Regular files use UVM anonymous objects; `tmpfs_reg_resize` adjusts the UVM object size, zeroes truncated partial pages, drops swap backing for shrinks, and updates tmpfs memory accounting for page count changes. Directories maintain real dirents for children and virtual `.`/`..` entries through reserved cookies. Link count drives node lifetime, with vnode reclaim destroying unlinked nodes.

Important interactions: called by mount creation, vnode operations, rename callbacks, and unmount teardown. It selects vnode operation vectors for regular/directory/symlink/socket, FIFO, and special-device nodes.

Security/reliability notes: careful ENOSPC unwind paths exist for symlink target, dirent, and vnode creation. Directory cookie allocation has a first incremental range and a vmem-managed overflow range. Holdcount/reclaimed bits protect nodes during file-handle lookup and deferred destruction.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vfsops.c

Read completely: 496 lines.

This implements tmpfs VFS operations and module registration. It initializes/destroys global dirent and node pools, validates mount arguments, computes default memory/node limits, supports `MNT_GETARGS`, handles update mounts, creates the root directory node, sets mount flags and statvfs information, and registers tmpfs vnode operation vectors.

Unmount flushes vnodes, detaches and frees all directory entries, clears vnode pointers, drops root and directory virtual links, frees all nodes, destroys memory accounting, and releases the mount structure. File-handle conversion supports `vptofh` and a linear-list `fhtovp` lookup using node id and generation.

Important interactions: `tmpfs_newvnode` and `tmpfs_loadvnode` are implemented in `tmpfs_subr.c`; FIFO/spec/normal vnode op descriptors are aggregated here. Mount memory accounting uses `tmpfs_mem.c`.

Security/reliability notes: update mounts reject node-limit shrink below current count and memory-limit shrink below current use. `tmpfs_vget` by inode number is unsupported; NFS-style file handles use explicit tmpfs fid data instead.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vnops.c

Read completely: 1373 lines.

This implements tmpfs’s main vnode operations. It defines the normal vnode op table and provides lookup, create, mknod, open, access, getattr, setattr, read/write, remove, link, mkdir, rmdir, symlink, readdir, readlink, inactive, reclaim, pathconf, advlock, getpages, putpages, whiteout, and print.

Lookup uses namecache first, handles `.`, `..`, whiteouts, read-only write denial, sticky-directory delete checks, and vcache lookup by node pointer. Create/mknod/mkdir/symlink call `tmpfs_construct_node`. Read/write use UBC over the node’s UVM object; write resizes before copying and rolls size back on error. Remove/rmdir support whiteout replacement. Readdir delegates cookie handling to `tmpfs_dir_getdents` and optionally returns cookie arrays. Page operations delegate to the UVM anonymous object pager and lazily schedule timestamp updates.

Important interactions: rename is implemented in `tmpfs_rename.c`; node/dirent mechanics live in `tmpfs_subr.c`; FIFO and device nodes use separate operation tables.

Security/reliability notes: access and mutation operations enforce read-only mounts, immutable/append flags, sticky directory rules, link limits, and vnode authorization. The page path checks past-EOF requests and reclaimed-vnode state before invoking the pager.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vnops.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vnops.h

Read completely: 76 lines.

This kernel-private header declares the main tmpfs vnode operation vector pointer and all vnode operation functions implemented by `tmpfs_vnops.c`, including `tmpfs_rename` from the rename companion file.

Important interactions: included by FIFO/spec headers and tmpfs implementation files that need common vnode operation prototypes.

Security/reliability notes: no runtime logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vnops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/Makefile

Read completely: 7 lines.

This kernel include makefile installs UDF public headers under `/usr/include/fs/udf`. The installed headers listed here are `ecma167-udf.h` and `udf_mount.h`.

Important interactions: this makes the on-media ECMA/UDF layout definitions available outside the kernel source tree; the private `udf.h` in this group is not listed for installation here.

Security/reliability notes: no runtime behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/ecma167-udf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/ecma167-udf.h

Read completely: 840 lines.

This is the packed on-media ECMA-167/UDF structure definition header. It defines volume recognition descriptors, descriptor tags, logical block addresses, allocation descriptors, character sets, path components, timestamps, entity identifiers, ICB tags and file types, anchors, volume descriptors, partition maps, sparing tables, VAT structures, space bitmaps, partition descriptors, logical volume integrity descriptors, file set descriptors, file identifier descriptors, extended attributes, file entries, extended file entries, indirect entries, allocation extent descriptors, and a `union dscrptr` overlay for descriptor parsing.

The header also defines key constants for tag ids, extent flags and length masks, UDF ICB allocation formats, file type ids, path component ids, partition flags, file identifier flags, permission masks, and descriptor fixed sizes.

Important interactions: included by `udf.h` and UDF implementation files that parse or construct disk descriptors. All structures are `__packed` to match the media format.

Security/reliability notes: this header has no executable logic but is a critical trust boundary for disk parsing. Many structures use flexible one-element trailing arrays, so consumers must validate descriptor lengths and CRC/tag fields before indexing variable payloads.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/ecma167-udf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf.h

Read completely: 432 lines.

This is the kernel-private UDF filesystem state header. It declares debug categories and `DPRINTF` macros, VFS prototypes, implementation identity strings, configuration limits, translation sentinels, buffer content hints, virtual-to-physical mapping types, allocation strategy ids, logical-volume open/close action bits, error-handling bits, and readdir cookie constants.

It defines UDF runtime structures: logical volume integrity trace entries, bitmaps, strategy argument and strategy operation tables, `struct udf_mount` for mounted volume state, and `struct udf_node` for vnode-backed files/directories. The mount structure tracks descriptors, fileset/root state, partition mapping, allocation strategy, sequential/VAT/sparable/metadata partition state, node rb-tree, sync state, and late allocation buffers. Nodes embed `genfs_node`, hold descriptor pointers, extent descriptors, dirhash, lock state, outstanding I/O counts, and related extended-attribute/stream nodes.

Important interactions: includes `ecma167-udf.h`, `udf_osta.h`, device/MMC headers, buffer queues, disk/kthread/malloc support, and genfs node support. The strategy table abstracts bootstrap, sequential, direct, and read-modify-write disc handling.

Security/reliability notes: most fields describe mutable mount-wide filesystem state. Correct locking is central: the file documents that `udf_node.node_mutex` must be claimed before reading/writing node state, and mount allocation/sync paths have their own mutexes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf.h -->