# Group Research: group_1033_linux_stable_sources_os_linux_linux_stable_fs_nfsd_nfsctl_c_sources_ab15c17a5963

Scope: `Docs/research_subset_a.md`; all listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsctl.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsctl.c

## Summary
Implements NFSD’s administrative control surface. It backs the `nfsd` pseudo-filesystem transaction files, legacy `/proc/fs/nfs/exports`, generic netlink control operations, per-network-namespace NFSD initialization, and module init/exit.

## Main APIs
- nfsdfs transaction handlers: `write_filehandle()`, `write_unlock_ip()`, `write_unlock_fs()`, `write_threads()`, `write_pool_threads()`, `write_versions()`, `write_ports()`, `write_maxblksize()`.
- NFSv4 controls: lease time, grace time, legacy recovery dir, and `v4_end_grace`.
- nfsdfs client control directories: `nfsd_client_mkdir()`, `nfsd_client_rmdir()`, `get_nfsdfs_client()`.
- Generic netlink handlers: RPC status dump, thread set/get, version set/get, listener set/get, and pool mode set/get.
- Lifecycle: `nfsd_net_init()`, `nfsd_net_exit()`, `init_nfsd()`, `exit_nfsd()`.

## Behavior
Legacy transaction files parse text commands for threads, pool threads, versions, listener sockets/transports, filehandle generation, block size, and NFSv4 timing. Netlink provides structured replacements for server configuration, listener management, protocol version toggles, pool mode, and live RPC status reporting. Mounting `nfsd` creates control files and a `clients` directory used by NFSv4 client-state observability.

## State and Synchronization
Most service mutation is serialized by `nfsd_mutex`. Listener list surgery also uses `svc_serv->sv_lock`. Per-net setup creates export/idmap caches, proc stats, counters, callback state, write-verifier state, optional localio state, and optional filehandle signing keys. RPC status dump reads service threads under RCU and validates request fields with `rq_status_counter`.

## Risks
This file is the administrative choke point: callers must preserve the “server stopped” checks for version, lease, grace, scope, and filehandle-key changes. Listener replacement is intentionally conservative because deleting listeners while threads are active is rejected. Filehandle signing depends on `nn->fh_key` being configured before signed handles are verified or emitted.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsd.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsd.h

## Summary
Central NFSD header collecting service constants, service entry points, NFS status constants, NFSv4 attribute masks, and compile-time stubs for optional features.

## Contents
Defines NFSD protocol version bounds, block-size limits, compound sizing constants, server thread helpers, nfsdfs client directory helpers, version toggling APIs, debugfs hooks, IO mode globals, lockd hooks, NFSv4 state lifecycle declarations, and pre-XDR’d `nfserr_*` status macros.

## Important Details
`nfsd_programs[]` and `nfsd_version{2,3,4}` are declared here for SunRPC service registration. `struct nfsd_thread_local_info` carries per-thread duplicate-reply-cache state. `nfsd_v4client()` and `nfsd_user_namespace()` are shared helpers used by protocol and XDR code. NFSv4 supported, writable, and exclusive-create attribute masks are centralized here.

## Risks
This header is a broad internal contract. Changes to error macros, attribute masks, version constants, or optional-feature stubs affect many protocol files. Attribute masks must remain aligned with XDR decoding/encoding support, or clients can be told an attribute is supported when NFSD cannot process it correctly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsfh.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsfh.c

## Summary
Implements NFSD filehandle verification, composition, update, release, and attribute capture. It translates on-the-wire filehandle bytes into exports/dentries and enforces export security before VFS operations proceed.

## Main APIs
- `fh_verify()` and `fh_verify_local()`.
- `fh_compose()` and `fh_update()`.
- `fh_getattr()`, `fh_fill_pre_attrs()`, `fh_fill_post_attrs()`, `fh_fill_both_attrs()`.
- `fh_put()`, `SVCFH_fmt()`, `fsid_source()`, `nfsd4_change_attribute()`.

## Behavior
Verification decodes the fsid portion, finds the matching export, optionally verifies a SipHash MAC on signed filehandles, decodes the fileid via `exportfs_decode_fh_raw()`, checks pseudoroot rules, sets export credentials, checks secure-port/xprtsec/security-flavor policy, and finally checks NFSD permissions. Composition chooses an fsid encoding from the reference handle, export fsid, UUID, or device identity, then encodes the filesystem-specific fileid and optional MAC.

## State and Synchronization
Each `svc_fh` owns dentry/export references until `fh_put()`. Write operations use `fh_want_write()`/`fh_drop_write()` mount write protection. Weak cache consistency data is captured in the filehandle around mutating operations. NFSv4 change attributes combine change cookies with ctime for non-monotonic regular-file counters.

## Risks
Filehandle correctness depends on matching fsid type, export policy, subtree-check acceptability, and optional MAC handling. `fh_verify()` can be called repeatedly on one handle with different access modes, so callers must still call `fh_put()` exactly once when done. Signed filehandles become stale if `fh_key` is absent or changed unexpectedly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsfh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsfh.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsfh.h

## Summary
Defines NFSD’s internal and wire filehandle structures plus helper APIs for filehandle manipulation.

## Contents
`struct knfsd_fh` stores raw handle bytes and current size. `struct svc_fh` wraps the raw handle with validated dentry/export references, write-mount state, WCC flags, pre/post attributes, NFSv4 change attributes, and readdir-cookie capability flags. The header defines fsid encodings, fsid-source classification, `mk_fsid()`, `key_len()`, copy/init/match helpers, write-protection helpers, and filehandle hashing.

## Important Details
Filehandle bytes begin with version, auth type, fsid type, and fileid type. Supported fsid encodings include device, explicit numeric fsid, deprecated major/minor, encoded device, UUID-derived, and UUID+inode forms. `fh_copy()` warns if the source has a validated dentry because it is intended for raw/unverified handles.

## Risks
The raw filehandle format is an ABI. Host-endian and network-endian historical encodings coexist, so changes to `mk_fsid()` or `key_len()` can break old clients or export-cache lookup. `fh_want_write()` requires paired `fh_drop_write()`, normally through `fh_put()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsfh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsproc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsproc.c

## Summary
Implements NFSv2 server procedures and registers the NFSv2 `svc_version` dispatch table.

## Main APIs
Handlers cover NULL, GETATTR, SETATTR, ROOT, LOOKUP, READLINK, READ, WRITECACHE, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, and STATFS. `nfsd_version2` binds those handlers to XDR decoders/encoders and duplicate-reply-cache policies.

## Behavior
Each procedure translates NFSv2 arguments into shared NFSD VFS helpers, manages filehandle lifetimes, maps newer/internal NFSD errors down to NFSv2 status values, and chooses cache behavior for idempotent versus non-idempotent operations. CREATE handles NFSv2’s overloaded semantics for regular files, device nodes, FIFOs, existing files, and truncation behavior.

## State and Synchronization
Procedure-local state lives in RPC argument/response objects. Filehandle references are explicitly released after shared VFS helpers. READ and READDIR reserve response pages and payload space before encoding. Non-idempotent operations use reply-cache modes such as `RC_REPLBUFF` or `RC_REPLSTAT`.

## Risks
NFSv2 compatibility rules are subtle, especially SETATTR “touch” handling, CREATE type inference, and lossy error mapping. Missing `fh_put()` calls leak export/dentry references; premature release breaks response encoding. `nfserr_jukebox` paths set `RQ_DROPME` to force retry rather than sending an ordinary reply.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfssvc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfssvc.c

## Summary
Central NFSD service manager and dispatcher. It owns SunRPC program registration tables, protocol version enablement, service creation/destruction, per-net startup/shutdown, dynamic thread management, write verifier generation, and duplicate-reply-cache dispatch integration.

## Main APIs
- Version/service controls: `nfsd_support_version()`, `nfsd_vers()`, `nfsd_minorversion()`, `nfsd_reset_versions()`, `nfsd_create_serv()`, `nfsd_destroy_serv()`, `nfsd_svc()`.
- Thread controls: `nfsd_nrthreads()`, `nfsd_nrpools()`, `nfsd_get_nrthreads()`, `nfsd_set_nrthreads()`, `nfsd_shutdown_threads()`.
- Net refs and verifier: `nfsd_net_try_get()`, `nfsd_net_put()`, `nfsd_copy_write_verifier()`, `nfsd_reset_write_verifier()`.
- Runtime dispatch: `nfsd_dispatch()`, `nfssvc_decode_voidarg()`, `nfssvc_encode_voidres()`.

## Behavior
Startup creates a pooled SunRPC service, binds it, registers address notifiers, initializes lockd when NFSv2/v3 are enabled, starts file cache, reply cache, and NFSv4 state. The `nfsd` kernel thread loop receives RPC work, grows or shrinks worker counts opportunistically, and disposes per-net file-cache objects. Dispatch decodes arguments, marks request status fields stable for netlink observation, consults the duplicate reply cache, executes the procedure, encodes the reply, and updates the cache.

## State and Synchronization
`nfsd_mutex` protects `nn->nfsd_serv`, listener state, version configuration, and startup globals. Per-net lifetime during shutdown uses `percpu_ref` completion handshakes. Write verifier updates use a seqlock and SipHash. Address notifiers use `nfsd_notifier_lock` and a refcount shared across namespaces.

## Risks
Service teardown order matters: exports, state, reply cache, file cache, lockd, and generic resources have dependent lifetimes. Dynamic thread management relies on `svc_pool` limits and careful mutex trylock behavior. Dispatch’s `rq_status_counter` stability protocol must stay paired with parser/execution boundaries or netlink status dumps can observe inconsistent request data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfssvc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsxdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfsxdr.c

## Summary
NFSv2 XDR decoder/encoder implementation for NFSD.

## Main APIs
- Basic helpers: `svcxdr_encode_stat()`, `svcxdr_decode_fhandle()`, `svcxdr_encode_fattr()`.
- Decoders: fhandle, sattr, diropargs, read, write, create, rename, link, symlink, readdir.
- Encoders: stat, attrstat, diropres, readlink, read, readdir, statfs, directory entries.
- Release hooks: `nfssvc_release_attrstat()`, `nfssvc_release_diropres()`, `nfssvc_release_readres()`.

## Behavior
Decoding validates fixed NFSv2 filehandle sizes, component names, attribute sentinel values, user/group ids in the request namespace, read/write offsets/counts, and symlink payload placement. Encoding emits NFSv2 file attributes, including type mapping, uid/gid munging, device/fsid/fileid values, lease-adjusted mtime, opaque payload pages, and READDIR cookie backpatching.

## State and Synchronization
The code works against `xdr_stream`, RPC request pages, and `svc_fh` response objects. READ/READLINK/READDIR encoders attach page-backed payloads and mark result payload ranges for RPC accounting. Release hooks drop response filehandles after encoding.

## Risks
All buffer reservations are manual, so encode paths must fail cleanly before overrunning the response stream. Filename validation rejects embedded NUL and slash; relaxing that would affect VFS path safety. READDIR stores a cookie offset for later backpatching, so failed entry encoding must restore the previous buffer length.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfsxdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/pnfs.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/pnfs.h

## Summary
NFSD pNFS layout interface header.

## Contents
Defines pNFS device-id mapping, the `nfsd4_layout_ops` operation table, layout/device preprocessing declarations, layout insertion/return helpers, device-id helpers, and pNFS lifecycle functions. It declares block, SCSI, and flex-file layout operation providers when their configs are enabled.

## Important Details
`nfsd4_layout_ops` abstracts layoutget, getdeviceinfo, layoutcommit, encoding, client fencing, recall behavior, and notification capabilities. When `CONFIG_NFSD_PNFS` is disabled, setup/return/close/init/exit functions compile to no-ops.

## Risks
This header is the contract between NFSv4 state handling and layout-specific implementations. Layout stateids, device IDs, recalls, and fencing must agree across `state.h`, layout modules, and XDR encoding. Stub behavior must remain safe for kernels with NFSv4 but no pNFS.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/pnfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/state.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/state.h

## Summary
Defines NFSD’s NFSv4 state model: clientids, stateids, sessions, callbacks, delegations, open/lock owners, pNFS layout state, copy state, reclaim records, and blocked locks.

## Contents
Core types include `clientid_t`, `stateid_t`, `nfs4_stid`, `nfs4_client`, `nfsd4_session`, `nfsd4_slot`, `nfs4_stateowner`, `nfs4_openowner`, `nfs4_lockowner`, `nfs4_file`, `nfs4_ol_stateid`, `nfs4_delegation`, `nfs4_layout_stateid`, `nfs4_cpntf_state`, and `nfsd4_blocked_lock`.

## Important Details
Stateid status/type bits distinguish open, lock, delegation, and layout state plus closed/revoked/freeable states. Clients carry id hashes, owner hashes, stateid IDRs, delegation lists, session lists, callback state, reclaim flags, courtesy/expirable state, async copy state, and nfsdfs debug dentries. Sessions have forward slot xarrays and backchannel slot bitmaps. Delegations embed callback and CB_GETATTR state.

## Main APIs
Declares stateid lookup/preprocessing, stateid allocation/freeing, callback scheduling, client reclaim tracking, copy-notify state management, delegation conflict checks, callback net init/shutdown, state revocation, copy cancellation, and grace-period forcing.

## Risks
This header encodes many lifetime and lock contracts used by `nfs4state.c` and related modules. Refcounts span clients, sessions, stateids, owners, files, callbacks, layouts, delegations, and blocked locks. Incorrect status-bit ownership or stale stateid generation comparisons can cause replay errors, state leaks, delegation failures, or use-after-free races.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/state.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/stats.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/stats.c

## Summary
Implements `/proc/net/rpc/nfsd` statistics output and proc registration.

## Main APIs
- `nfsd_proc_stat_init()`.
- `nfsd_proc_stat_shutdown()`.
- `nfsd_show()` via `DEFINE_PROC_SHOW_ATTRIBUTE(nfsd)`.

## Behavior
The proc reader prints reply-cache hits/misses/nocache, stale filehandle count, read/write byte counters, current thread count, deprecated histogram/read-ahead placeholders, generic SunRPC service stats, and when NFSv4 is enabled, per-operation NFSv4 counters plus write-delegation GETATTR count.

## State and Synchronization
Counters are per-net `percpu_counter` values in `struct nfsd_net`. Thread count uses global `nfsd_th_cnt`. Generic RPC stats are emitted through `svc_seq_show()`.

## Risks
The output format is long-standing user ABI, including deprecated zero fields. Reordering or removing fields can break monitoring tools. Counter sums are snapshots and are not intended to be transactionally consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/stats.h -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/stats.h

## Summary
Inline helpers and declarations for NFSD statistics accounting.

## Contents
Declares proc stats init/shutdown and wraps per-net `percpu_counter` updates for reply cache hits, misses, nocache, stale filehandles, read/write bytes, payload misses, duplicate-reply-cache memory usage, and NFSv4 write-delegation GETATTR.

## Important Details
Filehandle stale and IO byte helpers update both namespace-wide counters and per-export counters when an export stats object is present.

## Risks
Callers must pass the correct `nfsd_net` and optional `svc_export` so global and per-export accounting remain aligned. These helpers are intentionally lightweight and do not perform lifetime validation on the export stats pointer beyond null checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/trace.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/trace.c

## Summary
Tracepoint definition unit for NFSD.

## Contents
Defines `CREATE_TRACE_POINTS` and includes `trace.h`, causing the tracepoint declarations in the header to instantiate storage and registration metadata in exactly one compilation unit.

## Risks
This file must remain minimal. Duplicating `CREATE_TRACE_POINTS` in another NFSD source file would create duplicate tracepoint definitions; removing this file would leave trace events declared but not defined.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/trace.c -->