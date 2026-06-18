# Group Research: group_336_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_nfs_nfsv2_h_sources_c896eb5a755e

Subset scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsv2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsv2.h

This is a compatibility shim for older NFS code. Its only operational content is inclusion of `nfsproto.h`, after the historical Berkeley/FreeBSD/DragonFly license and version comments.

The file carries no local constants, structures, or functions. Its role is to preserve the legacy `nfsv2.h` include path while moving actual NFS protocol definitions into `nfsproto.h`.

Dependencies: `nfsproto.h`.

Research notes: any semantic analysis for NFSv2 protocol constants should follow `nfsproto.h`; this file itself is only an include wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsv2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/rpcv2.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/rpcv2.h

This header defines Sun RPC version 2 constants used by the DragonFly NFS implementation. It includes protocol version IDs, authentication flavor numbers, RPC message/reply status codes, authentication failure codes, fixed header sizes, mountd/NFS program numbers, and mount RPC limits.

It also defines Kerberos-v4-related RPC verifier structures: `nfsrpc_fullverf`, `nfsrpc_fullblock`, and `nfsrpc_nickverf`, plus explicit byte-size constants that must match their wire layout. The `NFSKERB` branch is effectively disabled with an `XXX` placeholder, while the non-Kerberos path typedefs tiny placeholder key arrays.

Key constants include `RPC_VER2`, `RPCAUTH_UNIX`, `RPCAUTH_KERB4`, `RPC_CALL`, `RPC_REPLY`, `RPCPROG_MNT`, `RPCPROG_NFS`, `RPCX_FULLVERF`, `RPCX_FULLBLOCK`, and Kerberos service/TTL/skew macros.

Research notes: this is wire-format ABI material. Changes affect NFS client/server RPC framing and should be treated as protocol compatibility changes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/rpcv2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/xdr_subs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/xdr_subs.h

This header provides NFS XDR conversion macros around `htonl` and `ntohl`. It covers unsigned 32-bit conversion, NFSv2 timestamp conversion between seconds/microseconds and `timespec`, NFSv3 timestamp conversion between seconds/nanoseconds and `timespec`, and 64-bit “hyper” conversion from/to two 32-bit network-order words.

Important macros: `fxdr_unsigned`, `txdr_unsigned`, `fxdr_nfsv2time`, `txdr_nfsv2time`, `fxdr_nfsv3time`, `txdr_nfsv3time`, `fxdr_hyper`, and `txdr_hyper`.

Research notes: the macros intentionally use 32-bit network byte-order operations even on big-endian machines and avoid relying on alignment. The NFSv2 timestamp macros treat all-ones microseconds and `tv_nsec == -1` as a special sentinel.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/xdr_subs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/Makefile

This kernel module Makefile builds the `ntfs` module from `ntfs_vfsops.c`, `ntfs_vnops.c`, `ntfs_subr.c`, `ntfs_ihash.c`, and `ntfs_compr.c`. It also includes generated/config header `opt_ntfs.h`.

The Makefile declares `SUBDIR= ntfs_iconv`, so the optional NTFS iconv helper module is built as a subdirectory module.

Research notes: module composition makes `ntfs_subr.c` the core metadata/data-path helper, `ntfs_vfsops.c` the mount/VFS layer, `ntfs_vnops.c` the vnode interface, `ntfs_ihash.c` the in-core inode hash, and `ntfs_compr.c` compressed attribute support.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs.h

This is the main on-disk NTFS format and mount-state header. It defines cluster and Unicode types (`cn_t`, `wchar`), packed on-disk structures for boot sectors, file records, attributes, standard time fields, file-name attributes, index roots, index allocation records, index entries, attribute-list records, and `$AttrDef` records.

It also defines NTFS system inode numbers such as `$MFT`, `$Volume`, `$AttrDef`, root, `$Bitmap`, boot, bad-clusters, and `$UpCase`, plus attribute type IDs such as standard information, attribute list, file name, volume name, data, index root, index allocation, and index bitmap.

`struct ntfsmount` stores per-mount state: mount pointer, bootfile copy, device vnode/device, retained system vnodes, MFT record sizing, default uid/gid/mode, mount flags, free cluster count, translated attribute definitions, export state, character conversion tables, and iconv handles.

Important macros map between mount/vnode/fnode/ntnode objects (`VFSTONTFS`, `VTOF`, `VTONT`, `FTOV`, `FTONT`) and convert clusters, bytes, blocks, and disk offsets using the in-scope `ntmp`.

Research notes: the header uses `#pragma pack(1)` for disk structures, so layout is ABI-critical. Several comments mark fields as unknown or inferred, reflecting the age of this NTFS implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_compr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_compr.c

This file implements decompression for NTFS compressed attribute data. `ntfs_uncompblock()` expands one 4 KiB NTFS compression block, handling both uncompressed block payloads and compressed tag/literal/back-reference streams. `ntfs_uncompunit()` walks a full NTFS compression unit and repeatedly calls `ntfs_uncompblock()` into the caller-provided uncompressed buffer.

The decompressor uses a local `GET_UINT16` macro for little in-memory 16-bit reads and relies on NTFS block/unit constants from `ntfs_compr.h`.

Dependencies: `ntfs.h`, `ntfs_compr.h`.

Research notes: this is read-path support only. It does not implement compression for writes. Bounds are mostly controlled by NTFS block-size constants and compressed block lengths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_compr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_compr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_compr.h

This header defines NTFS compression geometry and exports decompression helpers. `NTFS_COMPBLOCK_SIZE` is `0x1000` bytes and `NTFS_COMPUNIT_CL` is 16 clusters.

Exported functions are `ntfs_uncompblock()` for one compression block and `ntfs_uncompunit()` for a compression unit.

Research notes: callers need `struct ntfsmount` and the cluster conversion macros from `ntfs.h`; this header is intentionally small and only covers decompression.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_compr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_iconv/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_iconv/Makefile

This Makefile builds the `ntfs_iconv` kernel module from `ntfs_iconv.c`.

The module is separate from the base `ntfs` module and provides optional character-set conversion support through the kernel iconv framework.

Research notes: the parent NTFS Makefile includes this directory as a submodule.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_iconv/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_iconv/ntfs_iconv.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_iconv/ntfs_iconv.c

This file declares NTFS support for the kernel iconv framework with `VFS_DECLARE_ICONV(ntfs)`. It includes kernel module, mount, and iconv headers.

There are no local functions beyond the macro expansion. The base NTFS code references `struct iconv_functions *ntfs_iconv` and uses it when `NTFS_MFLAG_KICONV` is set.

Research notes: this is glue code; charset conversion behavior lives in the generic iconv framework and in the NTFS conversion setup/use functions in `ntfs_subr.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_iconv/ntfs_iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_ihash.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_ihash.c

This file implements the in-core `ntnode` hash table for NTFS. It allocates a hash table sized via `vfs_inodehashsize()`, keyed by device minor plus inode number, and protects lookup/insert/remove with a DragonFly LWKT token. A separate exported `ntfs_hashlock` is used by higher-level allocation logic in `ntfs_ntlookup()`.

Functions: `ntfs_nthashinit()`, `ntfs_nthash_uninit()`, `ntfs_nthashlookup()`, `ntfs_nthashins()`, and `ntfs_nthashrem()`.

Dependencies: `ntfs.h`, `ntfs_inode.h`, `ntfs_ihash.h`.

Research notes: the header declares `ntfs_nthashget()`, but this implementation does not define it. Actual lookup users call `ntfs_nthashlookup()`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_ihash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_ihash.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_ihash.h

This header exports the NTFS ntnode hash API and `ntfs_hashlock`.

Declarations include hash initialization/uninitialization, lookup, get, insert, and remove functions. `ntfs_nthashget()` is declared here but not implemented in the corresponding `ntfs_ihash.c`.

Research notes: consumers should verify whether `ntfs_nthashget()` is dead legacy API before using it.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_ihash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_inode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_inode.h

This header defines NTFS in-memory inode and file-stream state. `struct ntnode` represents an NTFS MFT record and tracks device identity, mount, inode number, flags, locks, use count, attached fnodes, loaded attribute list, link count, main record, and file-record flags.

`struct fnode` represents a vnode-exposed NTFS attribute stream for an `ntnode`; it stores the vnode pointer, stream type/name, file times, parent inode number, NTFS file flags, size/allocation, directory read cache cursor, and directory block buffer.

It also defines inode flags such as `IN_HASHED`, `IN_LOADED`, and `IN_PRELOADED`, fnode flags such as `FN_PRELOADED`, `FN_VALID`, and `FN_AATTRNAME`, and `struct ntfid` for NFS file handles.

Research notes: NTFS separates MFT-record identity (`ntnode`) from named attribute-stream vnode identity (`fnode`), which is important for alternate data stream handling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_subr.c

This is the core NTFS metadata and data-path helper implementation. It loads MFT records into `ntnode` attribute lists, resolves attributes directly or through `$ATTRIBUTE_LIST`, expands nonresident runlists, reads and writes plain nonresident attribute data through the buffer cache, decompresses compressed reads, performs directory lookup and directory enumeration, converts NTFS timestamps, and manages filename charset conversion.

Major metadata functions include `ntfs_loadntnode()`, `ntfs_attrtontvattr()`, `ntfs_runtovrun()`, `ntfs_ntvattrget()`, `ntfs_findvattr()`, `ntfs_ntlookup()`, `ntfs_ntget()`, `ntfs_ntput()`, `ntfs_ntref()`, `ntfs_ntrele()`, `ntfs_fget()`, and `ntfs_frele()`.

Directory logic is split between `ntfs_ntlookupfile()` and `ntfs_ntreaddir()`. Lookup scans `$INDEX_ROOT:$I30`, optionally follows index-allocation subnodes, handles `filename:stream` syntax through attribute definition lookup, and instantiates target vnodes via `ntfs_vgetex()`. Readdir fakes a flat stream over NTFS directory indexes by reading `$INDEX_ROOT`, `$BITMAP:$I30`, and `$INDEX_ALLOCATION:$I30`.

Data I/O is handled by `ntfs_readattr()`, `ntfs_readattr_plain()`, `ntfs_readntvattr_plain()`, `ntfs_writeattr_plain()`, and `ntfs_writentvattr_plain()`. Reads support resident data, nonresident runlists, sparse holes, and compressed units. Writes are limited to plain nonresident attributes and cannot extend files.

Other support includes `ntfs_procfixups()` for NTFS update-sequence fixups, `ntfs_toupper_use()` for loading `$UpCase`, `ntfs_u28()`/`ntfs_82u()` and init/uninit helpers for Unicode/local charset conversion, and string comparison helpers used by case-sensitive/case-insensitive lookup.

Research notes: the code contains old/disabled helper functions under `#if 0`. Several comments flag imperfect locking or old assumptions. The implementation is functional but conservative: no create/delete path is present here, and write support is constrained.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_subr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_subr.h

This header defines `struct ntvattr`, the in-memory representation of one NTFS attribute, including type, name, compression fields, data length/allocation, VCN range, index, resident data pointer, runlist arrays, or typed overlays for file name/index root/index allocation data.

It also declares the NTFS helper API implemented mostly in `ntfs_subr.c`: fixups, run parsing, attribute reads/writes, size/time queries, directory lookup/enumeration, attribute conversion/freeing, ntnode/fnode lifetime management, toupper table management, and charset conversion.

Research notes: some declared functions are disabled or absent in the implementation (`ntfs_parserun`, `ntfs_runtocn`, `ntfs_loadntvattrs`, `ntfs_findntvattr`), so this header includes legacy API surface beyond active code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_subr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vfsops.c

This file implements the NTFS VFS layer: mount, unmount, root lookup, statfs/statvfs, vnode lookup by inode, NFS filehandle conversion, export checking, and module initialization. It defines NTFS malloc types and the global `ntfs_iconv` function table pointer.

`ntfs_mount()` handles root and non-root mounts, argument copyin, update/export handling, device lookup, and device validation. `ntfs_mountfs()` opens the block device, reads and validates the boot sector, computes MFT record size, initializes charset tables, installs vnode ops, opens retained system vnodes (`$MFT`, root, `$Bitmap`), loads `$UpCase`, counts free clusters from `$Bitmap`, and reads `$AttrDef` into internal translated definitions.

`ntfs_unmount()` flushes non-system and system vnodes, checks retained system vnode references, closes the device, releases charset/toupper state, frees attribute definitions and mount state, and clears `MNT_LOCAL`.

`ntfs_vgetex()` is the central vnode factory. It maps inode number plus attribute type/name to an `ntnode` and `fnode`, optionally loads attributes, computes vnode type and stream size, reuses an existing vnode if present, otherwise allocates and initializes a new vnode.

Research notes: mount setup is read-heavy and retains core metadata vnodes to keep access stable. Export support uses inode-number-only file handles, with comments noting limited mutation support.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vfsops.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vfsops.h

This header defines flags for `ntfs_vgetex()`: `VG_DONTLOADIN`, `VG_DONTVALIDFN`, and `VG_EXT`. These control whether to load the `ntnode`, validate the `fnode`, and treat a record as an external/non-main record.

It declares `ntfs_vgetex()` and `ntfs_calccfree()`.

Research notes: these flags are used by directory lookup and attribute-list traversal to instantiate partial or external vnode state without forcing all normal validation paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vfsops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vnops.c

This file implements NTFS vnode operations. It wires `ntfs_vnode_vops` with getattr, inactive, reclaim, pathconf, old lookup, access, open/close, readdir, fsync, bmap, VM get/put pages, strategy, read, and write.

The read path uses cluster-sized `bread()` calls through the vnode/buffer cache. The strategy path maps buffer I/O to `ntfs_readattr()` or `ntfs_writeattr_plain()`. Writes are allowed only within the existing file size; attempts to extend return `EFBIG`.

`ntfs_getattr()` synthesizes Unix attributes from mount uid/gid/mode defaults, fnode size/allocation, ntnode link count, and NTFS file times. `ntfs_access()` checks mount read-only state and applies the mount-provided permission mask rather than per-file NTFS ACLs.

`ntfs_readdir()` simulates `.` and `..`, then converts NTFS Unicode names through `NTFS_U28()` and emits directory entries from `ntfs_ntreaddir()`. `ntfs_lookup()` handles `.`, `..`, and ordinary child lookup through `ntfs_ntlookupfile()`.

Research notes: this vnode layer presents a Unix-like view of NTFS with simplified permissions and limited write behavior. It does not implement create, remove, rename, mkdir, or truncation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfsmount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfsmount.h

This header defines NTFS mount flags and the user-kernel mount argument structure. Flags include case-insensitive lookup, showing all name variants, and using kernel iconv conversion.

`struct ntfs_args` carries the block device path, export args, default uid/gid/mode, flags, a 256-entry Unix-to-wchar table, and local/NTFS charset names for iconv.

Research notes: NTFS permission and charset behavior is mount-option driven rather than read from NTFS ACLs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/Makefile

This Makefile builds the `null` kernel module from `null_vfsops.c` and `null_vnops.c`.

Research notes: the module is the DragonFly nullfs/loopback filesystem implementation.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null.h

This header defines nullfs mount arguments and mount-private state. `struct null_args` contains the target path and export arguments. `struct null_mount` stores the nullfs mount pointer, held root vnode reference, and export state.

It also defines `MOUNTTONULLMOUNT()`, optional `NULLFSDEBUG()`, and the `nullfs_export()` prototype.

Research notes: nullfs private state is intentionally small because DragonFly’s implementation relies heavily on namecache forwarding instead of private overlay vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null_vfsops.c

This file implements nullfs VFS operations. Mount resolves the target path via namecache, gets the lower root vnode, allocates `struct null_mount`, installs vnode ops, stores a held root vnode reference, adjusts mount flags inherited from the lower filesystem, and sets up namecache mount-point state for DragonFly’s lightweight stacking model.

It supports mount updates for export changes, generates a stable-ish fsid from the lower root file handle plus mount path CRC, forwards statfs/quotactl/extattr/namecache-generation operations to the lower filesystem, and implements NFS export checks against nullfs-local export state.

Unmount releases the held root vnode and frees mount state. `nullfs_modifying()` rejects writes on a read-only nullfs mount and otherwise forwards modification checks to the lower filesystem.

Research notes: comments emphasize that when stacking nullfs over nullfs, it must avoid endless recursion by resolving the actual lower filesystem mount. The mount is registered as loopback and MPSAFE with no syncer thread.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null_vnops.c

This file implements nullfs vnode/namecache forwarding operations. The historical comment explains that DragonFly nullfs no longer maintains private null vnodes for most operations; instead, it uses the namecache API and rewrites operation dispatch to the lower mount’s normal vnode ops.

Implemented forwarding wrappers cover namecache operations: resolve, create, mkdir, mknod, link, symlink, whiteout, remove, rmdir, and rename. Rename validates that source and target nullfs mounts forward to the same lower mount before dispatching.

`null_mountctl()` handles export-setting locally through `nullfs_export()` and mount flags via `vop_stdmountctl()`.

Research notes: this is a minimal, namecache-oriented loopback layer, not a general-purpose overlay vnode framework.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/Makefile

This Makefile builds the `procfs` kernel module from the process-control, map, note, rlimit, status, subr, type, VFS, and vnode operation files.

Notably, architecture-sensitive register files (`procfs_regs.c`, `procfs_fpregs.c`, `procfs_dbregs.c`) are not listed here, implying they may be pulled in elsewhere or excluded by this module definition.

Research notes: module composition centers on pseudo-files under `/proc`, with most dispatch in `procfs_vnops.c` and read/write routing in `procfs_subr.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs.h

This header defines procfs node types and the in-memory `pfsnode`. `pfstype` enumerates root, curproc symlink, process directory, executable symlink, memory, registers, FP registers, debug registers, control, status, note, process-group note, map, executable type, cmdline, and resource limits.

`struct pfsnode` stores hash linkage, associated vnode, node type, pid, mode bits, open flags, unique file number, and a per-node lock.

The header defines helper macros for component-name matching, synthetic file-number generation, vnode/pfsnode conversion, and the `CHECKIO` authorization predicate for debugging-sensitive operations.

It declares procfs allocation/free, process lookup/release helpers, per-file handlers, register access functions, validity predicates, root lookup, and generic read/write dispatch.

Research notes: `CHECKIO` is central to security. It permits same-real-user debugging when setuid/exec restrictions are absent, or privileged override via capability checks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_ctl.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_ctl.c

This file implements writes to `/proc/<pid>/ctl`. It maps command strings such as `attach`, `detach`, `step`, `run`, and `wait`, plus signal names, to process debugging/control actions.

`procfs_control()` enforces execution-state and authorization checks, blocks tracing PID 1 at securelevel > 0, attaches by setting `P_TRACED`, reparenting to the tracer, and stopping the target, detaches by clearing tracing state and reparenting back when possible, single-steps through `procfs_sstep()`, resumes stopped processes, and waits for trace stop states.

`procfs_doctl()` accepts only writes, reads a bounded user string via `vfs_getuserstr()`, resolves it against control commands or signal names, and either calls `procfs_control()` or sends/queues a signal.

Research notes: the target process token must be held on entry. The file is debugger-sensitive and relies on `CHECKIO`, `p_trespass()`, securelevel checks, and stopped/traced process state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_ctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_dbregs.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_dbregs.c

This file implements `/proc/<pid>/dbregs` access for debug registers. `procfs_dodbregs()` rejects targets in exec, enforces `CHECKIO` and credential trespass checks, reads debug registers into `struct dbreg`, moves data through the uio, and on write updates registers only when the LWP is stopped.

`procfs_validdbregs()` hides the file for system processes.

Research notes: this is architecture-facing via `<sys/reg.h>` and external `procfs_read_dbregs()`/`procfs_write_dbregs()` implementations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_dbregs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_fpregs.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_fpregs.c

This file implements `/proc/<pid>/fpregs` access. `procfs_dofpregs()` applies exec-state, `CHECKIO`, and credential checks, reads floating-point registers into `struct fpreg`, copies them via uio, and writes them back only if the LWP is stopped.

`procfs_validfpregs()` excludes system processes.

Research notes: similar to `procfs_regs.c` and `procfs_dbregs.c`, with architecture-specific register access delegated to external helpers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_fpregs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_map.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_map.c

This file implements `/proc/<pid>/map`, producing a textual memory-map listing. `procfs_domap()` accepts reads only, builds an `sbuf` sized from requested offset/resid, locks the process VM map for iteration, temporarily releases the process token while scanning, and emits each mapping’s start/end, resident placeholder, object pointer, protections, object refcount/flags, COW state, backing object type, and resolved vnode path when available.

It handles normal and UKSMAP entries, object types such as default, vnode, swap, device, and managed device, and copes with map timestamp changes by re-looking-up the current entry.

`procfs_validmap()` hides map files for system processes.

Research notes: resident-page counting is deliberately disabled because large mappings make it impractical on 64-bit systems.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_mem.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_mem.c

This file implements `/proc/<pid>/mem` read/write access to a target process address space. `procfs_rwmem()` validates that the process is not exiting, execing, zombie, or in early allocation state, holds the vmspace, allocates one pageable kernel page of KVA, faults one target page at a time with read or write permissions, maps it into kernel space with quick pmap functions, and copies through `uiomove()`.

`procfs_domem()` wraps this with authorization: zero-length I/O succeeds, execing targets return `EAGAIN`, and unauthorized or jail-crossing access returns `EPERM`.

`procfs_findtextvp()` returns `p_textvp`, though comments note `/proc/pid/file` has information-leak concerns.

Research notes: the read/write implementation intentionally operates page-by-page. A comment warns about potential deadlock around busy pages on write faults.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_note.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_note.c

This file implements `/proc/<pid>/note` write parsing. `procfs_donote()` rejects reads, copies a bounded note string from user space using `vfs_getuserstr()`, and currently returns `EOPNOTSUPP`.

Research notes: the “send to process notify function” behavior is stubbed out, so note writes are parsed but unsupported.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_note.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_regs.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_regs.c

This file implements `/proc/<pid>/regs` access. `procfs_doregs()` rejects execing targets, enforces `CHECKIO` and credential checks, reads general registers into `struct reg`, copies through the uio, and writes back only when the process is stopped.

`procfs_validregs()` excludes system processes.

Research notes: unlike FP/debug register files, the stopped check uses process state `SSTOP` rather than `lp->lwp_stat`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_regs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_rlimit.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_rlimit.c

This file implements `/proc/<pid>/rlimit`. `procfs_dorlimit()` accepts reads only and formats every resource limit as `name current maximum`, using `-1` for `RLIM_INFINITY`.

It uses `_RLIMIT_IDENT` to expose `rlimit_ident[]` from resource headers and writes the formatted buffer via `uiomove_frombuf()`.

Research notes: the fixed 512-byte buffer is described as conservative; adding many resource limit names would require checking this assumption.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_rlimit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_status.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_status.c

This file implements `/proc/<pid>/status` and `/proc/<pid>/cmdline`. `procfs_dostatus()` accepts reads only and formats process name, pid/ppid/pgrp/session, controlling terminal, session flags, start/user/system CPU times, wait channel, uid/gid/groups, and jail hostname.

`procfs_docmdline()` emits command-line text. It prefers writable thread/process title mappings when allowed, then cached process args when allowed, then `p_comm` for other processes, and for the current process can fall back to reading `PS_STRINGS` and argv pointers from user space. Access to full args is gated by `ps_argsopen` or normal debug permissions.

Research notes: `procfs_dostatus()` uses a fixed 256-byte buffer with explicit overflow checks. `procfs_docmdline()` intentionally returns zero-length in some unavailable-argv cases to match Linux-like behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_status.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_subr.c

This file implements procfs vnode allocation, caching, process lookup helpers, generic read/write dispatch, user-string parsing, name-map lookup, and process-exit cleanup.

`procfs_allocvp()` hashes pfsnodes by pid, reuses existing vnode/pfsnode pairs for the same mount/pid/type, and allocates new vnodes with synthetic type/mode based on `pfstype`. `procfs_freevp()` removes a pfsnode from the hash and frees it.

`pfs_pfind()` and `pfs_zpfind()` return referenced processes with `p_token` held and reject processes in post-exit state. `pfs_pdone()` releases the token and process reference.

`procfs_rw()` routes reads/writes for note, regs, fpregs, dbregs, ctl, status, map, mem, type, cmdline, and rlimit. It obtains the current process from the uio thread, finds the target process, holds its first LWP, locks the pfsnode, calls the per-file handler, and posts kqueue write notes on successful writes.

`procfs_exit()` marks matching pfsnodes with `PFS_DEAD` and recycles their vnodes when a process exits, avoiding unsafe direct `vgone()` of active descriptors.

Research notes: pfsnode caching is mount-aware, because procfs can be mounted more than once. Exit handling is deliberately careful around active vnode references.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_type.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_type.c

This file implements `/proc/<pid>/etype`. `procfs_dotype()` accepts reads only, returns nothing for nonzero offsets, and emits the process emulation/sysent name followed by a newline, or `Not Available` if missing.

`procfs_validtype()` excludes system processes.

Research notes: this is a simple text pseudo-file exposing `p_sysent->sv_name`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_type.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_vfsops.c

This file implements procfs VFS operations. `procfs_mount()` rejects update mounts, registers `procfs_exit` as an exit hook when needed, marks the mount local, non-stackable, and quick-halt, assigns a new fsid, sets `f_mntfromname` to `procfs`, initializes statfs, and installs vnode ops.

`procfs_unmount()` flushes vnodes and unregisters the exit hook when the last procfs mount goes away. `procfs_root()` allocates the synthetic root vnode. `procfs_statfs()` reports page-sized block/io sizes, one block, and approximate file counts from `maxproc` and `nprocs`.

The module is registered with `VFCF_SYNTHETIC | VFCF_MPSAFE`.

Research notes: procfs has no backing storage; VFS state is almost entirely synthetic and tied to live process state.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_vnops.c

This file implements procfs vnode operations and directory topology. `procfs_vnode_vops` routes reads/writes to `procfs_rw`, lookup/readdir/readlink/getattr/open/close/ioctl/kqfilter to local handlers, and rejects creation/removal/rename-type operations with bad ops or read-only errors.

The `proc_targets` table defines process-directory entries: `.`, `..`, `mem`, `regs`, `fpregs`, `dbregs`, `ctl`, `status`, `note`, `notepg`, `map`, `etype`, `cmdline`, `rlimit`, `file`, and `exe`, with validity predicates for register/map/type files.

`procfs_lookup()` resolves root entries (`curproc`, `self`, numeric pids) and process-directory entries, applying jail visibility and `ps_showallprocs` filtering. It returns read-only errors for delete/rename/create attempts.

`procfs_readdir_root()` emits `.`, `..`, `curproc`, `self`, then visible process directories via `allproc_scan()`. `procfs_readdir_proc()` emits visible per-process target entries. `procfs_readlink()` resolves `curproc` to the current pid and `file`/`exe` to the executable path or `unknown`.

`procfs_open()` enforces exclusive write semantics and debug authorization for `Pmem`. `procfs_close()` clears exclusive flags and may clear process stop/step state on final close unless `PF_LINGER` is set. `procfs_ioctl()` implements procfs debugging ioctls for stop-event masks, flags, status, wait, and continue.

`procfs_getattr()` synthesizes attributes, masks debug-sensitive file permissions for setuid/setgid processes, sets register file sizes from register struct sizes, and reports symlink sizes for `curproc` and executable path links. Kqueue filters support read/write/vnode notifications and revoke handling.

Research notes: this is the main policy surface for procfs visibility and debugging control. Security checks are distributed across lookup/open/ioctl/read-write handlers, so changes must preserve jail, uid, setuid, and process-state restrictions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_vnops.c -->