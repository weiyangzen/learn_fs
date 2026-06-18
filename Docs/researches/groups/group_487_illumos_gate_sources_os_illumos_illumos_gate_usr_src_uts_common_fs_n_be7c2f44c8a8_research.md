# Group Research: group_487_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_be7c2f44c8a8

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_vfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_vfsops.c

## Purpose
Implements NFSv2 VFS operations for illumos: filesystem initialization, mount/remount, root vnode construction, unmount, statvfs, sync, fid-to-vnode lookup, NFS root mounting, and final VFS cleanup.

## Main Entry Points
- `nfsinit()` registers NFS vfsops and vnode ops.
- `nfs_mount()` copies and validates user/sysspace mount arguments, builds `servinfo` lists, handles failover/RDMA/security/zone/label policy, creates the root vnode, and applies mount options.
- `nfsrootvp()` allocates and initializes `mntinfo_t`, creates the NFS root rnode, probes server attributes and statfs transfer sizes, starts async manager support, and initializes mount kstats.
- `nfs_unmount()` handles normal and forced unmounts, async shutdown, rnode flushing/destruction, and kstat cleanup.
- `nfs_root()`, `nfs_statvfs()`, `nfs_sync()`, `nfs_vget()`, and `nfs_mountroot()` implement core VFS callbacks.
- `nfs_freevfs()` releases pathconf, server lists, and mount info after VFS teardown.

## Internal Mechanics
Mount argument handling is split between `nfs_copyin()` and `nfs_free_args()`. `nfs_copyin()` supports native and 32-bit user data models through `STRUCT_*` macros, copies transport config, netbufs, file handle, hostname, secure sync address/netname, optional pathconf, and `sec_data`. It transfers ownership of copied pointers into `servinfo` during mount setup.

`nfs_mount()` supports linked `nfs_args` failover lists only for read-only hard mounts. It can replace TCP/UDP transport with RDMA transport when `NFSMNT_TRYRDMA` or `NFSMNT_DORDMA` is requested. `NFSMNT_DORDMA` may discard non-RDMA-capable replicas or reject the mount if no usable server remains.

Security handling accepts newer `sec_data` via `NFS_ARGS_EXTA/B`, validates RPC flavors for sysspace mounts, and preserves legacy `NFSMNT_SECURE`/`NFSMNT_RPCTIMESYNC` AUTH_DES setup. Non-UNIX/loopback flavors get `AUTH_F_TRYNONE` during mount probing so initial GETATTR/STATFS can retry with AUTH_NONE.

`nfsrootvp()` establishes mount defaults: NFS program/version, procedure name/stat tables, call/timer type tables, ACL procedure tables, attribute cache bounds, hard/soft/semisoft/interrupt/directio flags, async queues, per-zone mount linkage, device/fsid assignment, and root vnode. It queries every replica with `RFS_STATFS` to derive minimum server transfer size.

Pathconf data is globally interned in `allpc` with reference counts so multiple mounts can share identical POSIX pathconf structures. Remount only updates pathconf and rejects locking-mode changes.

## Dependencies
Uses illumos VFS/vnode infrastructure, NFS rnodes and mount info, RPC client/security modules, RDMA reachability, zones, Trusted Extensions label policy, kstats, async NFS worker infrastructure, DNLC/rnode cache helpers, and NFSv2 XDR routines from `nfs_xdr.c`.

## Risks and Notes
- The pathconf intern table is a static global list; correctness depends on mount/remount/free paths maintaining refcounts.
- RDMA mount handling mutates `servinfo` transport ownership and has several failover paths where cleanup ordering matters.
- Legacy AUTH_DES conversion has delicate ownership of copied `knetconfig`, netbuf, and netname fields.
- NFS root mounting is special: it uses boot-time `mount_root()`, always sets AUTH_UNIX, and installs the root VFS manually.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_vnops.c

## Purpose
Implements NFSv2 vnode operations: open/close, read/write, attribute operations, access checks, lookup/create/remove/rename/link/mkdir/rmdir/symlink/readdir, VM page cache integration, mmap handling, record/share locking, ACL hooks, pathconf, and fid generation.

## Main Entry Points
- `nfs_vnodeops_template[]` registers all VOP callbacks for NFSv2.
- `nfs_open()` and `nfs_close()` enforce close-to-open consistency, credential retention, lock cleanup, page flushing, and delayed write error reporting.
- `nfs_read()` and `nfs_write()` implement VM-cached I/O through segmap/VPM plus direct/no-cache paths using `nfsread()` and `nfswrite()`.
- `nfs_getattr()`, `nfs_setattr()`, and `nfssetattr()` manage cache validation, dirty-page flushing, permission policy, NFS SETATTR RPCs, truncation, time conversion, and ACL/access cache purge.
- `nfs_lookup()`, `nfslookup()`, `nfslookup_dnlc()`, and `nfslookup_otw()` implement directory lookup, extended attribute lookup, DNLC positive/negative caching, and failover-aware LOOKUP RPCs.
- Directory mutation callbacks include `nfs_create()`, `nfs_remove()`, `nfs_link()`, `nfs_rename()`/`nfsrename()`, `nfs_mkdir()`, `nfs_rmdir()`, and `nfs_symlink()`.
- Page and mmap callbacks include `nfs_getpage()`, `nfs_getapage()`, `nfs_readahead()`, `nfs_putpage()`, `nfs_putapage()`, `nfs_sync_putapage()`, `nfs_pageio()`, `nfs_map()`, `nfs_addmap()`, `nfs_delmap()`, and `nfs_delmap_callback()`.
- Locking and metadata support includes `nfs_fid()`, `nfs_rwlock()`, `nfs_rwunlock()`, `nfs_seek()`, `nfs_frlock()`, `nfs_space()`, `nfs_pathconf()`, `nfs_setsecattr()`, `nfs_getsecattr()`, and `nfs_shrlock()`.

## Internal Mechanics
The file translates vnode operations into NFSv2 RPCs using `rfs2call()` and XDR helpers. Most operations enforce zone ownership before wire I/O. Rnode state locks protect cached size, attributes, symlink contents, readdir cache state, pending writes, mmap counts, stale state, delayed errors, and temporary unlink names.

Read/write paths choose between direct RPC buffers and VM-cached segmap/VPM operation. Direct I/O is used for `VNOCACHE`, per-rnode direct I/O, mount direct I/O, or when no mappings/cached pages exist. Cached writes throttle dirty page creation based on async queue pressure and active getattr pagewalks.

`nfsread()` issues chunked `RFS_READ` calls, updates I/O kstats, zero-residual handling through callers, and compares returned attributes against cache state without forcing a cache purge while pages are locked. `nfswrite()` issues chunked synchronous `RFS_WRITE` calls, updates kstats, purges attributes, and sets `RWRITEATTR` so close can refresh attributes not returned by WRITE.

Directory operations carefully maintain DNLC and readdir caches. Creates handle NFSv2 special-file encoding by packing device numbers into mode/size fields. Remove and rename implement local unlink-open semantics by renaming active files to generated `.nfs*` names and recording cleanup data in the rnode for `nfs_inactive()`.

`nfs_readdir()` uses an AVL-backed `rddir_cache` keyed by server cookie and request size. It supports waiters on in-progress cache fills, async readdir readahead, EOF cookie short-circuiting, and cache invalidation on directory mutations. `nfsreaddir()` fills cache entries from `RFS_READDIR`.

The VM path uses `nfs_bio()` as the common page I/O bridge. `nfs_getapage()` clusters reads, handles EOF and zero-fill cases, and schedules async readahead using `nfs_nra`. `nfs_putapage()` clusters writes, detects `RMODINPROGRESS` races with `writerp()`, and either schedules async writeback or performs synchronous writeback. Out-of-space/quota/access errors set rnode state and may force invalidation retries.

Mmap support blocks mapping when direct/no-cache state or mandatory locks make caching unsafe. `nfs_delmap()` installs address-space callbacks so potentially slow NFS flush work runs without holding the address-space lock; the callback updates map counts and flushes or invalidates pages based on close-to-open/direct-I/O semantics.

Record locks use either local `fs_frlock()` for `MI_LLOCK` mounts or lock-manager calls with NFS file handles. Nonlocal locks flush/invalidate cached pages before setting/unsetting locks. Share reservations wrap local owner data with NFS owner magic and hostname before calling the lock manager.

## Dependencies
Depends on illumos VOP/VM/segmap/VPM/pageout infrastructure, rnode and mount state helpers, NFS async worker queues, DNLC, ACL v2 helpers, lock manager (`lm_*`), kstats, DTrace I/O probes, NFS failover helpers, vnode event notifications, and XDR routines in `nfs_xdr.c`.

## Risks and Notes
- Many paths depend on careful lock ordering between `r_rwlock`, `r_lkserlock`, `r_statelock`, page locks, and address-space locks.
- NFSv2 32-bit offset limits are enforced throughout; reads/writes/truncates beyond `MAXOFF32_T` fail.
- Delayed write errors are stored in `r_error` and surfaced later on close/fsync/page operations.
- The `.nfs*` temporary-name mechanism is central to POSIX unlink-open behavior over a protocol without native support.
- Readdir cookies are opaque server offsets; `lseek()` on directories intentionally allows these values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_xdr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_xdr.c

## Purpose
Provides XDR encode/decode/free routines for NFSv2 protocol structures used by both client and server paths, with optimized inline encoders/decoders and special support for mblk and RDMA transports.

## Main Entry Points
- File handles and attributes: `xdr_fhandle()`, `xdr_fastfhandle()`, `xdr_fattr()`, `xdr_fastfattr()`, `xdr_nfs2_timeval()`.
- Read/write: `xdr_writeargs()`, `xdr_readargs()`, `xdr_rrok()`, `xdr_rdresult()`.
- Attribute/status results: `xdr_sattr()`, `xdr_attrstat()`, `xdr_fastattrstat()`, `xdr_saargs()`.
- Symlink/readlink: `xdr_readlink()`, `xdr_srok()`, `xdr_rdlnres()`, `xdr_slargs()`.
- Readdir: `xdr_rddirargs()`, `xdr_putrddirres()`, `xdr_getrddirres()`.
- Directory ops: `xdr_diropargs()`, `xdr_drok()`, `xdr_fastdrok()`, `xdr_diropres()`, `xdr_fastdiropres()`, `xdr_creatargs()`, `xdr_linkargs()`, `xdr_rnmargs()`.
- Statfs and fast helpers: `xdr_fsok()`, `xdr_fastfsok()`, `xdr_statfs()`, `xdr_faststatfs()`, `xdr_fastenum()`, `xdr_fastshorten()`.

## Internal Mechanics
Most routines first try `XDR_INLINE()` to encode/decode fixed-size fields directly as 32-bit XDR words. If inline storage is unavailable, they fall back to generic `xdr_*` helpers. Little-endian fast paths mutate structures into network order for pre-sized replies, while big-endian fast paths can often leave already laid-out data in place.

`xdr_writeargs()` supports normal byte arrays, mblk-backed data (`xdrmblk_getmblk()`), and RDMA read-from-client paths. Its `XDR_FREE` branch releases RDMA clists and allocated write buffers.

`xdr_readargs()` records expected RDMA write chunks during sizing/encoding and decodes RDMA write-list connection state. `xdr_rrok()` handles read replies over normal XDR, mblk XDR, and RDMA write chunks, including count-only replies when data is transferred by RDMA.

Readdir encoding converts kernel `dirent64` records into NFSv2 wire entries with 32-bit inode/cookie validation. Decode reconstructs `dirent64` records into the caller buffer and reports partial-buffer overflow by returning the bytes filled and next cookie.

Directory operation argument decoding allocates names when needed, enforces `NFS_MAXNAMLEN`, null-terminates names, and rejects embedded NULs by comparing `strlen()` with the XDR length. Free paths release only names marked with local free flags.

## Dependencies
Uses illumos RPC/XDR APIs, stream mblk XDR operations, RDMA XDR operations, NFSv2 protocol structs/constants, kernel memory allocation, dirent layout macros, and endian conversion helpers.

## Risks and Notes
- Many routines assume exact NFSv2 fixed layout and rely on 32-bit truncation checks for inode/cookie fields.
- RDMA paths have distinct encode/decode/free ownership rules for clists and transferred data.
- Fast little-endian routines convert structures in place, so callers must only use them in contexts expecting that mutation.
- `xdr_fastshorten()` adjusts XDR stream position to strip unused union payload space in fast reply paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_common.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_common.c

## Purpose
Provides common objfs vnode helper routines shared by root, object-directory, and data-file nodes.

## Main Entry Points
- `objfs_dir_open()` permits directory opens only with `FOFFMAX` and rejects writable opens.
- `objfs_common_close()` is a no-op close callback for nodes needing no per-close cleanup.
- `objfs_dir_access()` denies directory write access and allows other access.
- `objfs_common_getattr()` fills common `vattr_t` fields such as owner, group, block size, block count, sequence, and fsid.
- `objfs_nobjs()` counts currently loaded kernel modules.

## Internal Mechanics
`objfs_nobjs()` walks the global `modules` circular list under `mod_lock` and counts `mod_loaded` entries. Attribute helpers treat objfs as read-only, root-owned, and device-block-sized.

## Dependencies
Uses objfs internal headers, generic file/vnode types, module control list state, `mod_lock`, and kernel block-size helpers.

## Risks and Notes
The loaded-object count is dynamic and only a snapshot under `mod_lock`; directory link counts/statvfs values can change as modules load or unload.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_data.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_data.c

## Purpose
Implements `/system/object/<module>/object`, a synthetic read-only ELF file exposing metadata about a loaded kernel module for consumers such as DTrace. It includes CTF, symbol/string tables, pseudo section headers for text/data/bss, filename, and private objfs info while avoiding export of actual text/data/bss contents.

## Main Entry Points
- `objfs_data_init()` builds the section-header string table and resolves section links.
- `objfs_create_data()` creates a GFS file vnode for an object’s `object` file and records module generation/primary status.
- `objfs_data_lock()` and `objfs_data_unlock()` hold/release the module while validating that the vnode still refers to the current module generation.
- `objfs_data_getattr()` reports the synthetic ELF file size.
- `objfs_data_open()` rejects writes.
- `objfs_data_read()` synthesizes the ELF header, section headers, section data, padding, and special symbol-table transformations.
- `objfs_tops_data[]` registers VOPs for the data file.

## Internal Mechanics
The file defines `section_desc_t` descriptors for dummy, `.shstrtab`, `.SUNW_ctf`, `.symtab`, `.strtab`, `.text`, `.data`, `.bss`, `.info`, and `.filename`. `SECT_DATA` descriptors store offsets into `struct module` fields rather than direct addresses. `sect_addr()`, `sect_size()`, and `sect_valid()` compute per-module section presence and layout.

`data_offset()` calculates the synthetic file layout: ELF header, valid section headers, then valid non-`SHT_NOBITS` section data with alignment. `next_offset()` and `data_size()` derive section boundaries and total file size from the same layout logic.

`objfs_data_read()` constructs a native 32-bit or 64-bit ELF header based on kernel build, sets endian/class/machine fields, uses `ET_SUNWPSEUDO`, emits only valid section headers, and then emits backing data for materialized sections. `.text`, `.data`, and `.bss` are represented as `SHT_NOBITS` with address/size metadata only. `.symtab` is copied symbol-by-symbol through `read_symtab()`, which rewrites defined symbols’ `st_shndx` to `SHN_ABS`.

## Dependencies
Uses GFS file helpers, kernel module loader structures, ELF headers, objfs internal node types, `mod_hold_by_modctl()`, `mod_release_mod()`, `uiomove()`, and kernel memory allocation.

## Risks and Notes
- Reads fail if the module was unloaded or reloaded after the data vnode was created, detected through `mod_gencount`.
- Layout code must keep section offsets, alignment, validity, and ELF header `e_shnum/e_shstrndx` consistent.
- The file intentionally exposes addresses and sizes for loaded module sections but not raw text/data/bss bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_odir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_odir.c

## Purpose
Implements each per-module objfs directory `/system/object/<module>`, containing the synthetic `object` file.

## Main Entry Points
- `objfs_create_odirnode()` creates a GFS directory vnode for one loaded module and records its `modctl`.
- `objfs_odir_do_inode()` derives the inode number for the contained `object` file.
- `objfs_odir_getattr()` reports read/execute directory attributes.
- `objfs_tops_odir[]` registers object-directory VOPs.

## Internal Mechanics
The directory entries table contains a single real entry: `"object"`, created by `objfs_create_data()`. Inode numbers are generated from the module id with `OBJFS_INO_DATA()`. Attributes are dynamic timestamps from `gethrestime()` plus common objfs fields.

## Dependencies
Uses GFS directory helpers, objfs inode macros, module control structures, and common objfs directory/access helpers.

## Risks and Notes
The object-directory vnode stores a raw persistent `modctl` pointer. The data file later validates the underlying module generation before exposing contents.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_odir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_root.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_root.c

## Purpose
Implements the root directory of objfs, listing one directory per currently loaded kernel module.

## Main Entry Points
- `objfs_create_root()` creates the GFS root vnode with custom lookup/readdir callbacks.
- `objfs_root_getattr()` reports root directory attributes, including link count based on loaded object count.
- `objfs_root_do_lookup()` resolves a module name to an object-directory vnode.
- `objfs_root_do_readdir()` emits loaded module names as directory entries.
- `objfs_root_readdir()` wraps GFS directory iteration.
- `objfs_tops_root[]` registers root VOPs.

## Internal Mechanics
Lookup walks the global `modules` circular list under `mod_lock` and matches loaded modules by `mod_modname`. It drops `mod_lock` around vnode allocation because `modctl` structures are persistent.

Readdir uses module ids as offsets/cookies. It compares against `last_module_id` for EOF, skips unloaded modules, emits `mod_modname`, and assigns inode numbers with `OBJFS_INO_ODIR()`.

## Dependencies
Uses GFS root/directory helpers, global module list state, `mod_lock`, `last_module_id`, objfs inode macros, and common objfs directory helpers.

## Risks and Notes
Directory contents are live views of currently loaded modules. Readdir offset logic assumes module ids are monotonic and persistent enough for cookie-style iteration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_root.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_vfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_vfs.c

## Purpose
Implements objfs module linkage, filesystem initialization, and VFS operations for the kernel object filesystem.

## Main Entry Points
- `_init()`, `_info()`, and `_fini()` provide module linkage; `_fini()` returns `EBUSY` because objfs cannot be unloaded.
- `objfs_init()` registers VFS ops, builds GFS vnode op vectors, obtains a unique device major, and initializes data-file section metadata.
- `objfs_mount()` validates permission/mountpoint state, assigns a unique device/fsid, allocates `objfs_vfs_t`, and creates the root vnode.
- `objfs_unmount()` rejects forced unmounts, checks for active vnodes, releases the root vnode, and frees vfs-private data.
- `objfs_root()` returns the held root vnode.
- `objfs_statvfs()` reports pseudo-filesystem stats.

## Internal Mechanics
Objfs is declared as `"objfs"` with `VSW_HASPROTO | VSW_ZMOUNT`. It has three GFS operation vectors: root directory, object directory, and data file. Mount allocates a synthetic device number using `objfs_major` and atomically incremented `objfs_minor`, avoiding already mounted device ids.

Unmount expects only the caller and root vnode references to remain. Active object/data vnodes hold the root, so a root vnode count above one yields `EBUSY`.

## Dependencies
Uses illumos module linkage, VFS registration APIs, GFS op-vector construction, mount policy checks, unique device allocation, objfs node constructors, and common objfs object counting.

## Risks and Notes
- Forced unmount is explicitly unsupported.
- Objfs is non-unloadable, likely because exported module-object views and global initialized data are intended to persist.
- Stat values are pseudo values based on loaded object count rather than storage capacity.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/objfs/objfs_vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pathname.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pathname.c

## Purpose
Provides kernel pathname buffer utilities used during path lookup and symlink expansion.

## Main Entry Points
- `pn_alloc()` and `pn_alloc_sz()` allocate pathname buffers.
- `pn_free()` frees pathname storage.
- `pn_get_buf()` copies a user or kernel string into a caller-provided pathname buffer.
- `pn_get()` allocates a `MAXPATHLEN` buffer and copies a pathname into it.
- `pn_set()` resets an allocated pathname to a kernel string.
- `pn_insert()` replaces the current component with symlink contents during lookup.
- `pn_getsymlink()` reads a symlink target into a pathname buffer.
- `pn_getcomponent()` extracts the next path component.
- `pn_skipslash()`, `pn_setlast()`, `pn_fixslash()`, and `pn_addslash()` manipulate slash and component state.

## Internal Mechanics
`struct pathname` tracks the original buffer, current path pointer, current path length, and buffer size. `pn_get_buf()` supports user-space and kernel-space sources via `copyinstr()` and `copystr()`, then subtracts the terminating NUL from `pn_pathlen`.

`pn_insert()` is designed for symlink processing. Absolute symlink targets replace the entire pathname buffer from the start. Relative targets replace the just-consumed component by moving `pn_path` backward by `complen` and inserting the target before the remaining suffix.

`pn_getcomponent()` temporarily writes a slash sentinel at either `MAXNAMELEN` or current path length to guarantee loop termination, copies the component, restores the original byte/NUL, advances `pn_path`, and updates `pn_pathlen`.

Slash helpers trim leading slashes, isolate the final component, remove trailing slashes, or append a trailing slash while compacting the active component to the start of the buffer if needed.

## Dependencies
Uses kernel allocation, copyin/copystr helpers, vnode `VOP_READLINK`, `uio`/`iovec`, and pathname/vnode constants such as `MAXPATHLEN` and `MAXNAMELEN`.

## Risks and Notes
- Many routines mutate the pathname buffer in place and depend on `pn_path`/`pn_pathlen` staying consistent.
- `pn_insert()` and `pn_addslash()` use overlapping copies to preserve remaining path suffixes.
- Component extraction enforces `MAXNAMELEN`; too-long components return `ENAMETOOLONG`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pathname.c -->