# Group Research: group_335_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_nfs_nfs_syscalls_c__9e413a82c878

Scope confirmed against `Docs/research_subset_a.md`. All twelve listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_syscalls.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_syscalls.c

## Purpose

`nfs_syscalls.c` implements DragonFlyBSD's `nfssvc(2)` pseudo-system-call path for NFS server operation and client-side Kerberos/nickname authentication handoff. It is the user/kernel bridge used by `nfsd`, mount helper/client daemon paths, and NFS server socket setup.

## Main Contents

- `sys_nfssvc()` validates restricted-root capability, serializes on `nfs_token`, and dispatches `NFSSVC_*` commands:
  - `NFSSVC_BIOD` is obsolete and returns `ENXIO`.
  - `NFSSVC_MNTD` resolves a mount root vnode and runs `nfs_clientd()` for mount-side auth handling.
  - `NFSSVC_ADDSOCK` imports a socket fd and optional address, then calls `nfssvc_addsock()`.
  - server daemon requests pass auth results/failures into an existing `struct nfsd`, then run `nfssvc_nfsd()`.
- `nfssvc_addsock()` prepares a server socket:
  - reserves large socket buffers, disables socket autosize, clears interrupt timeouts,
  - enables TCP keepalive, `TCP_NODELAY`, and `TCP_FASTKEEP`,
  - allocates `struct nfssvc_sock`, links it into `nfssvc_sockhead`, installs receive upcall, and wakes `nfsd`.
- `nfssvc_nfsd()` is the main kernel NFS daemon loop:
  - creates/links a per-thread `struct nfsd` if needed,
  - finds sockets needing service, drains socket records, handles disconnects,
  - consults the recent-request cache, supports write gathering, executes `nfsrv3_procs[]`,
  - prepends record markers for stream transports, sends replies, logs RTT data, and cleans descriptors.
- `nfsrv_zapsock()` invalidates and shuts down a service socket, clears upcalls, frees raw mbufs, queued records, UID auth cache entries, and gathered write descriptors.
- `nfsrv_slpref()`, `nfsrv_slpderef()`, `nfs_slplock()`, and `nfs_slpunlock()` manage service-socket references and send/receive serialization.
- `nfsrv_init()` initializes or tears down all server socket and daemon queues, including recent-request cache cleanup when terminating.
- `nfsd_rt()` records server-side RTT/performance log entries.
- `nfs_getauth()`, `nfs_getnickauth()`, and `nfs_savenickauth()` implement the client-side Kerberos-style full-auth and nickname-auth cache handoff machinery.

## Notable Details

- The file is compiled with substantial server logic excluded under `NFS_NOSERVER`.
- `sys_nfssvc()` normalizes `EINTR` and `ERESTART` to success on return.
- The server loop intentionally drops `nfs_token` while holding the per-socket token during request processing.
- Privileged source port checks are optional via `vfs.nfs.nfs_privport`.
- Kerberos encryption blocks are stubs under `#ifdef NFSKERB`/`XXX`; non-Kerberos builds use zero timestamp verifier placeholders.
- `nfsrv_zapsock()` increments/decrements references indirectly so sockets are invalidated before final object free, avoiding use-after-free while daemons are active.

## Integration

This file ties server sockets and daemon scheduling to `nfs_socket.c`, request dispatch in `nfs_serv.c`, duplicate-request caching in `nfs_srvcache.c`, marshalling helpers in `nfsm_subs.c`, and mount/auth state in `nfsmount.h`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_vfsops.c

## Purpose

`nfs_vfsops.c` implements the VFS-level NFS filesystem operations: mount, root lookup, unmount, statfs/statvfs, sync, mountroot, diskless boot conversion, mount option decoding, and NFS mount structure allocation/freeing.

## Main Contents

- Registers the `nfs` VFS with `VFS_SET(..., VFCF_NETWORK | VFCF_MPSAFE)` and supplies `nfs_mount`, `nfs_unmount`, `nfs_root`, `nfs_statfs`, `nfs_statvfs`, `nfs_sync`, `nfs_init`, and `nfs_uninit`.
- Defines NFS malloc types and global `nfsstats`, plus sysctls for stats, IP paranoia/no-connection defaulting, debug, diskless state, and tunable I/O size.
- `nfs_iosize()` chooses page-aligned transfer sizes based on NFS version and transport.
- `nfs_convert_oargs()` and `nfs_convert_diskless()` translate old NFS mount/diskless structs into current NFSv3-capable forms. Converted loader-provided v2 root/swap handles are forcibly disabled for this snapshot.
- `nfs_statfs()` and `nfs_statvfs()` issue `NFSPROC_FSSTAT`, decode v2/v3 stat structures, and preserve mount-derived fields such as `f_iosize`.
- `nfs_fsinfo()` issues NFSv3 `FSINFO`, adjusts read/write/readdir sizes and maximum file size, marks `NFSSTA_GOTFSINFO`, and updates mount `f_iosize`.
- `nfs_mountroot()` configures network boot state, interface address, optional default gateway, NFSv3 root mount, optional NFS swap vnode, hostname, and root time.
- `nfs_mountdiskless()` allocates a root mount if needed, optionally performs mount RPC file-handle discovery, and calls `mountnfs()`.
- `nfs_decode_args()` normalizes and clamps mount options: v3-only flags, no-connection semantics, timeouts, retransmits, transfer sizes, attribute cache timers, group count, readahead, dead-server threshold, and reserved-port reconnect behavior.
- `nfs_mount()` copies user mount arguments, handles old-argument compatibility when enabled, supports update mounts, copies file handles/paths/hostnames, imports server sockaddr, and calls `mountnfs()`.
- `mountnfs()` allocates `struct nfsmount`, initializes locks/queues/token/object cache, defaults mount parameters, connects UDP mounts, installs vnode ops, obtains the root `nfsnode`, adds the mount to `nfs_mountq`, and starts NFS I/O reader/writer kernel threads.
- `nfs_unmount()` supports forced unmount cancellation, handshakes unmount-in-progress state, flushes vnodes, stops I/O threads, disconnects sockets, removes mount queue entry, and frees mount data when not Kerberos-held.
- `nfs_root()` obtains the root `nfsnode`, fetches FSINFO or attributes, marks the vnode as `VDIR`/`VROOT`, and returns it.
- `nfs_sync()` scans mount vnodes and calls `VOP_FSYNC()` unless lazy sync is requested.

## Notable Details

- NFSv3 is required for `nfs_mountroot()` by explicitly setting `NFSMNT_NFSV3`; root readdirplus is also enabled.
- `mountnfs()` keeps an extra reference on the root vnode to support `..` traversal if the root nfsnode would otherwise be flushed.
- `nfs_decode_args()` avoids changing buffer-cache-sensitive sizes after FSINFO has been obtained.
- Diskless swap is represented by a fake mount and then forced to a regular-file vnode before `swaponvp()`.
- Mounts create dedicated `nfsiod_rx` and `nfsiod_tx` LWKT threads with CPU placement based on CPU count.

## Integration

This file is the VFS anchor for the NFS client. It creates `struct nfsmount` instances consumed by `nfs_socket.c`, `nfs_bio.c`, `nfs_vnops.c`, and `nfsm_subs.c`, and installs vnode operation tables defined in `nfs_vnops.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_vnops.c

## Purpose

`nfs_vnops.c` implements the vnode operation layer for NFSv2/NFSv3 client files, directories, symlinks, special devices, and FIFOs. It translates VFS operations into NFS RPCs and coordinates local cache, buffer, namecache, credential, and weak-cache-consistency state.

## Vnode Operation Tables

- `nfsv2_vnode_vops` supplies normal file/directory operations: access, open/close, getattr/setattr, read/write, lookup/nresolve, create/mknod/remove/rename/link/symlink/mkdir/rmdir, readdir, strategy, fsync, reclaim/inactive, kqueue filter.
- `nfsv2_spec_vops` wraps special-device access, close, fsync, getattr, inactive, print, reclaim, setattr, with no direct read/write.
- `nfsv2_fifo_vops` delegates FIFO behavior to fifofs while preserving NFS metadata updates.

## Main Client Operations

- Access/open/close:
  - `nfs_access()` maps VFS access bits to NFSv3 `ACCESS`, caches access results by UID, falls back to local attribute checks for v2, and saves validated read/write credentials.
  - `nfs_open()` validates types, updates stored credentials, reconciles local vs remote modifications, and invalidates buffers when needed.
  - `nfs_close()` flushes dirty regular-file buffers; v3 may write-only or write+commit depending on `nfsv3_commit_on_close`.
- Attributes:
  - `nfs_getattr()` serves cached attributes, optionally refreshes via v3 `ACCESS`, then performs `GETATTR`.
  - `nfs_setattr()` handles truncation, readonly checks, time changes, write flushes, local size rollback on error, and calls `nfs_setattrrpc()`.
  - `nfs_setattrrpc()` encodes v2/v3 setattr requests and decodes v3 WCC data or v2 attributes.
- Lookup/namecache:
  - `nfs_nresolve()` is the newer namecache resolver using `LOOKUP`, negative/positive timeout caching, file-handle conversion, and v3 postop attrs.
  - `nfs_lookup()` is the old lookup API, still present for incomplete new-API coverage, handling parent locking, dotdot, rename/delete/create semantics, and NFS file-handle matching.
  - `nfs_lookitup()` is an internal helper for retry lookup, sillyrename, and v2/v3 fallback cases.
- Data I/O:
  - `nfs_read()` and `nfs_readlink()` use `nfs_bioread()`.
  - `nfs_readlinkrpc_uio()`, `nfs_readrpc_uio()`, and `nfs_writerpc_uio()` issue synchronous READLINK/READ/WRITE RPCs and handle v2/v3 differences, short reads, EOF, zero-fill, write verifiers, and commit requirements.
  - `nfs_strategy()` pushes a bio and routes sync I/O directly to `nfs_doio()` or async I/O to `nfs_asyncio()`.
  - `nfs_bmap()` is an identity mapping because NFS uses byte offsets, not local disk block mapping.
- Directory operations:
  - `nfs_readdir()` validates directory state, consults EOF cache, and uses buffered reads.
  - `nfs_readdirrpc_uio()` converts NFS READDIR replies into `struct nfs_dirent` records and maintains logical-offset-to-cookie mappings.
  - `nfs_readdirplusrpc_uio()` additionally populates namecache/vnode entries from returned attributes and file handles when safe.
- Mutating namespace operations:
  - `nfs_create()`, `nfs_mknodrpc()`, `nfs_mknod()`, `nfs_symlink()`, and `nfs_mkdir()` encode create-style RPCs and fall back to lookup when replies lack usable file handles.
  - `nfs_remove()` implements stateless-NFS-compatible sillyrename for active unlinked files.
  - `nfs_removeit()` and `nfs_removerpc()` remove delayed sillyrename names.
  - `nfs_rename()` handles cross-device checks, optional flush-before-rename, target sillyrename, notifications, and retry `ENOENT` mapping.
  - `nfs_link()` issues hard-link RPCs and optionally flushes source data before linking.
  - `nfs_rmdir()` issues directory removal and maps retry `ENOENT` to success.
- Flush/commit:
  - `nfs_fsync()` calls `nfs_flush(..., commit=1)`.
  - `nfs_flush()` scans dirty buffer trees, writes new dirty buffers, optionally performs NFSv3 COMMIT on `B_NEEDCOMMIT` buffers, waits for pending writes, handles interruptible mounts, and reports deferred write errors.
  - `nfs_flush_bp()` and `nfs_flush_docommit()` collect commit ranges and complete or re-dirty buffers based on commit outcome.
  - `nfs_commitrpc_uio()` issues NFSv3 COMMIT and validates write verifiers.
- Miscellaneous:
  - `nfs_advlock()` uses local `lf_advlock()` as a placeholder for absent lockd integration.
  - FIFO wrappers track access/update times and call fifofs operations.
  - Kqueue filter support wires read/write/vnode knotes to vnode pollinfo.

## Notable Details

- The file uses `nm_token` widely to serialize mount-local NFS client state.
- Multiple sysctls tune correctness/performance tradeoffs: rename flushing, hard-link flushing, access cache timeout, positive/negative namecache timeout, and close-time v3 commit.
- Several retry kludges intentionally map idempotency/race responses to success, such as `ENOENT` after retransmitted remove/rename and `EEXIST` after create/link/mkdir/symlink retries.
- Directory cookies are maintained in block-sized logical offset maps, and missing cookies are treated as `NFSERR_BAD_COOKIE`.
- NFSv2 READDIR is called out as unsafe for HAMMER-style directory cookies.
- Readdirplus avoids caching degenerate `.`/`..` names and identical directory file handles.
- `nfs_flush()` uses negative error values internally because RB scan callbacks use negative returns to stop scans.

## Integration

This file is the main consumer of `nfsm_subs.c` request-building/parsing helpers, `nfsnode.h` per-vnode state, `nfsmount.h` mount state, `nfs_bio.c` buffer I/O, and `nfs_node.c` nfsnode allocation/cache functions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsdiskless.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsdiskless.h

## Purpose

`nfsdiskless.h` defines boot-time data structures used to bring up an NFS-root or diskless DragonFlyBSD client. These structures carry network interface, gateway, server address, root/swap path, file-handle, credential, and hostname data from bootstrap code into `nfs_mountroot()`.

## Main Contents

- `struct nfsv3_diskless` is the current NFSv3-capable diskless configuration:
  - default interface and gateway,
  - NFS mount args and variable-length file handles for swap and root,
  - server socket addresses and hostnames,
  - swap block count and credentials,
  - root timestamp and client hostname.
- `struct onfs_args` preserves old pre-current NFS mount argument layout.
- `struct nfs_diskless` preserves the older NFSv2-style diskless boot structure with fixed 32-byte root/swap file handles.

## Notable Details

- The header documents that fields are stored in network byte order to avoid client/server byte-order issues.
- The newer `nfsv3_diskless` can hold up to `NFSX_V3FHMAX` file handles, while the legacy structure is fixed to `NFSX_V2FH`.
- Runtime conversion from `nfs_diskless` to `nfsv3_diskless` is implemented in `nfs_vfsops.c`.

## Integration

Consumed by `nfs_vfsops.c` for NFS root mounting and legacy diskless-boot conversion. It depends on NFS argument and protocol constants from the surrounding NFS headers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsdiskless.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsm_subs.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsm_subs.c

## Purpose

`nfsm_subs.c` implements the mbuf/XDR marshalling and unmarshalling helper routines used by both NFS client and server code. It builds RPC headers, appends file handles/strings/uio/bio payloads, parses replies and requests, handles weak cache consistency fields, and formats server replies.

## Main Contents

- Request construction:
  - `nfsm_reqhead()` starts an NFS request mbuf chain.
  - `nfsm_rpchead()` builds the SunRPC call header, assigns XIDs, maps generic NFS proc ids to v2/v3, and encodes UNIX or Kerberos auth plus verifier.
  - `nfsm_build()` appends fixed-size fields to the current mbuf.
  - `nfsm_fhtom()`, `nfsm_srvfhtom()`, and `nfsm_srvpostop_fh()` encode client/server file handles.
  - `nfsm_strtom()` and `nfsm_strtmbuf()` encode counted, padded NFS strings.
  - `nfsm_uiotom()`/`nfsm_biotom()` and lower-level `nfsm_uiotombuf()`/`nfsm_biotombuf()` copy uio or bio payloads into mbuf chains.
- Reply/request parsing:
  - `nfsm_dissect()` extracts fixed-size fields, using `nfsm_disct()` when data spans mbufs.
  - `nfsm_getfh()` parses v2/v3 file handles.
  - `nfsm_mtofh()` parses optional v3 post-op file handles, creates/gets nfsnodes, and loads attributes.
  - `nfsm_strsiz()`, `nfsm_srvstrsiz()`, and `nfsm_srvnamesiz()` validate counted string lengths.
  - `nfsm_mtouio()`/`nfsm_mtobio()` and lower-level `nfsm_mbuftouio()`/`nfsm_mbuftobio()` copy mbuf payloads into uio or bio buffers.
  - `nfsm_adv()` and `nfs_adv()` skip padded data in mbuf chains.
  - `nfsm_srvmtofh()` parses server-side file handles from client requests.
  - `nfsm_srvsattr()` parses NFSv3 setattr structures into `struct vattr`.
- Request execution:
  - `nfsm_request()` initializes `struct nfsm_info` and runs `nfs_request()` synchronously to completion.
  - `nfsm_request_bio()` starts the state machine for async BIO-backed operations and completes the BIO itself on early failure.
- Attribute and WCC handling:
  - `nfsm_loadattr()` updates the attribute cache from reply data.
  - `nfsm_postop_attr()` handles optional NFSv3 post-operation attributes.
  - `nfsm_wcc_data()` decodes v3 weak-cache-consistency data and marks `NRMODIFIED` when server-side before-time mismatches local expectations.
  - `nfsm_v3attrbuild()` builds NFSv3 setattr fields from `struct vattr`.
- Server reply formatting:
  - `nfsm_reply()` and `nfsm_writereply()` build RPC reply headers.
  - `nfsm_srvwcc_data()`, `nfsm_srvpostop_attr()`, and `nfsm_srvfattr()` encode v3 WCC/postop attributes and v2/v3 file attributes.

## Notable Details

- XID generation starts from `krandom()` and uses `atomic_fetchadd_int()`, avoiding zero.
- Helper routines commonly free `info->mrep` or `info->mreq` on parse/build failures to simplify caller cleanup.
- `nfsm_disct()` may splice a new mbuf into the reply chain to create contiguous data for fields crossing mbuf boundaries.
- Many routines assume NFS's 4-byte XDR padding and use `nfsm_rndup()`.
- `nfsm_uiotombuf()` asserts a single iovec under diagnostic builds.
- `nfsm_srvfattr()` clamps link counts above 65535, reflecting NFS field-size behavior.
- Server-side name parsing distinguishes malformed RPC (`EBADRPC`) from valid NFS errors such as `NFSERR_NAMETOL`.

## Integration

This is the central utility layer for `nfs_vnops.c`, `nfs_vfsops.c`, server procedures in `nfs_serv.c`, socket/request state in `nfs_socket.c`, and cache/attribute handling in `nfs_node.c` and related NFS modules.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsm_subs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsm_subs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsm_subs.h

## Purpose

`nfsm_subs.h` declares the NFS marshalling state machine, helper macros, `struct nfsm_info`, and all exported mbuf/XDR helper functions implemented in `nfsm_subs.c`.

## Main Contents

- `enum nfsm_state` defines request state-machine phases:
  - setup, auth, try, wait reply, process reply, done.
- `struct nfsm_info` holds:
  - mbuf construction/parsing pointers (`mb`, `md`, `mrep`, `mreq`, `bpos`, `dpos`),
  - v2/v3 flag,
  - request state-machine fields (`procnum`, vnode, thread, credentials, `nfsreq`, `nfsmount`, error),
  - optional async BIO completion data and writerpc commit state.
- Error-flow macros:
  - `NULLOUT`, `NEGATIVEOUT`, `NEGKEEPOUT`, `NEGREPLYOUT`, and `ERROROUT` standardize `goto nfsmout` cleanup patterns.
- Function prototypes cover request/reply building, file handles, attributes, WCC, strings, uio/bio conversion, mbuf skipping, server reply attributes, and `nfs_request()`.
- `nfsm_clget()` lazily extends mbuf clusters during server reply construction.
- `nfsm_rndup()` rounds XDR fields to 4-byte boundaries.
- `NFSV3_WCCRATTR` and `NFSV3_WCCCHK` select WCC interpretation behavior.

## Notable Details

- The macros assume caller-local variables named `error`, `info`, `nfsd`, and/or `slp` depending on macro.
- `struct nfsm_info` is shared by synchronous vnode RPCs, async BIO RPCs, and server-side encoding paths.
- The header is intentionally low-level and dangerous outside the NFS code because helpers mutate mbuf chains and cleanup ownership.

## Integration

Included by most NFS client/server implementation files. It provides the common ABI between high-level NFS operations and the request state machine in `nfs_socket.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsm_subs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsmount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsmount.h

## Purpose

`nfsmount.h` defines `struct nfsmount`, the per-mount NFS client state object stored in `mount->mnt_data`, plus mount service thread state and kernel helper declarations.

## Main Contents

- `enum nfssvc_state` tracks NFS I/O service lifecycle: init, waiting, pending, stopping, done.
- `struct nfsmount` stores:
  - mount flags and internal state,
  - receive/transmit locks, I/O threads, and thread states,
  - associated `struct mount` and per-mount nfsnode allocator,
  - root file handle and server sockaddr/socket/protocol data,
  - timeout, retry, RTT, congestion, and dead-server tracking,
  - read/write/readdir transfer sizes and readahead,
  - attribute cache timer bounds,
  - auth handoff fields and Kerberos/write verifier state,
  - UID nickname auth cache hash/LRU lists,
  - async bio and request queues,
  - maximum file size, root credential, and mount token.
- `VFSTONFS(mp)` casts a VFS mount to its NFS mount state.
- Kernel declarations expose `nfs_free_mount()` and `nfs_setvtype()`.

## Notable Details

- The structure is the central synchronization and queueing object for NFS client I/O.
- It carries both socket transport state and VFS/cache policy state.
- Multiple queues split BIOs, transmit requests, receive requests, and pending requests.
- `nm_token` protects mount-local NFS state across vnode, socket, and bio code.

## Integration

Allocated and initialized in `nfs_vfsops.c`; used throughout `nfs_vnops.c`, `nfs_bio.c`, `nfs_socket.c`, `nfs_iod.c`, and marshalling helpers via `VFSTONFS()`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsmountrpc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsmountrpc.h

## Purpose

`nfsmountrpc.h` declares helper routines used during NFS root/diskless boot mount RPC discovery and option parsing.

## Main Contents

- `md_mount()` performs mount-daemon RPC lookup for a path and returns a file handle, handle size, and adjusted NFS args.
- `md_lookup_swap()` performs similar lookup for an NFS swap path.
- `nfs_mountopts()` parses/sets NFS mount options into `struct nfs_args`.
- `setfs()` parses/sets server address/path information.

## Notable Details

- This header has no include guard in the read file.
- It is specific to mount-time support, not normal vnode operation.
- The declarations use IPv4 `struct sockaddr_in`, matching diskless-root comments that this path is AF_INET-only.

## Integration

Consumed by `nfs_vfsops.c` for `nfs_mountdiskless()` when no loader-provided root/swap file handle is available, with implementations in `nfs_mountrpc.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsmountrpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsnode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsnode.h

## Purpose

`nfsnode.h` defines the per-vnode NFS client object, directory-cookie cache records, sillyrename state, cached directory entry format, vnode conversion macros, inline helpers, and vnode operation prototypes.

## Main Contents

- `struct sillyrename` stores delayed remove state for active unlinked files: credential, directory vnode, generated name length, and generated `.nfs...` name.
- `struct nfs_dirent` is the internal directory-entry format stored in NFS directory buffers.
- `struct nfsdmap` maps logical directory offsets to NFS cookies in groups of `NFSNUMCOOKIES`.
- `struct nfsnode` stores:
  - hash entry, current file size, cached revision, cached `vattr`, and attribute timestamp,
  - NFSv3 access cache fields,
  - last known mtime/ctime and lease expiry,
  - file handle pointer/inline file handle and size,
  - validated read/write credentials,
  - owning vnode, advisory lock state, saved write error,
  - unioned special-file time fields or directory cookie verifier/EOF/cookie list,
  - node flags and resize lock.
- Macros alias union fields for file vs directory use and convert `vnode`/`nfsnode`.
- Flags include flush-in-progress/wanted, local modified, write error, removed, special-file access/update/change, and remote modified.
- Inline helpers:
  - `nfs_rslock()`/`nfs_rsunlock()` serialize file-size changes.
  - `nfs_vpcred()` chooses stored write/read credentials or falls back to mount root credential.
- Prototypes expose write/inactive/reclaim/flush, sillyremove, nfsnode lookup, cookie lookup, and directory invalidation.

## Notable Details

- `NWANTED` is defined with the same bit value as `NACC` (`0x0100`), which is notable if both symbolic uses survive in code paths.
- File handles up to `NFS_SMALLFH` are stored inline; larger handles can be heap allocated, though `NFS_SMALLFH` defaults to 64.
- DragonFly does not pass ucreds directly to read/write vnode ops, so successful access/open stores credentials in the nfsnode for later I/O RPCs.

## Integration

Used by vnode operations in `nfs_vnops.c`, nfsnode allocation in `nfs_node.c`, buffer I/O in `nfs_bio.c`, and marshalling helpers that encode vnode file handles.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsproto.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsproto.h

## Purpose

`nfsproto.h` defines wire-level NFSv2/NFSv3 constants, procedure numbers, error codes, XDR field sizes, type conversion macros, file handle representation, and packed protocol structures.

## Main Contents

- Protocol constants:
  - NFS port/program/version IDs,
  - max transfer/path/name/header/packet sizes,
  - NFS block accounting size.
- Error constants:
  - standard v2/v3 NFS errors,
  - v3-only extended errors,
  - DragonFly-internal markers such as `NFSERR_RETVOID`, `NFSERR_AUTHERR`, `NFSERR_RETERR`, and fake `NFSERR_STALEWRITEVERF`.
- XDR size constants for v2/v3 file handles, attributes, setattr, cookies, statfs, fsinfo, pathconf, WCC, write verifier, and create verifier.
- Generic NFS procedure numbers and mapped actual NFSv2 procedure numbers.
- NFSv3 operation constants:
  - setattr time modes,
  - access bitmask values,
  - write commitment levels,
  - create modes,
  - fsinfo property bits.
- Conversion macros map vnode mode/type values to NFSv2/NFSv3 wire values and back.
- `nfstype` enumerates NFS file types.
- `union nfsfh` and `nfsfh_t` define file handle storage.
- Time, 64-bit integer, quad conversion, and special-device structs model packed wire fields.
- `struct nfs_fattr` represents v2/v3 file attributes via a union with accessor macros.
- `struct nfsv2_sattr`, `struct nfsv3_sattr`, `struct nfs_statfs`, `struct nfsv3_fsinfo`, and `struct nfsv3_pathconf` define key protocol payloads.

## Notable Details

- Protocol structs avoid native `quad` fields and use arrays/packed 32-bit components for XDR density.
- `NFSX_FH(v3)` reserves maximum v3 file-handle size plus length field on the client side, while server-side `NFSX_SRVFH(v3)` uses local `fhandle_t` size.
- Generic procedure IDs are used internally, then mapped to v2 wire procedure numbers when needed.
- NFSv2 FIFO mode is encoded as a character-device mode for compatibility.

## Integration

Included by nearly every NFS module. It is the shared contract between NFS marshalling (`nfsm_subs.c`), client vnode/VFS logic, server handlers, and socket/RPC code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsproto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsrtt.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsrtt.h

## Purpose

`nfsrtt.h` defines optional circular performance-monitor logs for NFS client RPC round-trip timing and NFS server response timing.

## Main Contents

- `NFSRTTLOGSIZ` sets both logs to 128 entries.
- `struct nfsrtt` stores client-side completion-order RPC timing entries:
  - procedure id, measured RTT, timeout, in-flight count, congestion window, smoothed RTT, deviation, mount fsid, timestamp.
- Server-side `DRT_*` flags identify NQNFS, TCP transport, cached reply, cached drop, and NFSv3 use.
- `struct nfsdrt` stores server-side reply-time entries:
  - flags, procedure id, client IP address, response time in microseconds, timestamp.

## Notable Details

- The log `pos` field is the next write position, so chronological traversal wraps around the circular buffer.
- Logging is controlled externally by global `nfsrtton`.
- Server log uses `INADDR_ANY` to represent non-IP clients.

## Integration

Server-side entries are written by `nfsd_rt()` in `nfs_syscalls.c`; client-side logging is used by the request/socket path outside this header.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsrtt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsrvcache.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsrvcache.h

## Purpose

`nfsrvcache.h` defines the server recent-request cache entry structure, cache size bounds, states, return codes, and flags used to suppress duplicate NFS request execution and replay cached replies.

## Main Contents

- Cache size bounds:
  - `NFSRVCACHE_MAX_SIZE` is 2048.
  - `NFSRVCACHE_MIN_SIZE` is 64.
- `struct nfsrvcache` stores:
  - LRU and hash links,
  - RPC XID,
  - cached reply mbuf or cached reply status,
  - client host address,
  - RPC procedure number,
  - request state,
  - flag bits.
- Accessor macros alias reply/status and address union fields.
- Request states:
  - `RC_UNUSED`,
  - `RC_INPROG`,
  - `RC_DONE`.
- Cache lookup return decisions:
  - `RC_DROPIT`,
  - `RC_REPLY`,
  - `RC_DOIT`,
  - `RC_CHECKIT`.
- Flags track locking/waiting, reply representation, NQNFS, and address representation.

## Notable Details

- Cached replies may be stored either as an mbuf chain or as a status code.
- Address storage supports compact IPv4 address or full sockaddr-like name via `union nethostaddr`.
- Return values directly drive the server loop in `nfssvc_nfsd()`.

## Integration

Used by server duplicate-request cache implementation in `nfs_srvcache.c` and by `nfs_syscalls.c` when deciding whether to execute, reply from cache, or drop an incoming RPC.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsrvcache.h -->