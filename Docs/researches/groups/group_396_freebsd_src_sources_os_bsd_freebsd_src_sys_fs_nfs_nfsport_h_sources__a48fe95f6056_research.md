# Group Research: group_396_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_nfs_nfsport_h_sources__a48fe95f6056

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsport.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsport.h

`nfsport.h` is the FreeBSD kernel portability and integration umbrella for the in-kernel NFS implementation. It pulls in kernel, network, VM, RPC, UFS, and NFS headers, then normalizes platform-specific types and operations behind NFS-specific macros.

Key contents:
- Defines port types such as `NFSSOCKADDR_T`, `NFSPROC_T`, `NFSDEV_T`, `NFSACL_T`, and vnode operation argument aliases.
- Provides mbuf allocation wrappers (`NFSMGET`, `NFSMGETHDR`, `NFSMCLGET`, `NFSMCLGETHDR`) that sleep/retry until allocation succeeds.
- Defines NFSv4 operation numbers, callback operation numbers, synthetic/stat-only operations, NFSv4.1/v4.2 operation counts, and NFS procedure numbers through `NFSV42_NPROCS`.
- Defines exported statistics ABI structures: `nfsstatsv1`, older `nfsstatsov1`, and legacy `ext_nfsstats`.
- Under `_KERNEL`, includes the core NFS common/client/server headers and adapts FreeBSD primitives for NFS code: credentials, vnode locking, socket addresses, signal masks, memory operations, monotonic time, malloc types, device numbers, vnode tags, and lock macros.
- Defines `struct nfsvattr`, mapping NFS attribute names onto FreeBSD `struct vattr` fields while adding NFS-specific supported attributes, mounted-on fileid, and filesystem id data.
- Defines NFSv4 server stable-storage records (`nfsrv_stablefirst`, `nfst_rec`, `nfsrv_stable`) and flags used during reclaim/grace handling.
- Defines many mount state helpers and predicates such as `NFSHASNFSV3`, `NFSHASNFSV4`, `NFSHASPNFS`, `NFSHASFLEXFILE`, `NFSHASTLS`, and write-verifier/session flags.
- Provides client request wrapper `struct nfsreq`, directory block size selection, delegation eligibility macro `NFSVNO_DELEGOK`, and MDS session helpers for pNFS.

Important integration points:
- This header is intentionally broad and central; almost every in-kernel NFS file depends on its macro layer.
- Its statistics structures are ABI-sensitive because userland tooling can consume them.
- Locking macros map NFS subsystem locks to FreeBSD `struct mtx` instances and encode expected lock ownership patterns.
- Some procedure definitions overlap with `nfsproto.h`, guarded by preprocessor checks, so consumers must preserve include ordering assumptions.

Research notes:
- This file is less protocol specification than FreeBSD binding layer. It bridges generic NFS code to FreeBSD vnode, VM, socket, mbuf, mount, and credential facilities.
- Changes here can have large blast radius because it defines operation numbering, stats array sizes, lock names, malloc tags, mount-state interpretation, and function prototypes used throughout client and server code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsproto.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsproto.h

`nfsproto.h` is the protocol constants and wire-format definition header for NFSv2, NFSv3, NFSv4.0, NFSv4.1, NFSv4.2, pNFS, ACLs, extended attributes, and related RPC sizing.

Key contents:
- Defines core NFS identity and limits: `NFS_PORT`, `NFS_PROG`, callback program, versions, max path/name/data sizes, packet/XDR overhead, server max I/O defaults, and minor versions.
- Defines NFS protocol error values, including stable RFC-defined values, NFSv4.1/v4.2 additions, extended attribute errors, internal synthetic errors (`NFSERR_STALEWRITEVERF`, `NFSERR_DONTREPLY`, etc.), and RPC/authentication-tagged error values.
- Defines XDR sizes for handles, attributes, statfs/fsinfo/pathconf structures, stateids, GSS headers, device ids, file layouts, and flex-file layouts.
- Defines NFS procedure numbering across v2/v3/v4 plus synthetic client procedure identifiers for v4.1/v4.2, pNFS, extended attributes, append write, openattr, clone, and related operations.
- Defines NFSv2 actual RPC procedure numbers and NFSv4 compound/callback procedure numbers.
- Defines NFSv4 constants for locking, open claims, delegation return values, share access/deny, open result flags, file-handle volatility, access bits, write stability, create modes, exchange-id flags, sessions, sequence flags, pNFS layout types, device notifications, and callback recall-any bits.
- Under kernel builds, defines vnode-to-NFS conversion macros, `nfstype`, NFS time structs, packed 64-bit protocol representation, NFSv2/v3 attribute structs, NFSv2/v3 set-attribute structs, and NFSv4.2 IO advise hint bits.
- Defines extensive NFSv4 attribute bit numbers and masks, including supportable, settable, gettable, statfs/pathconf/readdirplus/referral groups, v4.1-only and v4.2-only attributes, POSIX draft ACL attributes, xattr support, clone block size, and change attribute type.
- Defines operation bitmaps and SP4_MACH_CRED must/allowed operation filtering macros.
- Defines in-memory helper structs for statfs, fsinfo, pathconf, NFSv4 stateids, notification bitmaps, seek contents, extended-attribute set modes, POSIX draft ACL models/scopes/tags/permissions, and change attribute types.

Important integration points:
- The error values below `10000` intentionally mirror FreeBSD `errno` values; the comments warn that changing `errno` mappings would require NFS translation changes.
- Attribute bitmap definitions are central to NFSv4 compound construction and server/client advertised capability handling.
- Wire structs avoid native 64-bit fields where alignment would make direct XDR copying unsafe.
- Procedure and operation counts drive statistics array sizing and DTrace probe arrays elsewhere in this group.

Research notes:
- This file is the primary protocol vocabulary for the FreeBSD NFS stack.
- It combines RFC-fixed values with FreeBSD-internal synthetic values; consumers must distinguish values that go on the wire from local control/status values.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsproto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsrvcache.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsrvcache.h

`nfsrvcache.h` defines the NFS server recent request cache used to detect duplicate RPC requests and replay/drop/execute them safely.

Key contents:
- Defines cache sizing bounds: `NFSRVCACHE_MAX_SIZE`, `NFSRVCACHE_MIN_SIZE`, and `NFSRVCACHE_HASHSIZE`.
- Defines `struct nfsrvcache`, with hash/list links, RPC xid, timestamp, cached reply mbuf or status, transport-specific identity, RPC procedure number, and state flags.
- Supports UDP identity via `union nethostaddr` and TCP/session-oriented identity via socket reference, request length, TCP sequence, checksum, cache time, ACK state, and refcount.
- Defines access macros for the nested reply/status/address/TCP fields.
- Defines ACK state values (`RC_NO_SEQ`, `RC_NO_ACK`, `RC_ACK`, `RC_NACK`) and cache action return values (`RC_DROPIT`, `RC_REPLY`, `RC_DOIT`).
- Defines cache flags for locking/waiting, cached reply type, transport, address family, in-progress state, NFS protocol version, reference count, and same-TCP-connection matching.
- Defines `LIST_HEAD(nfsrvhashhead, nfsrvcache)` and `struct nfsrchash_bucket`, a fine-grained locked TCP cache hash bucket.

Important integration points:
- This cache is server-side duplicate suppression and reply replay infrastructure.
- The same entry can represent either a full reply mbuf chain or only a reply status.
- Transport identity differs significantly between UDP and TCP, reflected by the `rc_un2` union.

Research notes:
- The header only defines data layout and constants; cache insertion, lookup, locking, replay, and eviction behavior live in server implementation files outside this group.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsrvcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsrvstate.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsrvstate.h

`nfsrvstate.h` defines NFSv4 server-side state structures: clients, sessions, opens, locks, delegations, layouts, local lock rollback, user/group caches, pNFS device metadata, and pNFS data-server file records.

Key contents:
- Declares list/head types for clients, states, locks, lock files, sessions, layouts, DS directories, devices, dont-list markers, and user/group cache buckets.
- Defines hash macros for clientid, stateid, uid/gid, user/group names, sessions, and layouts.
- Defines `struct nfsclient`, the server representation of an NFSv4 client, including stateid hash table, open/delegation/session lists, lease/expiry data, clientid/confirm verifiers, SP4_MACH_CRED operation bitmaps, callback info, uid/gid, client strings, callback socket request data, and flags.
- Defines `struct nfslayout`, representing pNFS layout state with stateid, clientid, file handle, device id, fsid, layout length/type/flags/mirror count, and variable XDR payload.
- Defines `struct nfsdsession`, the NFSv4.1 session object with slot table, associated client, limits, callback parameters, session id, and callback session. Comments document locking order and field-level lock responsibilities.
- Defines overloaded `struct nfsstate`, used for open owners, open files, lock owners, lock state, and delegations. It contains list/hash links, stateid, sequence, uid, flags, owner bytes, associated lock file/cache/client pointers, and union fields for open/delegation-specific metadata.
- Defines `struct nfslock`, `struct nfslockconflict`, and `struct nfsrollback` for byte-range lock state, conflict reporting, and local lock rollback.
- Defines `struct nfslockfile`, grouping opens, delegations, locks, local locks, rollback entries, file handle, local-lock serialization, and use count per file.
- Defines `struct nfsusrgrp`, a name/id/credential cache entry with numeric and name hash links plus expiry/wired state.
- Defines stable restart record header `struct nfsf_rec` and prototypes for client/delegation cleanup.
- Defines `struct nfsdevice` for pNFS data-server device info, including DS directory vnodes, host/address strings, device id, MDS fsid/stripe size, and no-space state.
- Defines old/new pNFS DS attribute records (`opnfsdsattr`, `pnfsdsattr`) and recovery dont-list entries.
- Defines pNFS DS file xattr records (`opnfsdsfile`, `pnfsdsfile`) outside the kernel-only block so on-disk/xattr layout can be shared.

Important integration points:
- This is a server state ABI/layout header internal to kernel NFS code, not just declarations.
- Locking comments on `struct nfsdsession` are critical: state lock and session-hash lock ordering prevents races during session lookup/add/delete.
- Several structs use trailing flexible/one-byte arrays and are malloced to exact size.
- pNFS metadata xattr structs encode persistent data-server layout state and must remain compatible with existing metadata.

Research notes:
- The file is foundational for NFSv4 correctness: lease recovery, stateid lookup, open/lock/delegation lifecycle, sessions, and pNFS layout/device state all depend on these layouts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsrvstate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsv4_errstr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsv4_errstr.h

`nfsv4_errstr.h` provides a small static mapping from NFSv4 protocol error values to human-readable strings.

Key contents:
- Defines `static const char *nfsv4_errstr[]`, indexed by `errval - NFSERR_BADHANDLE`, covering `NFSERR_BADHANDLE` through `NFSERR_XATTR2BIG`.
- Includes strings for core NFSv4 errors, NFSv4.1 session/pNFS errors, NFSv4.2 offload/layout errors, and extended attribute errors.
- Defines `static const char *nfsv4_geterrstr(int errval)`, which returns `NULL` if the error is outside the NFSv4 range and otherwise returns the static string.

Important integration points:
- The array size is tied to `NFSERR_XATTR2BIG - 10000`, so it depends on the contiguous NFSv4 error numbering in `nfsproto.h`.
- The header intentionally defines static storage in the including C file, with comments noting it is currently used narrowly rather than packaged as a separate library function.

Research notes:
- This is a user-facing diagnostic helper, likely for mount/client error reporting.
- Any new contiguous NFSv4 error added in `nfsproto.h` should be reflected here to keep indexing correct and messages meaningful.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsv4_errstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/rpcv2.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/rpcv2.h

`rpcv2.h` defines Sun RPC version 2 constants and NFS-adjacent RPC authentication, GSS, mount protocol, gssd, and nfsuserd values.

Key contents:
- Defines RPC version `RPC_VER2`.
- Defines authentication flavors: null, UNIX/AUTH_SYS, short, Kerberos v4, RPCSEC_GSS, and FreeBSD Kerberos GSS service pseudo-flavors for none/integrity/privacy.
- Defines auth/verifier size limits and AUTH_UNIX minimum size/gid count.
- Defines RPCSEC_GSS version, procedures, services, sequence limits/window sizes, MIC/WRAP identifiers, QOP, and GSS XDR size constants.
- Defines private RPC program/procedure values for `gssd` and `nfsuserd`.
- Provides GSS major status constants if GSS headers have not already defined them.
- Defines RPC message/reply statuses, accept/deny statuses, auth failure values, common RPC header sizes, MOUNT program values, and NFS RPC program number.
- Defines `struct rpcv2_time`.

Important integration points:
- `nfsproto.h` uses RPC error constants to build `NFSERR_RPCERR`-tagged synthetic NFS errors.
- This header supplies protocol constants used by both client and server RPC wrapping code.
- Conditional GSS status definitions avoid duplicate definition when full GSS/RPCSEC headers are present.

Research notes:
- The file is a compact compatibility/protocol-definition header for RPC pieces that NFS needs without depending entirely on userland RPC generated headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/rpcv2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/xdr_subs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/xdr_subs.h

`xdr_subs.h` defines low-level XDR conversion helpers for NFS protocol encoding/decoding.

Key contents:
- Defines scalar conversion macros `fxdr_unsigned(t, v)` and `txdr_unsigned(v)` using `ntohl()`/`htonl()`.
- Defines NFSv2 time conversion macros between XDR `struct nfsv2_time` and native `timespec`, with the special `0xffffffff` microsecond value handled as zero on decode and `tv_nsec == -1` encoded as `0xffffffff`.
- Defines NFSv3 time conversion macros using seconds and nanoseconds.
- Defines NFSv4 time conversion macros using high seconds, seconds, and nanoseconds; decode ignores high seconds and clamps nanoseconds modulo 1,000,000,000.
- Defines `fxdr_hyper(f)` to decode an unaligned XDR 64-bit unsigned value from two 32-bit words.
- Defines inline `txdr_hyper(uint64_t f, uint32_t *t)` to encode a 64-bit value into two big-endian 32-bit words.

Important integration points:
- These helpers intentionally avoid assuming alignment, which matters for XDR data inside mbuf chains.
- They are used by attribute parsing, file-size/stat fields, timestamps, and protocol marshalling throughout NFS code.

Research notes:
- The file is small but safety-critical: incorrect conversion affects wire compatibility and attribute correctness.
- Native big-endian systems rely on `ntohl()`/`htonl()` compiling away as appropriate.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfs/xdr_subs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs.h

`nfsclient/nfs.h` is the public-ish kernel client header for FreeBSD's NFS client support functions, debug hooks, and async I/O daemon state.

Key contents:
- Defines terminal print delay defaults `NFS_TPRINTF_INITIAL_DELAY` and `NFS_TPRINTF_DELAY`.
- Defines vnode mount version predicates `NFS_ISV3`, `NFS_ISV4`, and `NFS_ISV34`.
- Under `NFS_DEBUG`, defines debug categories and `NFS_DPF`; otherwise it compiles to no-op.
- Defines `enum nfsiod_state` with states for unavailable, available, and newly created-for-async-I/O nfsiod threads.
- Declares client BIO/page/cache functions: `ncl_meta_setsize`, `ncl_bioread`, `ncl_biowrite`, `ncl_vinvalbuf`, `ncl_asyncio`, `ncl_doio`.
- Declares node lifecycle/cache functions: `ncl_nhinit`, `ncl_nhuninit`, `ncl_nodelock`, `ncl_nodeunlock`, `ncl_getattrcache`.
- Declares RPC operations for read, write, readlink, readdir, readdirplus, commit, clearcommit, fsinfo.
- Declares module init/uninit and nfsiod creation functions.

Important integration points:
- This header connects vnode operations to the client-side RPC implementation and async I/O subsystem.
- The function list spans files in this group (`nfs_clbio.c`, `nfs_clnode.c`, `nfs_clnfsiod.c`) and other client RPC files outside this group.

Research notes:
- The header is declaration-focused; behavior lives in the client `.c` files.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clbio.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clbio.c

`nfs_clbio.c` implements FreeBSD NFS client VM/page and buffer-cache I/O: getpages/putpages, buffered reads/writes, direct writes, cache consistency checks, buffer invalidation, async I/O queueing, actual cache-block RPC I/O, and truncate-size handling.

Key functions and behavior:
- `ncl_getpages()` services VM page faults for NFS vnodes. It can delegate to `vfs_bio_getpages()` via the `vfs.nfs.use_buf_pager` sysctl, or perform direct `ncl_readrpc()` into mapped physical pages using a pbuf. It rejects non-cacheable direct-I/O vnodes when mmap is disallowed.
- `ncl_putpages()` writes dirty VM pages back through `VOP_WRITE()`, selecting `n_writecred` when present and trimming writes at EOF. It keeps or clears dirty state depending on write success and `nfs_keep_dirty_on_error`.
- `nfs_bioread_check_cons()` enforces approximate NFS cache consistency by comparing cached modification/size state with fresh attributes, invalidating buffers/directories when modified or stale, and forcing attribute refreshes.
- `ncl_bioread()` implements buffered reads for regular files, symlinks, and directories. It performs fsinfo initialization, max-file-size checks, optional direct read for `IO_DIRECT`, readahead when safe, directory cookie recovery on `NFSERR_BAD_COOKIE`, directory EOF tracking, and buffer-to-uio copying.
- `nfs_directio_write()` performs synchronous direct writes in chunks no larger than mount `wsize`, requiring `FILE_SYNC` and deliberately preventing write-verifier updates from hiding verifier changes from buffered writes.
- `ncl_write()` implements buffered file writes. It handles previous async write errors, fsinfo/wsize setup, append semantics, direct append/write optimization, file-size limits, commit-size pressure, buffer allocation/resizing, non-contiguous write policy, dirty range tracking, sync/async/delayed writes, and `IO_UNIT` rollback on failure.
- `nfs_getcacheblk()` wraps `getblk()` with interruptible-mount signal masking and retry behavior, returning locked cache buffers.
- `ncl_vinvalbuf()` flushes and invalidates vnode buffers/pages, coordinates with NFS exclusive vnode access, handles interruptible/forced dismount behavior, performs pNFS layout commit when needed, and clears `NMODIFIED`.
- `ncl_asyncio()` queues buffers to nfsiod worker threads. It avoids async commit overloads and readdirplus deadlocks, creates/wakes workers, limits queue growth, attaches credentials, and returns `EIO` to force synchronous I/O when no worker can service the mount.
- `ncl_doio()` is the central cache-block RPC executor for synchronous and async paths. It dispatches reads to `ncl_readrpc`, `ncl_readlinkrpc`, `ncl_readdirrpc`, or `ncl_readdirplusrpc`; dispatches writes/commits to `ncl_writerpc`/`ncl_commit`; handles unstable-write commit state; preserves recoverable dirty buffers; records unrecoverable write errors on the nfsnode; and completes buffers with `bufdone()`.
- `ncl_meta_setsize()` updates local file size for truncate/extend, truncates buffers past EOF, adjusts a straddling dirty buffer, and updates vnode pager size.

Important integration points:
- Uses mount flags and state from `nfsport.h`/`nfsmount.h`, node state from `nfsnode.h`, RPC operations declared in `nfsclient/nfs.h`, DTrace cache probes, and global stats in `nfsstatsv1`.
- The code carefully coordinates VM object state, buffer cache state, vnode locks, NFS node locks, and mount locks.
- pNFS-specific behavior appears in invalidation/layout commit handling and in mount-state checks.
- Async I/O uses `nfs_clnfsiod.c` worker state and `ncl_iod_mutex`.

Research notes:
- This is the main client data-path file in the group.
- High-risk areas are cache consistency, dirty-buffer error recovery, append/direct-I/O behavior, lock ordering, and interactions between mmap/pageout and NFSv4 close/stateid handling.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clbio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clcomsubs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clcomsubs.c

`nfs_clcomsubs.c` contains client common subroutines for mbuf/uio transfer, reply file-handle and attribute parsing, and NFSv4 client lock helper wrappers.

Key functions and behavior:
- `nfsm_uiombuf()` copies a single-iovec `uio` payload into the current NFS request mbuf chain held by `struct nfsrv_descript`. It supports ordinary mbufs and external-page mbufs, pads to XDR alignment, updates `nd_bpos`/`nd_mb`, and advances the uio.
- `nfsm_uiombuflist()` builds and returns a new mbuf chain from a single-iovec `uio`, optionally using external pages. On user-copy failure it frees the chain and returns `NULL`.
- `nfsm_loadattr()` parses post-op attributes from an NFS reply into `struct nfsvattr`. It dispatches to `nfsv4_loadattr()` for v4, decodes packed `struct nfs_fattr` for v3, and handles v2 quirks including FIFO-as-character-device representation and ctime/usec-as-generation mapping.
- `nfscl_mtofh()` extracts a file handle and optional attributes from NFSv3 or NFSv4 replies. For NFSv4 it expects GetFH and Getattr operation results; for NFSv3 it handles post-op present flags.
- `nfscl_lockinit()`, `nfscl_lockexcl()`, `nfscl_lockunlock()`, and `nfscl_lockderef()` wrap NFSv4 client state/delegation lock initialization, exclusive acquisition, release, and reference dropping/wakeup behavior.

Important integration points:
- Assumes `uio_iovcnt == 1` for mbuf-copy helpers; callers must segment larger scatter/gather writes before calling.
- Uses XDR conversion helpers from `xdr_subs.h` and protocol structs from `nfsproto.h`.
- Attribute parsing feeds cache loading and vnode attribute update paths elsewhere.
- Lock dereference uses the client state mutex macros from `nfsport.h`.

Research notes:
- This file sits between RPC marshalling/parsing macros and higher-level vnode operations.
- Error paths are important because partial mbuf/uio advancement and copyin failures can otherwise corrupt request construction.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clcomsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clkdtrace.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clkdtrace.c

`nfs_clkdtrace.c` implements the FreeBSD DTrace provider `nfscl` for NFS client logical RPC and cache events.

Key contents:
- Defines DTrace provider attributes and provider operations (`provide`, `enable`, `disable`, `getargdesc`, `destroy`).
- Defines `struct dtnfsclient_rpc`, mapping a logical NFS operation slot to NFSv4, NFSv3, and optional NFSv2 probe names and storing start/done probe ids.
- Defines the procedure-name table indexed by NFS procedure number up to `NFSV41_NPROCS + 1`, covering v2/v3/v4 operations and a final noop slot.
- Registers access-cache probes: flush done, get hit, get miss, load done.
- Registers attribute-cache probes: flush done, get hit, get miss, load done.
- Registers NFSv2, NFSv3, and NFSv4 RPC start/done probes, using sparse v2/v3 names and v4 names.
- `dtnfsclient_getargdesc()` describes probe argument types for cache probes and RPC probes. RPC done probes expose an additional integer error/status argument.
- `dtnfsclient_enable()` and `dtnfsclient_disable()` set per-probe function pointers or per-procedure probe ids used by the runtime NFS client code.
- `dtnfsclient_load()` registers the provider and installs generic NFS start/done probe function pointers.
- `dtnfsclient_unload()` clears function pointers and unregisters the provider.
- Module metadata declares dependencies on `dtrace`, `opensolaris`, `nfscl`, and `nfscommon`.

Important integration points:
- Probe arrays (`nfscl_nfs2_start_probes`, etc.) are externally allocated by the client; this provider fills ids into them.
- Procedure table sizing is tied to protocol counts from `nfsproto.h`.
- The provider traces logical NFS client operations, not necessarily one-to-one network RPC sends; comments explicitly mention auth retries, jukebox retries, and cache hits.

Research notes:
- This file is observability infrastructure. It should track procedure table changes when protocol procedure counts/names are extended.
- Incorrect argument descriptions can break DTrace consumers even if NFS behavior remains correct.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clkdtrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clkrpc.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clkrpc.c

`nfs_clkrpc.c` implements kernel RPC server-side handling for NFS client callbacks (`nfscbd`), used primarily by NFSv4 callback operations from server to client.

Key functions and behavior:
- `nfscb_program()` is the RPC dispatch entry for callback requests. It accepts only null and callback compound procedures, constructs an `nfsrv_descript`, realigns incoming mbufs, captures caller addresses and credentials, enables external-page reply handling for KTLS when available, invokes callback processing, frees request resources, and sends mbuf replies or RPC errors.
- `nfs_cbproc()` marks stream sockets when appropriate, calls `nfscl_docb()` to execute the callback, and returns cache-style reply/drop actions.
- `nfscbd_addsock()` reserves socket buffer space, steals a userland socket from its file descriptor, creates datagram or connection RPC transport, registers callback program/version, and releases the transport reference.
- `nfscbd_nfsd()` services callback daemon requests from `nfssvc()`. It optionally installs a Kerberos service principal, starts the callback service pool with fixed thread counts, clears service names on exit, and coordinates singleton operation via `nfs_numnfscbd`.
- `nfsrvd_cbinit()` initializes or tears down the callback service pool, waiting for callback daemon registrations during termination and creating the `nfscbd` service pool when absent.

Important integration points:
- Uses kernel RPC service APIs (`svc_*`, `svcpool_*`) and RPCSEC_GSS/TLS support.
- Shares server-style descriptor/caching return conventions (`RC_DROPIT`, `RC_REPLY`) even though it handles client callbacks.
- Coordinates with global `nfscbd_pool`, `nfs_numnfscbd`, and NFS daemon lock macros.
- Callback authentication is intentionally permissive in the current path; comments discuss limitations and historical AUTH_SYS callback behavior.

Research notes:
- This file is control-plane callback plumbing, not normal client outbound RPC.
- Correct resource ownership is central: incoming request mbufs, credentials, sockets stolen from userland, service pool refs, and daemon lifecycle are all managed here.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clkrpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clnfsiod.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clnfsiod.c

`nfs_clnfsiod.c` implements lifecycle management and worker loops for NFS client asynchronous I/O kernel threads (`nfsiod`).

Key contents:
- Defines global worker state: `ncl_numasync`, `ncl_iodwant[]`, and `ncl_iodmount[]`.
- Defines sysctls:
  - `vfs.nfs.iodmaxidle`: idle seconds before non-minimum workers exit.
  - `vfs.nfs.iodmin`: minimum spare workers to keep.
  - `vfs.nfs.iodmax`: maximum worker count.
  - `vfs.nfs.defect`: allow workers to migrate/defect between mounts for fairness.
- `sysctl_iodmin()` validates and applies a new minimum, creating workers synchronously if needed.
- `sysctl_iodmax()` validates and applies a new maximum, waking excess idle workers so they exit.
- `nfs_nfsiodnew_sync()` finds an unused worker slot, creates a kernel process with `kproc_create()`, and marks it available on success.
- `ncl_nfsiodnew_tq()` runs queued worker-creation requests on `taskqueue_thread`.
- `ncl_nfsiodnew()` queues async worker creation and requires the iod mutex.
- `nfsiod_setup()` fetches tunables, initializes client state, clamps initial minimum, and creates initial workers during kernel startup.
- `nfssvc_iod()` is the worker loop: waits for an assigned mount and queued buffers, exits on max shrink/idle timeout, dequeues buffers, calls `ncl_doio()` with read or write credentials, wakes queue waiters as it drains, optionally defects from mounts with multiple workers, and updates global counts on exit.

Important integration points:
- `ncl_asyncio()` in `nfs_clbio.c` queues buffers and wakes/assigns these workers.
- All worker arrays and queue counters are protected by `ncl_iod_mutex` through `NFSLOCKIOD()`.
- Mount buffer queues (`nm_bufq`, `nm_bufqlen`, `nm_bufqiods`, `nm_bufqwant`) are manipulated under the iod lock.
- Worker exit wakes waiters on `ncl_numasync` when the last worker terminates.

Research notes:
- This file is the concurrency backbone for NFS read-ahead and write-behind.
- Risk areas are queue ownership during unmount, worker shrink/idle races, and fairness behavior when multiple mounts share workers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clnfsiod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clnode.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clnode.c

`nfs_clnode.c` implements NFS client node/vnode allocation, lookup, inactive/reclaim cleanup, sillyrename cleanup, and cache invalidation.

Key functions and behavior:
- `ncl_nhinit()` creates the UMA zone for `struct nfsnode`.
- `ncl_nhuninit()` destroys the node UMA zone.
- `ncl_nget()` looks up or creates an NFS vnode/nfsnode by file handle. It hashes the file handle, searches the mount vnode hash, allocates a new node/vnode on miss, initializes mutex and exclusive lock, enables recursive/shared vnode locking, marks root vnodes, attaches the file handle, inserts into mount queue and vnode hash, and handles racing insert losers.
- `nfs_freesillyrename()` asynchronously releases the saved directory vnode and frees sillyrename state.
- `ncl_releasesillyrename()` detaches sillyrename state from non-directory vnodes, optionally invalidates buffers, removes the silly-renamed file, frees credentials, and queues directory vnode release to avoid lock-order reversal.
- `ncl_inactive()` handles last-use vnode processing. For NFSv4 regular files it clears the current open stateid, flushes dirty pages/buffers as needed before delayed close, performs `nfsrpc_close()`, releases sillyrename state, and retains only meaningful post-inactive flags (`NMODIFIED`, `NDSCOMMIT`).
- `ncl_reclaim()` performs final vnode teardown: lets NLM abort pending locks, releases sillyrename, closes remaining NFSv4 opens, returns delegations before hash removal when not unmounting, removes from vnode hash, saves delegation attributes via `nfscl_reclaimnode()`, frees directory cookie maps, write credentials, file handle, v4 node data, mutex/lock, and UMA node storage.
- `ncl_invalcaches()` invalidates all access-cache entries and the attribute cache for a vnode, firing DTrace flush probes.

Important integration points:
- Uses FreeBSD vnode hash and mount queue APIs to provide one vnode per file handle per mount.
- Coordinates with NFSv4 state management (`nfsrpc_close`, delegation return, open stateid clearing), VM/page flushing, buffer invalidation, NLM lock reclaim hook, and DTrace cache probes.
- Sillyrename cleanup is split into a taskqueue release to avoid vnode lock-order reversal when dropping the directory vnode reference.

Research notes:
- This is the client vnode lifecycle file. Correct ordering matters because vnode reclaim can race with close, delegation recall, unmount, delayed writes, NLM locks, and sillyrename cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clnode.c -->