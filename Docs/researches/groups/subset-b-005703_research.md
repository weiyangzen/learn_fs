# subset-b-005703 Research

Grouped source research for the Ceph-client copy of Linux NFSD control, service, filehandle, NFSv2 procedure/XDR, pNFS, state, stats, and trace-point-definition sources. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsctl.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfsctl.c

## Purpose

`nfsctl.c` implements the administrative surface and module/per-network-namespace lifecycle for the in-kernel NFS server. It backs the `nfsd` pseudo filesystem transaction files, the legacy `/proc/fs/nfs/exports` view, and the newer NFSD Generic Netlink configuration/status operations. The source was read as a complete 2381-line file for this report.

## Important APIs, Types, and Functions

Key procfs/nfsdfs handlers are `write_filehandle`, `write_unlock_ip`, `write_unlock_fs`, `write_threads`, `write_pool_threads`, `write_versions`, `write_ports`, `write_maxblksize`, `write_leasetime`, `write_gracetime`, `write_recoverydir`, and `write_v4_end_grace`, reached through `nfsctl_transaction_write/read`. Filesystem helpers include `nfsd_fill_super`, `nfsd_fs_get_tree`, `nfsd_umount`, `nfsd_client_mkdir`, `nfsd_client_rmdir`, and `get_nfsdfs_client`. Netlink entry points include `nfsd_nl_rpc_status_get_dumpit`, `nfsd_nl_threads_set_doit/get_doit`, `nfsd_nl_version_set_doit/get_doit`, `nfsd_nl_listener_set_doit/get_doit`, and `nfsd_nl_pool_mode_set_doit/get_doit`. Module lifecycle is `init_nfsd`/`exit_nfsd`; per-net lifecycle is `nfsd_net_init`/`nfsd_net_exit`.

## Control Flow

Transaction files parse a userspace write into a bounded simple-transaction buffer, dispatch by inode number through `write_op`, and then expose a reply through read. Zero-length reads synthesize a zero-length write so state files can be queried. Admin writes generally validate syntax, trace the request, take `nfsd_mutex` for service-global state, call service helpers in `nfssvc.c`, and format a text response. Netlink setters perform equivalent structured validation and then update the running namespace state. The mount path uses `simple_fill_super` to create fixed nfsdfs files plus a `clients` directory used by NFSv4 client debug/control code.

## State and Persistence Behavior

State is primarily live kernel state in `struct nfsd_net`: server pointer, export/idmap caches, counters, version bitmaps, lease/grace times, min thread count, server scope name, filehandle signing key, write verifier lock, and optional localio client lists. `nfsd_net_init` allocates per-net resources and initializes counters and default versions; `nfsd_net_exit` tears them down and frees sensitive `fh_key` material. Configuration changes are not persisted by this file except where NFSv4 legacy client tracking uses its recovery directory machinery.

## Dependencies and Integration Points

The file integrates SunRPC service sockets, lockd, GSS/rpc_pipefs, export and idmap caches, pNFS, NFSv4 state, filecache, tracepoints, and generated NFSD netlink policy/family code. It is the bridge between userspace administration tools and `nfssvc.c`, `state.c`, lockd, export cache code, and procfs/netlink UAPI.

## Risks and Edge Cases

Many settings are rejected while the service is running because changing versions, block size, lease/grace time, scope, or filehandle key would invalidate active service allocation. Listener replacement is careful but destructive: it moves existing sockets aside, refuses removal while threads are active, and recreates listeners after destroying old ones. Text parsers require newline-terminated writes and have compatibility behaviors such as implicit NFSv4 minor toggling. `write_unlock_fs` explicitly notes weak filesystem sanity checks before revoking lock/state. Netlink RPC status depends on `rq_status_counter` acquire/release sequencing to avoid torn request snapshots.

## Test Signals

Useful signals are nfsdfs read/write round trips for all transaction files, netlink get/set parity with the YAML schema, refusal of mutable settings while threads run, listener add/remove across IPv4/IPv6 and fd/transport inputs, namespace teardown/mount/unmount tests, RPC status dumps under NFSv4 compound load, filehandle key length and shutdown-only tests, and lock/state revocation tests for `unlock_ip` and `unlock_filesystem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsd.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfsd.h

## Purpose

`nfsd.h` is a central NFSD internal header. It collects protocol version constants, service prototypes, shared error constants, NFSv4 attribute masks, service-thread helpers, and feature-conditional declarations used throughout the server. The source was read as a complete 608-line file for this report.

## Important APIs, Types, and Functions

Important declarations include `nfsd_svc`, `nfsd_dispatch`, `nfsd_nrthreads`, `nfsd_nrpools`, `nfsd_get_nrthreads`, `nfsd_set_nrthreads`, `nfsd_shutdown_threads`, `nfsd_current_rqst`, `nfsd_vers`, `nfsd_minorversion`, `nfsd_reset_versions`, `nfsd_create_serv`, and `nfsd_destroy_serv`. Types include `struct nfsd_genl_rqstp`, `struct nfsd_thread_local_info`, `struct nfsdfs_client`, `struct nfsd_voidargs`, and `struct nfsd_voidres`. It exports global symbols such as `nfsd_programs`, `nfsd_mutex`, `nfsd_th_cnt`, `nfsd_max_blksize`, cache-mode globals, and NFSv4 setup/shutdown hooks. It also defines many pre-XDR `nfserr_*` constants.

## Control Flow

The header has no standalone runtime flow, but it fixes cross-file call paths: admin entry points invoke service lifecycle functions; SunRPC dispatch invokes `nfsd_dispatch`; NFSv2/v3/v4 procedure tables reference shared void XDR helpers; and NFSv4 processing consults supported attribute masks and state-management prototypes. Inline helpers such as `nfsd_v4client`, `nfsd_user_namespace`, `nfsd4_set_netaddr`, `bmval_is_subset`, and `nfsd_attrs_supported` participate directly in request validation and encoding paths.

## State and Persistence Behavior

This file defines contracts for live state, not storage. It centralizes global and per-net state access points and constants that shape service allocation, version availability, NFSv4 lease/state subsystems, and response encoding. Persistent NFSv4 recovery is represented only through declarations such as `nfs4_reset_recoverydir`, `nfs4_recoverydir`, client tracking registration, and grace-state hooks.

## Dependencies and Integration Points

Dependencies include Linux NFS protocol headers, SunRPC service/xprt headers, mount and namespace types, export metadata, `netns.h`, and `stats.h`. The header is included by nearly every NFSD implementation file and therefore forms a high-risk ABI-like internal contract for procedure tables, error handling, service startup, NFSv4 attributes, callbacks, and optional features such as ACLs, pNFS, localio, debugfs, and security labels.

## Risks and Edge Cases

Changing constants such as `NFSD_SUPPORTED_MINOR_VERSION`, XDR-size assumptions, pre-encoded error symbols, or NFSv4 attribute masks can alter wire behavior. The NFSv4 attribute masks must stay synchronized with decoder and encoder support. Feature-conditional stubs must match real function semantics closely enough that non-V4 or non-pNFS builds compile and behave predictably.

## Test Signals

Compile matrix coverage across `CONFIG_NFSD_V2`, `CONFIG_NFSD_V4`, ACL, pNFS, localio, security-label, POSIX-ACL, and debugfs combinations is essential. Protocol tests should validate version enablement, NFSv4 supported/writeable attribute masks, error-code mapping, callback availability, and no-op stub behavior when features are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsfh.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfsfh.c

## Purpose

`nfsfh.c` implements NFSD filehandle decoding, validation, composition, signing, weak-cache-consistency attribute capture, and NFSv4 change attribute generation. It is a core trust-boundary file: opaque client-provided handles become kernel dentries and exports only after export lookup, type checking, security checks, and optional MAC verification. The source was read as a complete 962-line file for this report.

## Important APIs, Types, and Functions

Public functions are `fh_verify`, `fh_verify_local`, `fh_compose`, `fh_update`, `fh_getattr`, `fh_fill_pre_attrs`, `fh_fill_post_attrs`, `fh_fill_both_attrs`, `fh_put`, `SVCFH_fmt`, `fsid_source`, and `nfsd4_change_attribute`. Key internal helpers include `nfsd_acceptable`, `nfsd_mode_check`, `nfsd_originating_port_ok`, `nfsd_setuser_and_check_port`, `check_pseudo_root`, `fh_append_mac`, `fh_verify_mac`, `nfsd_set_fh_dentry`, `_fh_update`, `set_version_and_fsid_type`, and `fsid_type_ok_for_exp`.

## Control Flow

`fh_verify` calls `__fh_verify`; the first verification decodes the filehandle through `nfsd_set_fh_dentry`, while later calls reuse `fh_dentry` and repeat permission/security checks. Decoding validates handle version/auth/fsid layout, normalizes deprecated fsid type 2, looks up the export, optionally elevates credentials for `NOSUBTREECHECK`, verifies signed handles, decodes the dentry through exportfs, applies pseudo-root restrictions, sets export credentials, checks xprtsec and security flavors, and finally calls `nfsd_permission`. Composition chooses a handle fsid format from a reference handle or export options, encodes the fsid, calls `exportfs_encode_fh`, optionally appends a siphash MAC, and stores references to dentry/export.

## State and Persistence Behavior

State is carried in `struct svc_fh`: raw handle bytes, max size, dentry/export refs, write-mount protection, WCC flags, 64-bit cookie flag, and pre/post attributes. The optional filehandle MAC uses per-net `nn->fh_key` set via netlink. No file-backed persistence is owned here, but filehandle layout is persistent from the client's perspective, and `nfsd4_change_attribute` deliberately combines ctime with non-monotonic change cookies to avoid client-visible reuse after crashes.

## Dependencies and Integration Points

The code integrates exportfs filehandle encoding/decoding, export cache lookup, VFS permission/stat APIs, SunRPC auth/GSS credential handling, xprtsec policy, tracepoints, filecache stats, pNFS/NFSv4 state consumers, and mount write protection. It is consumed by all NFS procedure implementations before VFS operations.

## Risks and Edge Cases

The highest-risk paths are accepting stale or forged handles, mishandling signed handle lengths, changing fsid encoding compatibility, and skipping security checks on reused handles. `NOSUBTREECHECK` intentionally bypasses some parent permission constraints to reconnect dentries. NFSv2/v3/v4 max handle sizes alter WCC, cookie, V4ROOT, and export-operation behavior. `fh_put` must be called by callers to release dentries, exports, and write refs.

## Test Signals

Tests should cover valid and stale filehandles, deprecated fsid conversion, signed filehandle success/failure/no-key/no-space paths, subtreecheck versus nosubtreecheck exports, secure-port/GSS/xprtsec/security-flavor checks, V4ROOT restrictions, WCC pre/post attribute capture, `fh_update` after create, and change attribute monotonicity with and without `STATX_CHANGE_COOKIE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsfh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsfh.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfsfh.h

## Purpose

`nfsfh.h` defines the on-wire and internal NFSD filehandle layouts plus helper functions for composing, comparing, hashing, and releasing filehandle-backed state. The source was read as a complete 339-line file for this report.

## Important APIs, Types, and Functions

Core types are `struct knfsd_fh`, `typedef struct svc_fh`, `enum nfsd_fsid`, and `enum fsid_source`. Important helpers/macros include `fh_version`, `fh_auth_type`, `fh_fsid_type`, `fh_fileid_type`, `fh_fsid`, `mk_fsid`, `key_len`, `fh_copy`, `fh_copy_shallow`, `fh_init`, `fh_match`, `fh_fsid_match`, `fh_want_write`, `fh_drop_write`, `knfsd_fh_hash`, and `fh_clear_pre_post_attrs`. It declares the implementation APIs `fh_verify`, `fh_verify_local`, `fh_getattr`, `fh_compose`, `fh_update`, `fh_put`, `nfsd4_change_attribute`, and pre/post attribute fillers.

## Control Flow

The header's inline flow is mostly data preparation and cleanup. `mk_fsid` writes the fsid portion for a selected encoding scheme, `key_len` returns the corresponding byte length, `fh_init` zeroes a handle and sets max size, `fh_want_write`/`fh_drop_write` acquire and release mount write access, and match/hash helpers support comparisons and diagnostics. The declared C file functions perform actual decode/encode and validation.

## State and Persistence Behavior

`knfsd_fh` stores the opaque bytes sent to clients; `svc_fh` wraps that with transient server-side dentry/export refs, write protection state, WCC flags, readdir-cookie sizing, and saved pre/post attributes. The filehandle byte format is a compatibility contract with clients and exportfs, while `svc_fh` state is per-request or per-compound and must be released.

## Dependencies and Integration Points

The header depends on crc32, SunRPC service types, inode versioning, exportfs fid types, NFSv4 constants, and export metadata. It is the shared filehandle contract for XDR decoders, NFS procedure implementations, export cache lookup, VFS operations, stats, and trace formatting.

## Risks and Edge Cases

The layout uses host-byte-order words for opaque values, sometimes storing network-order pieces with sparse casts. Alignment-sensitive writes in `mk_fsid` for 64-bit inode/UUID formats require care. Any new fsid type must update `key_len`, composition, decoding, and client compatibility expectations. `fh_copy` warns when copying an initialized handle with a dentry because ownership would be duplicated incorrectly.

## Test Signals

Useful tests include handle encode/decode across all fsid types, NFSv2/3/4 max-size behavior, mount write reference balancing, hash compatibility with packet analyzers, match/fsid-match comparisons, WCC flag propagation, and build coverage across filesystems with and without UUIDs or stable device IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsfh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsproc.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfsproc.c

## Purpose

`nfsproc.c` implements NFS version 2 procedure handlers and the `svc_version` dispatch table for program version 2. It maps the old RFC 1094 procedure set to shared NFSD VFS, filehandle, and XDR helpers. The source was read as a complete 850-line file for this report.

## Important APIs, Types, and Functions

Procedure handlers include `nfsd_proc_null`, `nfsd_proc_getattr`, `nfsd_proc_setattr`, `nfsd_proc_root`, `nfsd_proc_lookup`, `nfsd_proc_readlink`, `nfsd_proc_read`, `nfsd_proc_writecache`, `nfsd_proc_write`, `nfsd_proc_create`, `nfsd_proc_remove`, `nfsd_proc_rename`, `nfsd_proc_link`, `nfsd_proc_symlink`, `nfsd_proc_mkdir`, `nfsd_proc_rmdir`, `nfsd_proc_readdir`, and `nfsd_proc_statfs`. `nfsd_map_status` converts newer/internal status values into NFSv2-compatible errors. `nfsd_procedures2` is the procedure metadata table, and `nfsd_version2` publishes it to SunRPC.

## Control Flow

SunRPC dispatch decodes arguments using the table's `pc_decode`, calls the handler, then encodes via `pc_encode`. Each handler generally validates filehandles with `fh_verify` or delegates to shared VFS functions such as `nfsd_lookup`, `nfsd_read`, `nfsd_write`, `nfsd_create`, `nfsd_unlink`, `nfsd_rename`, `nfsd_link`, `nfsd_symlink`, `nfsd_readdir`, and `nfsd_statfs`. Create has extra legacy semantics: it locks the parent during lookup/create, overloads `ATTR_SIZE` for device numbers, handles existing regular files as truncate-on-create, and treats some special-file creates as permission checks. All handler statuses are normalized through `nfsd_map_status`.

## State and Persistence Behavior

This file owns no persistent storage. It manages per-request `svc_fh` references, result buffers, pages for read/readlink/readdir payloads, and duplicate-reply-cache policy through `pc_cachetype` in the procedure table. Non-idempotent operations use reply caching (`RC_REPLBUFF` or `RC_REPLSTAT`) to satisfy retransmits consistently.

## Dependencies and Integration Points

It integrates `cache.h`, `xdr.h`, `vfs.h`, `trace.h`, filehandle validation, SunRPC service dispatch, NFSv2 XDR encode/decode functions, and shared VFS operation implementations. It is selected by `nfssvc.c` when NFSv2 is compiled and enabled.

## Risks and Edge Cases

NFSv2 lacks modern error granularity, so status mapping can hide important server-side distinctions. The overloaded CREATE path is compatibility-heavy and sensitive to special-file and mode interpretation. Handlers must balance `fh_put` exactly as indicated by comments and table release callbacks. Read/write paths mark `RQ_DROPME` on jukebox/delay-like errors to avoid sending inappropriate replies.

## Test Signals

Run NFSv2 connectathon/pynfs-style procedure tests, retransmit duplicate-reply-cache tests for non-idempotent ops, create/truncate/special-file compatibility cases, symlink target length and multi-page payload tests, readdir cookie/toosmall behavior, error mapping checks, and filehandle release leak detection under failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfssvc.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfssvc.c

## Purpose

`nfssvc.c` is the central service runtime for NFSD. It defines the SunRPC service programs, version enablement, service creation/destruction, per-namespace startup/shutdown, thread-pool scaling, write verifier generation, RPC dispatch integration with the duplicate reply cache, and void XDR helpers. The source was read as a complete 1078-line file for this report.

## Important APIs, Types, and Functions

Externally used APIs include `nfsd_support_version`, `nfsd_vers`, `nfsd_minorversion`, `nfsd_net_try_get`, `nfsd_net_put`, `nfsd_copy_write_verifier`, `nfsd_reset_write_verifier`, `nfsd_destroy_serv`, `nfsd_reset_versions`, `nfsd_shutdown_threads`, `nfsd_current_rqst`, `nfsd_create_serv`, `nfsd_nrpools`, `nfsd_get_nrthreads`, `nfsd_set_nrthreads`, `nfsd_svc`, `nfsd_dispatch`, `nfssvc_decode_voidarg`, and `nfssvc_encode_voidres`. Global data includes `nfsd_programs`, `nfsd_mutex`, and `nfsd_th_cnt`. Internal service-thread logic is in `nfsd`.

## Control Flow

Admin code calls `nfsd_svc` under `nfsd_mutex`: it records scope, creates `svc_serv` if needed, starts per-net resources, sets thread counts, and destroys the service if zero threads remain. `nfsd_create_serv` initializes per-net refs, block size, versions, pooled SunRPC service, rpcbind entries, address notifiers, and write verifier. Worker threads run `nfsd`, receive requests, dynamically shrink on idle timeout or grow when no idle threads are available, dispose filecache entries, and exit through SunRPC thread teardown. `nfsd_dispatch` decodes arguments, publishes request status with `rq_status_counter`, consults/updates the duplicate reply cache, calls the selected procedure, encodes the result, and handles drop/decode/encode errors.

## State and Persistence Behavior

Runtime state is per-net and service-global: enabled versions, `svc_serv`, sockets, lockd status, reply cache, filecache, NFSv4 state, per-net refs, `nfsd_users`, address notifier refcount, active thread count, and a seqlock-protected write verifier. The verifier is regenerated from raw time hashed with a per-net siphash key on service creation. No disk persistence is owned here; NFSv4 recovery state is started/stopped through other modules.

## Dependencies and Integration Points

The file integrates SunRPC service core, svc sockets/xprts, rpcbind, lockd, NFS ACL program variants, optional localio, NFSv4 state, reply cache, filecache, export flushing, network address notifiers, freezer/kthread infrastructure, and tracepoints. `nfsctl.c` uses it for all service configuration.

## Risks and Edge Cases

`nfsd_mutex` is the main serialization contract; violating it risks races with service pointer, socket lists, versions, and global settings. Startup fails when no listeners exist. Dynamic thread creation/removal relies on pool min/max and trylock behavior. Request status publication must remain synchronized with netlink readers. Shutdown must kill percpu refs and wait before freeing per-net resources.

## Test Signals

Signals include service start/stop with and without listeners, version enable/disable and rpcbind registration, pool thread scaling and max clamping, dynamic thread grow/shrink traces, duplicate-reply-cache replay/drop behavior, write verifier stability within one instance and change across restart, net namespace teardown under load, and address removal aging temporary transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsxdr.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfsxdr.c

## Purpose

`nfsxdr.c` implements NFSv2 XDR encode/decode helpers for filehandles, attributes, procedure arguments, procedure results, directory entries, and result release. It is the wire-format partner of `nfsproc.c`. The source was read as a complete 663-line file for this report.

## Important APIs, Types, and Functions

Public decode helpers include `nfssvc_decode_fhandleargs`, `nfssvc_decode_sattrargs`, `nfssvc_decode_diropargs`, `nfssvc_decode_readargs`, `nfssvc_decode_writeargs`, `nfssvc_decode_createargs`, `nfssvc_decode_renameargs`, `nfssvc_decode_linkargs`, `nfssvc_decode_symlinkargs`, and `nfssvc_decode_readdirargs`. Public encoders include `svcxdr_encode_stat`, `svcxdr_decode_fhandle`, `svcxdr_encode_fattr`, `nfssvc_encode_statres`, `nfssvc_encode_attrstatres`, `nfssvc_encode_diropres`, `nfssvc_encode_readlinkres`, `nfssvc_encode_readres`, `nfssvc_encode_readdirres`, `nfssvc_encode_statfsres`, `nfssvc_encode_nfscookie`, and `nfssvc_encode_entry`. Release helpers are `nfssvc_release_attrstat`, `nfssvc_release_diropres`, and `nfssvc_release_readres`.

## Control Flow

Decoders consume an `xdr_stream`, initialize `svc_fh` objects, validate names and payload lengths, convert NFSv2 `sattr` sentinels into Linux `iattr` flags, and build subsegments for opaque write payloads. Encoders reserve stream space, write status first, and conditionally append attributes, filehandles, opaque pages, readdir terminators, statfs data, and read/readlink payload metadata. Readdir uses a separate page-backed XDR buffer; each new entry first patches the previous entry's cookie, then writes presence, fileid, clipped name, and placeholder cookie.

## State and Persistence Behavior

There is no persistent state. Per-request state includes decoded pointers into the RPC buffer, `svc_fh` ownership, response pages, `cookie_offset`, and result lengths. Release callbacks drop filehandle refs after the response has been encoded.

## Dependencies and Integration Points

The file integrates shared VFS attribute data, `xdr.h` argument/result structs, auth namespace mapping via `nfsd_user_namespace`, filehandle helpers, lease mtime adjustment, export fsid-source selection, and SunRPC XDR/page-payload helpers. `nfsproc.c` binds these helpers into the NFSv2 procedure table.

## Risks and Edge Cases

Name decoding rejects empty names, slash, and embedded NUL. NFSv2 fixed-size filehandles are copied as exactly `NFS_FHSIZE`. `sattr` has legacy Sun compatibility for `0xffff` mode and `useconds=1000000` touch semantics. Attribute encoding truncates symlink size at `NFS_MAXPATHLEN` and maps fsid depending on export configuration. Readdir must correctly roll back partial entries on `toosmall`.

## Test Signals

Wire-level tests should verify XDR round trips for every NFSv2 procedure, malformed short buffers, invalid names, large write/read payload bounds, UID/GID namespace munging, sattr sentinel handling, symlink size clipping, statfs field encoding, readdir cookie patching and rollback, and filehandle release callbacks after encode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfsxdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/pnfs.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/pnfs.h

## Purpose

`pnfs.h` declares NFSD pNFS layout infrastructure used by NFSv4.1+ layout operations. It provides layout operation callbacks, device-id mapping, layout state preprocessing/return APIs, and no-op stubs when pNFS is disabled. The source was read as a complete 110-line file for this report.

## Important APIs, Types, and Functions

Important types are `struct nfsd4_deviceid_map` and `struct nfsd4_layout_ops`. Callback members cover device info, layout get, layout commit, layout encoding, client fencing, notification types, and recall behavior. Declarations include `nfsd4_preprocess_layout_stateid`, `nfsd4_insert_layout`, `nfsd4_return_file_layouts`, `nfsd4_return_client_layouts`, `nfsd4_set_deviceid`, `nfsd4_find_devid_map`, `nfsd4_setup_layout_type`, `nfsd4_return_all_client_layouts`, `nfsd4_return_all_file_layouts`, `nfsd4_close_layout`, `nfsd4_init_pnfs`, and `nfsd4_exit_pnfs`.

## Control Flow

The header itself has no executable control flow except stubs. In enabled builds, NFSv4 layout operations preprocess a layout stateid, call the export-selected layout backend through `nfsd4_layout_ops`, insert or return layout state, encode responses through XDR helpers, and optionally fence clients using backend-specific logic with retry backoff capped by `MAX_FENCE_DELAY`.

## State and Persistence Behavior

The declared state is live NFSv4/pNFS state: per-client and per-file layout stateids, layout segments, device-id maps keyed by fsid/device generation, and backend callbacks. There is no direct persistence here, but layout state interacts with client lease/grace semantics and backend fencing.

## Dependencies and Integration Points

This header depends on NFSv4 state (`state.h`), NFSv4 XDR (`xdr4.h`), exportfs, and export metadata. Optional backends include block, SCSI, and flexfile layouts. It is integrated by NFSv4 operation handlers and service/module init paths via `nfsd4_init_pnfs`/`nfsd4_exit_pnfs`.

## Risks and Edge Cases

Feature stubs must make non-pNFS builds behave as if no layouts exist. Device-id fsid encoding must match filehandle/export identity. Fencing retries can delay recovery; disabled recalls or unsupported backends must not leave clients with stale layout authority. Layout stateid preprocessing must distinguish create versus existing paths and layout types.

## Test Signals

Signals include build coverage with `CONFIG_NFSD_PNFS` off and each backend on, layoutget/layoutcommit/layoutreturn protocol tests, device-id stability checks, recall/fence retry behavior, client/file-wide layout return tests, and export option tests that enable or suppress layout types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/pnfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/state.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/state.h

## Purpose

`state.h` defines the internal NFSv4 state model: clientids, stateids, clients, sessions, callbacks, sequence slots, open/lock/delegation/layout state, replay caches, copy-notify state, blocked locks, recovery hooks, and grace management. The source was read as a complete 908-line file for this report.

## Important APIs, Types, and Functions

Important scalar types are `clientid_t`, `stateid_opaque_t`, `stateid_t`, and `copy_stateid_t`. Key structures include `nfsd4_callback`, `nfsd4_callback_ops`, `nfs4_stid`, `nfs4_cpntf_state`, `nfs4_cb_fattr`, `nfs4_delegation`, `nfs4_cb_conn`, `nfsd4_slot`, `nfsd4_channel_attrs`, `nfsd4_create_session`, `nfsd4_conn`, `nfsd4_session`, `nfs4_client`, `nfs4_client_reclaim`, `nfs4_replay`, `nfs4_stateowner`, `nfs4_openowner`, `nfs4_lockowner`, `nfs4_clnt_odstate`, `nfs4_file`, `nfs4_ol_stateid`, `nfs4_layout_stateid`, and `nfsd4_blocked_lock`. Declared operations cover stateid lookup/preprocessing, callback setup/run/shutdown, client put/probe/change, copy state, reclaim records, file refs, pNFS state revocation, client tracking, grace ending, delegation conflict checks, and directory delegations.

## Control Flow

Most flow is implemented elsewhere, but the header establishes object ownership and lookup paths. NFSv4 compounds resolve client/session/slot state, validate stateids through `nfs4_preprocess_stateid_op` and `nfsd4_lookup_stateid`, update sequence/replay caches, act on open/lock/deleg/layout stateids, and use callback objects for recalls, layout recalls, offload, notify-lock, recall-any, and CB_GETATTR. Inline helpers classify delegations, derive containing objects, compare stateid generations, run callbacks only once, and transition courtesy clients toward expiry.

## State and Persistence Behavior

This is the state schema for live NFSv4 service operation. Clients are hashed by id and name and can be active, courtesy, or expirable. Sessions own forward-channel slots and backchannel slot state. Stateids are refcounted and typed as open, lock, delegation, or layout. Replay buffers preserve seqid-mutating replies. Reclaim records and client tracking connect live state to stable reboot recovery, while grace-period APIs gate reclaim behavior. Async copy and copy-notify state have TTL/reaper behavior to avoid accumulation.

## Dependencies and Integration Points

Dependencies include MD5, IDR, refcounting, SunRPC transports, filehandle structures, and NFSD common declarations. The header is shared by NFSv4 XDR/procedure/state implementation files, pNFS, callbacks, nfsdfs client debug directories, lock handling, copy offload, and service startup/shutdown.

## Risks and Edge Cases

The main risks are refcount/list lifetime bugs, lock-order mistakes across `cl_lock`, `st_mutex`, `ls_lock`, `deleg_lock`, async locks, and session locks, replay cache sizing failures, and incorrect state transitions for revoked/freeable/closed stateids. Courtesy-client expiry is conflict-sensitive. Callback and backchannel state must handle connection loss. Layout and delegation recalls can race with client returns, revocation, and file teardown.

## Test Signals

Test with NFSv4.0 and v4.1+ client recovery, lease expiry, courtesy clients, OPEN/CLOSE/LOCK replay, session sequence slot replay, delegation recall/revoke/CB_GETATTR, async copy cleanup, blocked lock notify, pNFS layout recalls, admin revocation via filesystem unlock, and net namespace shutdown under active clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/stats.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/stats.c

## Purpose

`stats.c` exposes NFSD runtime statistics through `/proc/net/rpc/nfsd` using seq_file/proc helpers. It reports duplicate reply cache, filehandle, I/O, thread, generic RPC, and optional NFSv4 operation counters. The source was read as a complete 86-line file for this report.

## Important APIs, Types, and Functions

The main show function is `nfsd_show`. `DEFINE_PROC_SHOW_ATTRIBUTE(nfsd)` creates proc operations. Exported setup/teardown APIs are `nfsd_proc_stat_init` and `nfsd_proc_stat_shutdown`.

## Control Flow

`nfsd_proc_stat_init` registers the proc stats file for a net namespace using `svc_proc_register`; opening/reading the file invokes `nfsd_show`. The show function obtains the net namespace from proc inode data, retrieves `struct nfsd_net`, sums per-cpu counters, prints legacy-compatible lines, calls `svc_seq_show` for generic RPC stats, and conditionally appends NFSv4 operation and write-delegation getattr counters. Shutdown unregisters the proc entry by name.

## State and Persistence Behavior

No persistent state is stored here. The file reads live per-net `percpu_counter` arrays and the global `nfsd_th_cnt` atomic. Deprecated fields are printed as zeros to preserve proc output shape for existing tools.

## Dependencies and Integration Points

Dependencies include seq_file, procfs, SunRPC stats, net namespaces, `nfsd.h`, and UAPI counter indexes via `stats.h`. `nfsctl.c` calls initialization/shutdown during per-net lifecycle, and many NFSD paths increment the counters exposed here.

## Risks and Edge Cases

The proc output is user-visible and compatibility-sensitive. Counter sums are snapshots and may not be perfectly atomic across all fields. Adding or reordering fields can break parsers. NFSv4 operation output depends on `LAST_NFS4_OP` and counter index layout staying aligned.

## Test Signals

Signals include proc registration per net namespace, output format comparison with legacy expectations, counter increments for reply cache hits/misses/nocache, stale filehandles, I/O bytes, thread count changes, NFSv4 operation counters, and clean unregister during namespace teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/stats.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/stats.h

## Purpose

`stats.h` declares NFSD stats proc setup/teardown and provides inline helpers for updating per-net and per-export counters. The source was read as a complete 76-line file for this report.

## Important APIs, Types, and Functions

Declarations are `nfsd_proc_stat_init` and `nfsd_proc_stat_shutdown`. Inline counter helpers are `nfsd_stats_rc_hits_inc`, `nfsd_stats_rc_misses_inc`, `nfsd_stats_rc_nocache_inc`, `nfsd_stats_fh_stale_inc`, `nfsd_stats_io_read_add`, `nfsd_stats_io_write_add`, `nfsd_stats_payload_misses_inc`, `nfsd_stats_drc_mem_usage_add`, `nfsd_stats_drc_mem_usage_sub`, and, for NFSv4, `nfsd_stats_wdeleg_getattr_inc`.

## Control Flow

Callers pass `struct nfsd_net` and, when available, `struct svc_export`. The helpers increment or add/subtract `percpu_counter` values indexed by UAPI `NFSD_STATS_*` constants. Export-aware helpers update both the namespace counter and the export's `ex_stats` counter when present.

## State and Persistence Behavior

The state is live in per-net and per-export counter arrays. There is no persistence. The helpers are intentionally low-overhead and avoid locking around each increment by relying on percpu counters.

## Dependencies and Integration Points

The header depends on `uapi/linux/nfsd/stats.h` for stable counter indexes and `linux/percpu_counter.h`. It is pulled through `nfsd.h` and used by reply cache, filehandle verification, I/O paths, duplicate reply cache memory accounting, and NFSv4 delegation getattr paths.

## Risks and Edge Cases

Counter index drift between UAPI and `nfsd_net` allocation would corrupt reporting. Export stats are optional, so helpers must keep null checks. Per-cpu counters are approximate until summed, which is appropriate for stats but not for enforcement. Negative DRC memory accounting must remain balanced.

## Test Signals

Compile tests should verify all helpers see complete `struct nfsd_net` and export stats declarations. Runtime tests should assert namespace and export counters both move for stale filehandles and I/O, DRC memory add/sub pairs balance, and `/proc/net/rpc/nfsd` displays updated values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/trace.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/trace.c

## Purpose

`trace.c` is the tracepoint definition translation unit for NFSD. It defines `CREATE_TRACE_POINTS` before including `trace.h`, causing the trace event storage and descriptors declared in the header to be emitted exactly once. The source was read as a complete 4-line file for this report.

## Important APIs, Types, and Functions

There are no functions or types defined directly in this file. Its important API effect is compile-time: `CREATE_TRACE_POINTS` activates the Linux tracepoint macro definitions from `trace.h`.

## Control Flow

There is no runtime control flow in this file. At build time, it provides the single C translation unit that materializes NFSD tracepoints used by `nfsctl.c`, `nfsfh.c`, `nfsproc.c`, `nfssvc.c`, and other NFSD sources.

## State and Persistence Behavior

The file owns no runtime state beyond generated static tracepoint metadata. Trace buffers and event enablement are managed by the kernel tracing subsystem, not by this source.

## Dependencies and Integration Points

The only direct dependency is local `trace.h`. Integration is broad because all `trace_nfsd_*` call sites rely on this file being compiled into the NFSD object set exactly once.

## Risks and Edge Cases

If this file is omitted, tracepoint references fail to link or remain undefined. If `CREATE_TRACE_POINTS` is defined in more than one NFSD translation unit, duplicate definitions can result. Tracepoint ABI details are controlled by `trace.h`, but this file is the build-system anchor.

## Test Signals

Build/link NFSD with tracing enabled, verify representative `nfsd:*` trace events exist under tracefs/perf, enable events while exercising nfsdfs writes and RPC operations, and confirm no duplicate tracepoint definition warnings appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/trace.c -->
