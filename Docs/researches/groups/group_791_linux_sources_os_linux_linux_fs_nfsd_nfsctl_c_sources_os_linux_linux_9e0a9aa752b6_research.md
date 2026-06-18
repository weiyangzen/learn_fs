# Group Research: group_791_linux_sources_os_linux_linux_fs_nfsd_nfsctl_c_sources_os_linux_linux_9e0a9aa752b6

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsctl.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfsctl.c

## Summary
Implements the administrative control surface and module lifecycle for the in-kernel NFS server. It backs the `nfsd` pseudo-filesystem, legacy proc exports view, generic netlink server management APIs, per-net namespace initialization, and module init/exit sequencing.

## Main Responsibilities
- Defines transaction-style control files such as `threads`, `pool_threads`, `versions`, `portlist`, `max_block_size`, `filehandle`, lock unlock helpers, NFSv4 lease/grace controls, and cache/stat files.
- Mounts and populates the `nfsd` filesystem with control files, export views, stats, optional Kerberos enctype symlink, and `clients/` debug directories.
- Provides generic netlink handlers for server threads, listeners, enabled protocol versions, pool mode, filehandle signing key, server scope, lease/grace settings, and live RPC status dumps.
- Initializes and destroys per-network-namespace NFSD state, including exports, idmapping, proc stats, counters, callback state, localio lists, write verifier state, and filehandle signing key memory.
- Performs module-level setup and teardown for debugfs, NFSv4 slabs/pNFS/laundry work, duplicate reply cache slab, lockd callbacks, export workqueue, pernet ops, client tracking, filesystem registration, netlink family registration, proc entries, and localio hooks.

## Key Data Structures and Interfaces
- `write_op[]` maps pseudo-file inode numbers to transaction handlers.
- `transaction_ops` uses `simple_transaction_*` so reads can synthesize zero-length writes and writes return generated replies.
- `nfsd_files[]` describes the pseudo-filesystem entries and their file operations.
- `nfsd_genl_*` handlers encode and decode generic netlink attributes defined by the NFSD netlink family.
- `nfsdfs_client` references are attached to inodes under `nfsd/clients/` and released through recursive removal callbacks.
- `nfsd_net_ops` allocates per-net `struct nfsd_net` state and registers `nfsd_net_id`.

## Important Behavior
Writes to `threads` and netlink `threads_set` call `nfsd_svc()` under `nfsd_mutex`, so listener setup, version state, thread counts, and server lifetime are serialized. `pool_threads` adjusts per-pool maxima but cannot fully start the server from zero and preserves at least one thread in pool zero when used.

`versions` and netlink version configuration reject changes while `nn->nfsd_serv` exists. Text configuration supports `+N`, `-N`, and NFSv4 minor forms; netlink clears current versions then applies nested major/minor enabled attributes.

`portlist` supports three modes: read current listener names, add an existing socket file descriptor, or create IPv4/IPv6 listeners from a transport name and port. Netlink listener configuration can replace listener sets, but removing listeners is blocked while threads are active.

NFSv4 lease and grace times are bounded to 10 through 3600 seconds and are mutable only while the service is down. `v4_end_grace` allows explicit grace termination only via affirmative writes.

The RPC status dump walks all service pools and threads under RCU while using `rq_status_counter` acquire loads to avoid reporting unstable request fields. For NFSv4 compounds it includes a bounded list of operation numbers.

Filehandle signing keys are copied from netlink as two little-endian u64 values into a per-net `siphash_key_t`; setting is restricted to stopped service state by the caller.

## Dependencies
Depends on SunRPC service and transport APIs, lockd, rpc_pipefs/GSS, export and idmap caches, NFSD NFSv4 state and pNFS initialization, duplicate reply cache, filecache stats, procfs, generic netlink, fs context APIs, pernet operations, localio, and tracepoints.

## Risks and Subtleties
Most mutation paths rely on `nfsd_mutex`; adding new control paths without the same locking can race service creation, listener replacement, or version changes. The text pseudo-file ABI has legacy parsing behavior and user-visible compatibility quirks, especially around NFSv4 version reporting and transaction reads.

Listener replacement is delicate: old sockets are temporarily spliced away, possible deletes are blocked with active threads, then missing requested sockets are recreated. Error handling must avoid leaving an empty stopped service object around.

Per-net teardown frees sensitive `fh_key` memory and destroys counters/caches; lifecycle changes must preserve init/exit unwind ordering because many later resources depend on earlier pernet, workqueue, slab, and callback setup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsd.h -->
# File Research: sources/os/linux/linux/fs/nfsd/nfsd.h

## Summary
Central NFSD internal header collecting service-wide constants, public prototypes, protocol version declarations, NFS status constants, NFSv4 attribute masks, and small helpers shared across the NFS server implementation.

## Main Responsibilities
- Defines supported NFS version limits, NFSv4 minor version limit, max compound operations, and service block-size limits.
- Declares global NFSD service state and entry points for service startup, shutdown, dispatch, thread accounting, version toggles, client directories, lockd, debugfs, and NFSv4 state lifecycle.
- Provides pre-XDR big-endian NFS error constants for NFSv2/v3/v4 paths.
- Defines supported and writable NFSv4 attribute bitmaps, including pNFS, security label, POSIX ACL, and exclusive-create variants.
- Supplies helpers for user namespace selection, NFSv4 client detection, netaddr formatting, bitmap subset checks, and attribute support checks.

## Key Data Structures and Interfaces
- `struct nfsd_genl_rqstp` is a stable snapshot used by netlink RPC status reporting.
- `struct nfsd_thread_local_info` stores per-thread compound/cache metadata.
- `struct nfsdfs_client` is the refcounted object attached to client debug filesystem entries.
- `enum vers_op` abstracts version mutation/testing through `nfsd_vers()` and `nfsd_minorversion()`.
- `nfsd_suppattrs[3][3]` and the `NFSD4_*_SUPPORTED_ATTRS_WORD*` masks define supported attribute sets by NFSv4 minor.

## Important Behavior
The header intentionally normalizes status handling by exposing big-endian constants such as `nfserr_stale`, `nfserr_wrongsec`, and NFSv4-specific errors. Internal-only sentinel statuses such as `nfserr_eof`, `nfserr_replay_me`, `nfserr_replay_cache`, and `nfserr_symlink_not_dir` are allocated outside assigned protocol errors before conversion to big-endian values.

NFSv4 attribute masks are split between supported, write-only, writable, and exclusive-create sets. Optional features alter the masks at compile time, so protocol handlers should test against these helpers instead of duplicating config logic.

When `CONFIG_NFSD_V4` or related options are disabled, this header provides no-op stubs for NFSv4 lifecycle, recovery, pNFS, callback, and state-revocation hooks, allowing non-v4 builds to share call sites.

## Dependencies
Includes core NFS protocol headers, SunRPC service and transport APIs, UAPI NFSD debug definitions, export definitions, per-net NFSD state, and stats declarations.

## Risks and Subtleties
This header is a broad coupling point. Changes to error constants, version limits, or attribute masks affect many protocol paths and must remain consistent with XDR encoding, protocol specifications, and optional config stubs.

`nfsd_user_namespace()` derives the namespace from the transport credential when present; callers using request credentials for id translation should preserve that behavior for container/user-namespace correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsfh.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfsfh.c

## Summary
Implements NFSD filehandle verification, composition, release, weak cache consistency attribute capture, optional signed filehandle MACs, and NFSv4 change attribute generation.

## Main Responsibilities
- Decodes on-the-wire filehandles into exports and dentries via export cache lookup and filesystem `export_operations`.
- Performs export, subtree, secure-port, xprtsec, security flavor, type, pseudo-root, and VFS permission checks.
- Composes filehandles for replies using export fsid policy, filesystem file identifiers, reference filehandles, UUID/device/fsid encodings, and optional SipHash MAC signing.
- Maintains `svc_fh` lifetime, including dentry/export references, mount write access, and pre/post operation attributes.
- Generates NFSv4 change attributes from `STATX_CHANGE_COOKIE` and ctime fallback/mitigation.

## Key Data Structures and Interfaces
- `nfsd_set_fh_dentry()` maps `knfsd_fh` content to `fh_export` and `fh_dentry`.
- `__fh_verify()` is the core verifier behind RPC `fh_verify()` and non-RPC `fh_verify_local()`.
- `fh_compose()` builds a new `svc_fh` for a dentry/export pair.
- `fh_update()` finalizes filehandles after create operations that started from negative dentries.
- `fh_fill_pre_attrs()`, `fh_fill_post_attrs()`, and `fh_fill_both_attrs()` support weak cache consistency and NFSv4 change info.
- `fh_append_mac()` and `fh_verify_mac()` implement optional `NFSEXP_SIGN_FH` protection.

## Important Behavior
Subtree checking uses `nfsd_acceptable()` to walk ancestors up to the export root and ensure execute permission on each parent. For `NFSEXP_NOSUBTREECHECK`, lookup temporarily raises effective capabilities so `exportfs_decode_fh_raw()` can reconnect dentries through inaccessible parent paths.

Filehandle verification first locates the export by fsid, then decodes the file id unless the handle identifies the export root. NFSv4 pseudo-root exports expose only the pseudoroot object and traversable directories/symlinks, returning stale for unrelated objects.

Security checks are layered: secure source port, export user credential setup, xprtsec policy, GSS flavor policy with explicit bypass cases, then filesystem permission checks. LOCALIO calls pass `rqstp == NULL` and intentionally skip transport-security and flavor checks because access was already affirmed over NFS.

Composition chooses fsid encoding from a reference filehandle when compatible, otherwise from explicit export fsid, export UUID, or device number. It handles root filehandles specially with `FILEID_ROOT` and signs non-root filehandles when export policy requires it.

Weak cache consistency is disabled for exports/filesystems that advertise no WCC support. NFSv4 filehandles request btime and change-cookie attrs, while regular files with non-monotonic change cookies are mixed with ctime to avoid reuse after unclean shutdown.

## Dependencies
Uses Linux `exportfs`, VFS path and permission APIs, mount write accounting, NFSD export/auth/vfs helpers, tracepoints, crypto `siphash` and constant-time compare, kstat/statx, and per-net NFSD state.

## Risks and Subtleties
This is a security-critical path. Skipping `fh_verify()` or reusing verified dentries without rechecking permissions can miss changed export options, security flavor requirements, mount crossings, or credential changes.

Signed filehandles depend on a configured per-net `fh_key`; missing key or insufficient handle space degrades composition/verification and is rate-limited in logs. Any change to filehandle size accounting must preserve MAC word subtraction before `exportfs_decode_fh_raw()`.

Reference and cleanup discipline is strict: successful verification owns dentry/export references, `fh_put()` drops them and mount write access, and create paths must call `fh_update()` when a dentry becomes positive after initial composition.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsfh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsfh.h -->
# File Research: sources/os/linux/linux/fs/nfsd/nfsfh.h

## Summary
Defines the on-wire and internal NFSD filehandle representation, fsid encodings, `svc_fh` state, and inline helpers for initialization, matching, write access, hashing, and attribute bookkeeping.

## Main Responsibilities
- Documents and defines `struct knfsd_fh`, whose first bytes describe version, auth type, fsid type, and fileid type.
- Defines `struct svc_fh`, the internal verified filehandle object carrying handle bytes, dentry/export references, WCC state, write-mount state, and NFSv4 post/pre change attributes.
- Provides fsid encodings for device, user fsid, deprecated major/minor, encoded device, UUID-derived, full UUID, and UUID-plus-inode formats.
- Exposes core filehandle operations implemented in `nfsfh.c`.
- Provides small helpers for copying, initialization, comparison, fsid comparison, mount write acquisition, CRC hashing, and WCC reset.

## Key Data Structures and Interfaces
- `struct knfsd_fh` stores up to `NFS4_FHSIZE` raw bytes and current size.
- `struct svc_fh` stores raw handle plus validated VFS/export context.
- `enum nfsd_fsid` identifies fsid encoding in the handle.
- `enum fsid_source` tells NFSv2 attribute encoding whether fsid came from device, explicit fsid, or UUID.
- `mk_fsid()` serializes the selected fsid representation into handle words.
- `key_len()` returns fsid encoding byte lengths.

## Important Behavior
All handle words are treated as opaque to clients, but internal code sometimes stores host-endian and network-endian values in the same raw word array. The comments call this out explicitly, and the helpers use forced casts where needed.

`fh_want_write()` and `fh_drop_write()` protect exported mounts from writes during remount or shutdown. The flag in `svc_fh` prevents duplicate mount write acquisition.

`knfsd_fh_hash()` computes a Wireshark-compatible CRC32 hash for tracing/debugging. `fh_match()` and `fh_fsid_match()` compare exact raw handles or only fsid portions.

## Dependencies
Depends on Linux crc32, SunRPC service structures, inode versioning, exportfs fid formats, NFSv4 constants, and NFSD export definitions.

## Risks and Subtleties
`fh_copy()` warns if the source has a verified dentry; it is intended for raw decoded handles, not transferring live references. Misusing shallow copies can leak or double-drop dentries/exports.

`mk_fsid()` assumes UUID pointers are valid for UUID modes and uses direct casts into raw handle storage. Callers must choose an fsid type that is valid for the export and handle size.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsfh.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsproc.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfsproc.c

## Summary
Implements NFSv2 server procedure handlers and the NFSv2 SunRPC procedure table. It bridges decoded NFSv2 RPC arguments to common NFSD VFS helpers and maps internal/NFSv3/NFSv4-style errors back to NFSv2-compatible statuses.

## Main Responsibilities
- Handles NFSv2 NULL, GETATTR, SETATTR, LOOKUP, READLINK, READ, WRITE, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, RMDIR, READDIR, STATFS, and obsolete/reserved procedures.
- Performs NFSv2-specific CREATE overloading for regular files, directories, FIFOs, char/block devices, truncation, and permission checks.
- Initializes read/readlink/readdir response pages and reserves reply buffer space for payloads.
- Maps unsupported or newer NFSD errors to NFSv2 status values through `nfsd_map_status()`.
- Defines `nfsd_procedures2[]` with decode/encode/release callbacks, argument/result sizes, reply cache policy, XDR result sizing, and procedure names.

## Key Data Structures and Interfaces
- Procedure arguments and responses are stored in `rqstp->rq_argp` and `rqstp->rq_resp`.
- Handlers operate mostly through `svc_fh`, `nfsd_attrs`, and shared VFS helpers such as `nfsd_lookup()`, `nfsd_read()`, `nfsd_write()`, `nfsd_create()`, `nfsd_unlink()`, `nfsd_rename()`, and `nfsd_statfs()`.
- `nfsd_version2` exports the NFSv2 service version descriptor with per-CPU procedure counters and `nfsd_dispatch()`.

## Important Behavior
NFSv2 has limited error vocabulary, so bad/no filehandle maps to stale, wrongsec/xdev/file-open maps to access, symlink-not-dir maps to notdir, and generic symlink/wrong-type maps to I/O.

SETATTR contains compatibility logic for old clients that set both atime and mtime to a value near current time. If explicit timestamp setting would fail, it converts the request to “set to now” semantics.

CREATE is intentionally complicated because NFSv2 overloads file creation and special-file semantics. It locks the parent, composes a child filehandle, infers type when absent, handles existing special files as permission checks, consumes `ATTR_SIZE` as device number for special files, and truncates existing regular files.

READ and WRITE clamp counts to NFSv2 maximums and available response buffer space. Jukebox errors set `RQ_DROPME` so the RPC can be dropped rather than replied to in selected cases.

READDIR builds a single-page XDR dirlist and stores cookie offsets for later patching by `nfssvc_encode_nfscookie()`.

## Dependencies
Depends on NFSD cache policy definitions, NFSv2 XDR helpers, common NFSD VFS helpers, filehandle helpers, tracepoints, Linux namei/create helpers, and SunRPC service procedure descriptors.

## Risks and Subtleties
NFSv2 protocol compatibility drives behavior that looks unusual from modern VFS semantics, especially CREATE type inference, timestamp handling, and special-file treatment. Refactors must preserve wire-visible quirks.

Several handlers transfer ownership of decoded filehandles and must call `fh_put()` on argument and/or response handles at the correct point. Release callbacks in the procedure table complete cleanup for successful response handles.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsproc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfssvc.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfssvc.c

## Summary
Provides the central NFSD service engine: RPC program/version registration, server creation and destruction, per-net startup/shutdown, thread management, write verifier generation, address notifiers, RPC request initialization, the nfsd kernel thread loop, and duplicate reply cache dispatch integration.

## Main Responsibilities
- Defines `nfsd_programs[]` for NFS, optional NFSACL, and optional LOCALIO RPC programs.
- Maintains enabled protocol versions and minor versions per net namespace.
- Creates and binds `svc_serv` instances, registers address notifiers, starts/stops lockd and NFSD per-net resources, and tears them down.
- Implements global and per-net startup/shutdown for NFSv4 state, file cache, duplicate reply cache, lockd, and export flushing.
- Manages thread counts across pools with maximum enforcement and dynamic thread growth/shrink.
- Generates and copies the stable write verifier used by WRITE/COMMIT semantics.
- Dispatches decoded RPCs through the duplicate reply cache and procedure encode/decode paths.

## Key Data Structures and Interfaces
- `nfsd_mutex` serializes `nn->nfsd_serv`, listener lists, service setup, and mutable startup settings.
- `nfsd_programs[]` ties program numbers to version tables, authentication, request initialization, and rpcbind registration.
- `nfsd_version[]`, optional `nfsd_acl_version[]`, and optional `localio_versions[]` form protocol version tables.
- `nfsd_net_ref` protects per-net NFSD state during active service operation.
- `nfsd()` is the service kthread entry point.
- `nfsd_dispatch()` is the shared dispatcher for NFS, NFSACL, and LOCALIO procedure tables.

## Important Behavior
`nfsd_create_serv()` initializes per-net refs, default block size, enabled versions, a pooled SunRPC service, rpcbind binding, address notifiers, and a new write verifier. It leaves `nn->nfsd_serv` visible under notifier lock only after successful bind.

`nfsd_startup_net()` requires at least one configured permanent listener, starts lockd when NFSv2/v3 are enabled, starts per-net file cache and reply cache, then starts NFSv4 state. Failure unwinds in reverse order.

`nfsd_set_nrthreads()` caps total threads to `NFSD_MAXSERVS` and scales excessive per-pool requests down. A single thread-count value is treated specially as an even distribution request across pools with `min_threads`.

The `nfsd` kthread loop waits in `svc_recv()`, disposes deferred filecache items, kills excess dynamic threads after idle timeout, and spawns more threads when all are busy and the pool is below its maximum.

`nfsd_dispatch()` decodes arguments, marks request fields stable through `rq_status_counter`, consults the duplicate reply cache, executes the procedure, encodes the result, marks request fields unstable again, and updates or bypasses the cache according to procedure policy and drop/error outcomes.

Address notifiers age temporary transports immediately when IPv4/IPv6 addresses go down, preventing stale connection state from lingering against removed local addresses.

## Dependencies
Depends on SunRPC service, pooling, stats, transports, rpcbind, duplicate reply cache, NFSD VFS/filecache/state/export helpers, lockd, NFSACL, LOCALIO, network address notifiers, IPv6 optional support, freezer/kthread APIs, siphash, and tracepoints.

## Risks and Subtleties
`nfsd_mutex` is the main correctness boundary. Server pointer publication, listener mutation, version changes, dynamic thread changes, and destruction must remain serialized.

The request status counter protocol is used by netlink RPC-status readers; any dispatcher changes must preserve odd/even release/acquire semantics around stable request fields.

Startup requires configured listeners before threads start. Control paths that create `svc_serv` without threads must destroy it if no listeners or threads remain, or they can leave unusable service state.

The NFSACL mismatch helpers appear to test support using the requested version inside loops, which is a subtle area to treat carefully if modifying version-negotiation behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfssvc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsxdr.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfsxdr.c

## Summary
Implements NFSv2 XDR encoding and decoding helpers for NFSD procedure arguments and responses, including filehandles, attributes, names, read/write payloads, directory entries, statfs results, and response cleanup.

## Main Responsibilities
- Decodes NFSv2 filehandles, filenames, directory operation arguments, setattr attributes, read/write/create/rename/link/symlink/readdir arguments.
- Encodes NFSv2 status, filehandles, file attributes, attrstat, diropres, readlink, read, readdir, statfs, and simple status results.
- Converts Linux `kstat` data to NFSv2 `fattr`, including type mapping, ids in the request user namespace, symlink size cap, device encoding, fsid selection, and lease-aware mtime.
- Handles opaque payload pages for READ and READLINK replies.
- Provides release callbacks that drop response filehandles.

## Key Data Structures and Interfaces
- `nfs_ftypes[]` maps Linux inode mode file types to NFSv2 type constants.
- `svcxdr_decode_fhandle()` initializes `svc_fh` with a fixed `NFS_FHSIZE` handle.
- `svcxdr_decode_sattr()` translates NFSv2 sattr fields to Linux `iattr`.
- `svcxdr_encode_fattr()` serializes a `kstat` and filehandle/export context.
- `nfssvc_encode_entry()` is the directory callback used by `nfsd_readdir()`.
- `nfssvc_release_attrstat()`, `nfssvc_release_diropres()`, and `nfssvc_release_readres()` release response filehandles.

## Important Behavior
Filename decoding rejects zero-length names, names longer than `NFS_MAXNAMLEN`, embedded NULs, and slashes.

Setattr decoding treats `0xffffffff` as “do not set” and tolerates the Sun client `0xffff` mode sentinel. UID/GID conversion uses the request’s user namespace and only marks valid ids. A microsecond value of `1000000` on mtime triggers the old Sun convention for setting atime/mtime to current server time.

NFSv2 file attributes use a protocol-limited view: symlink size is capped at `NFS_MAXPATHLEN`, inode numbers and sizes are truncated to u32 fields, and fsid is derived from explicit export fsid, UUID xor, or encoded device depending on `fsid_source()`.

READ/READLINK encoders put data in pages and call `svc_encode_result_payload()` so the RPC layer accounts for payload placement. READDIR stores a cookie placeholder for each entry and patches the previous entry’s cookie when the next offset is known.

## Dependencies
Depends on NFSD VFS, XDR declarations, auth/user namespace helpers, lease timestamp helpers, XDR stream APIs, page-backed SunRPC buffers, and filehandle/export helpers.

## Risks and Subtleties
This file is protocol-ABI code. Compatibility quirks such as sentinel setattr values, `1000000` microseconds, u32 truncation, and NFSv2 cookie patching are intentional.

Directory encoding must roll back `dirlist.len` and clear `cookie_offset` when the buffer is too small; otherwise partial entries or bad cookies could be exposed to clients.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfsxdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/pnfs.h -->
# File Research: sources/os/linux/linux/fs/nfsd/pnfs.h

## Summary
Declares the NFSD pNFS server-side layout interface and compile-time stubs. It connects NFSv4.1+ layout operations to concrete block, SCSI, and flexfile layout implementations when configured.

## Main Responsibilities
- Defines the pNFS device-id map and layout operation vector.
- Declares layout driver hooks for GETDEVICEINFO, LAYOUTGET, LAYOUTCOMMIT, layout encoding, client fencing, and recall behavior.
- Exposes common pNFS stateid preprocessing, layout insertion, layout return, device-id generation, and device-id lookup helpers.
- Provides initialization, teardown, layout-type setup, client/file layout return, and layout close APIs.
- Supplies no-op stubs when `CONFIG_NFSD_PNFS` or `CONFIG_NFSD_V4` support is absent.

## Key Data Structures and Interfaces
- `struct nfsd4_deviceid_map` maps an index and fsid data to generated pNFS device IDs.
- `struct nfsd4_layout_ops` is the per-layout-type method table.
- `nfsd4_layout_ops[]` indexes available layout drivers.
- Optional externs expose `bl_layout_ops`, `scsi_layout_ops`, and `ff_layout_ops`.

## Important Behavior
The interface separates protocol preprocessing from filesystem/layout-specific encoding and commit behavior. Layout implementations can disable recalls, advertise notification types, and provide a fencing callback for client isolation.

`MAX_FENCE_DELAY` caps exponential backoff for fence retries at three minutes.

## Dependencies
Depends on NFSv4 NFSD state structures, exportfs, NFS export definitions, NFSv4 XDR declarations, and optional block/SCSI/flexfile layout configuration.

## Risks and Subtleties
The header deliberately compiles away pNFS behavior when unsupported. Callers must not assume layout state exists unless the relevant config is enabled, and layout driver hooks must honor shared stateid and recall rules from `state.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/pnfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/state.h -->
# File Research: sources/os/linux/linux/fs/nfsd/state.h

## Summary
Defines the core NFSv4 state model used by NFSD: client IDs, sessions, callbacks, stateids, delegations, open/lock owners, files, pNFS layout state, blocked locks, recovery records, and copy-notify state.

## Main Responsibilities
- Defines wire-derived identifiers such as `clientid_t`, `stateid_t`, and copy stateids.
- Describes NFSv4 callback infrastructure and callback operation hooks.
- Defines common stateid objects and concrete delegation, open/lock, and layout stateid containers.
- Defines client/session/channel/slot structures for NFSv4.0 and v4.1+ session operation.
- Models openowners, lockowners, replay caches, per-client open/delegation file state, file aggregation, blocked locks, and pNFS layout state.
- Declares lifecycle and lookup functions implemented by NFSv4 state code.

## Key Data Structures and Interfaces
- `struct nfs4_stid` is the common refcounted stateid core for open, lock, delegation, and layout state.
- `struct nfs4_client` is the top-level client object containing identity, credentials, callbacks, sessions, stateid IDR, delegations, reclaim state, async copies, nfsdfs entries, and optional pNFS/SCSI layout data.
- `struct nfsd4_session` tracks v4.1+ session IDs, channel attributes, connections, backchannel slots, and forward replay slots.
- `struct nfs4_stateowner`, `nfs4_openowner`, and `nfs4_lockowner` model seqid-mutating owners and replay state.
- `struct nfs4_file` aggregates all state for a filehandle/inode, including cached `nfsd_file` references, share deny/access counts, delegations, and layout state lists.
- `struct nfs4_ol_stateid`, `nfs4_delegation`, and `nfs4_layout_stateid` specialize stateid behavior for opens/locks, delegations, and pNFS layouts.

## Important Behavior
Stateid status bits encode closed, revoked, admin-revoked, freeable, and freed states. Locking rules differ by type: client locks protect open/lock state, delegation locks protect delegation status, and layout locks protect layout status.

Delegations carry recall callback state, retry counts, delegated timestamp fields, CB_GETATTR state, and per-client/per-file linkage. Helper predicates distinguish read, write, and attribute delegations.

Sessions bound resource limits with constants for max slots, slot cache size, and total memory per session. Slots store seqid, cached status/data, credential, generation, and flags for in-use/cache/reuse behavior.

Clients can be active, courtesy, or expirable. Courtesy clients preserve state after lease expiry until conflict or laundromat pressure forces expiration.

Replay support exists both for NFSv4.0 owner seqid operations and NFSv4.1+ session slots. `NFSD4_REPLAY_ISIZE` embeds a common-size reply buffer and falls back to dynamic allocation for large replies.

pNFS layout stateids include layout lists, recall callback, delayed fence work, exponential backoff state, and fenced status.

## Dependencies
Depends on crypto MD5, IDR, refcounts, SunRPC transports, filehandle definitions, NFSD service definitions, callbacks, pNFS optional configuration, nfsd file cache objects, and NFSv4 XDR/state operation implementations.

## Risks and Subtleties
This header encodes the ownership and lock hierarchy for NFSv4 state. Bugs usually come from using the wrong lock for a stateid type, dropping references too early, or bypassing lookup/preprocess helpers that validate generation, type, status, client, filehandle, and open mode.

Many structs require first-field embedding so `container_of()` conversions work. Layout, delegation, open, and lock state objects depend on these layout assumptions.

Client lifetime is intentionally nontraditional: resting clients can have zero active references while still present in lookup tables, and destruction must respect in-flight compounds, callbacks, sessions, and reclaim records.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/state.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/stats.c -->
# File Research: sources/os/linux/linux/fs/nfsd/stats.c

## Summary
Implements procfs output for NFSD statistics under `/proc/net/rpc/nfsd` and registers/unregisters the per-net proc stats endpoint.

## Main Responsibilities
- Formats reply cache, filehandle stale, I/O byte, thread count, deprecated thread histogram, and deprecated read-ahead cache statistics.
- Delegates generic RPC service statistics formatting to `svc_seq_show()`.
- Emits per-NFSv4 operation counters and write-delegation GETATTR counter when NFSv4 is enabled.
- Registers and unregisters the proc entry through SunRPC stats helpers.

## Key Data Structures and Interfaces
- `nfsd_show()` reads `struct nfsd_net` from proc inode data and prints counter values from `nn->counter`.
- `DEFINE_PROC_SHOW_ATTRIBUTE(nfsd)` creates proc operations.
- `nfsd_proc_stat_init()` calls `svc_proc_register()`.
- `nfsd_proc_stat_shutdown()` calls `svc_proc_unregister()`.

## Important Behavior
Output preserves legacy field groups even for deprecated stats by printing zero-filled placeholders. This maintains compatibility with userspace parsers expecting historical `/proc/net/rpc/nfsd` layout.

Counter reads use `percpu_counter_sum_positive()` to aggregate per-CPU counters without exposing negative transient values.

## Dependencies
Depends on seq_file, SunRPC stats, proc/net namespace infrastructure, NFSD counters, and NFSv4 operation constants when enabled.

## Risks and Subtleties
The text format is a userspace ABI. Removing deprecated zero fields or changing ordering can break monitoring tools.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/stats.h -->
# File Research: sources/os/linux/linux/fs/nfsd/stats.h

## Summary
Declares NFSD proc stats setup/teardown and inline helpers for updating per-net and per-export NFSD counters.

## Main Responsibilities
- Exposes proc stats registration functions.
- Provides inline increment/add/subtract helpers for reply cache hits, misses, no-cache events, stale filehandles, I/O bytes, payload misses, and duplicate reply cache memory usage.
- Mirrors selected per-net stats into per-export stats when export stats are available.
- Provides an NFSv4-only helper for write delegation GETATTR conflicts.

## Key Data Structures and Interfaces
- Helpers update `nn->counter[NFSD_STATS_*]`.
- Per-export mirror updates use `exp->ex_stats->counter[EXP_STATS_*]`.
- Counter IDs come from `uapi/linux/nfsd/stats.h`.

## Important Behavior
The stale filehandle and I/O helpers update both namespace-wide and export-specific counters, allowing global proc stats and per-export reporting to stay consistent.

Duplicate reply cache memory helpers use add/sub wrappers around per-cpu counters to track allocation changes.

## Dependencies
Depends on NFSD UAPI stats IDs, Linux percpu counters, `struct nfsd_net`, and export stats structures.

## Risks and Subtleties
Callers should use these helpers instead of touching counters directly when export-level mirroring matters. Passing a null export is supported for namespace-only accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/trace.c -->
# File Research: sources/os/linux/linux/fs/nfsd/trace.c

## Summary
Instantiates NFSD tracepoints by defining `CREATE_TRACE_POINTS` before including `trace.h`.

## Main Responsibilities
- Provides the single compilation unit that emits storage and definitions for tracepoints declared in `fs/nfsd/trace.h`.

## Key Data Structures and Interfaces
- `CREATE_TRACE_POINTS` controls Linux tracepoint definition generation.
- `#include "trace.h"` imports the NFSD trace event declarations.

## Important Behavior
This file intentionally contains no runtime logic beyond tracepoint instantiation.

## Dependencies
Depends on NFSD `trace.h` and the kernel tracepoint macro system.

## Risks and Subtleties
Only one translation unit should define `CREATE_TRACE_POINTS` for a trace header. Duplicating this pattern elsewhere would cause duplicate tracepoint definitions at link time.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/trace.c -->