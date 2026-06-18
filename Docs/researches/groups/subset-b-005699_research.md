# subset-b-005699 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/export.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/export.c

## Purpose
`export.c` implements the NFSD export lookup and validation layer. It maintains the two SUNRPC cache families that map `(client, path)` to `svc_export` records and `(client, fsid fragment)` to export paths, validates newly supplied export definitions from userspace, exposes export state through seq files, and provides request-time helpers for filehandle verification and NFSv4 pseudoroot discovery.

## Important APIs, types, and functions
The core objects are `struct svc_export` and `struct svc_expkey` from `export.h`, backed by `svc_export_cache_template` and `svc_expkey_cache_template`. Userspace cache population is handled by `svc_export_parse()` and `expkey_parse()`, with `check_export()` enforcing exportability, `fsloc_parse()`, `secinfo_parse()`, `xprtsec_parse()`, and `nfsd_uuid_parse()` parsing optional export attributes. Request-time lookup APIs include `rqst_exp_get_by_name()`, `rqst_exp_find()`, `rqst_exp_parent()`, `rqst_find_fsidzero_export()`, `exp_rootfh()`, and `exp_pseudoroot()`. Security policy is centralized in `check_xprtsec_policy()`, `check_security_flavor()`, and `check_nfsd_access()`. Lifecycle entry points are `nfsd_export_wq_init()`, `nfsd_export_wq_shutdown()`, `nfsd_export_init()`, `nfsd_export_flush()`, and `nfsd_export_shutdown()`.

## Control flow
At namespace initialization, NFSD creates and registers separate per-net cache instances for path exports and filehandle-key mappings. Cache misses trigger `sunrpc_cache_pipe_upcall()` so userspace mountd/exportfs can provide records. The parse paths decode qword records, resolve clients via `auth_domain_find()`, resolve paths with `kern_path()`, validate export flags and filesystem support, then update the relevant cache with `sunrpc_cache_update()`. Request lookup first tries the AUTH_SYS client, then falls back to a GSS client when needed; fsid-based lookup resolves an expkey to a path, then resolves that path to a real export. NFSv4 pseudoroot composition finds the fsid 0 export and delegates filehandle generation to `fh_compose()`.

## State and persistence
State is runtime cache state scoped by network namespace. Export objects own references to `auth_domain`, `struct path`, optional UUIDs, optional NFSv4 referral/replica locations, secinfo flavor arrays, xprtsec mode bits, pNFS layout metadata, and per-export counters. Expkey objects own client, fsid type/value, and an export path when positive. Object freeing is deferred through `rcu_work` on the global `nfsd_export` workqueue; namespace shutdown unregisters caches, waits for RCU, flushes the workqueue, destroys caches, and purges UNIX auth state. `nfsd_export_flush()` purges cache content and indirectly flushes filecache state through the expkey cache `flush` callback.

## Dependencies and integration points
This file integrates SUNRPC cache infrastructure, `auth_domain` client matching, VFS path and exportfs validation, NFSD filehandle helpers, pNFS layout setup, NFSv4 fs_locations/secinfo support, TLS/mTLS transport flags, tracepoints, and `/proc`/nfsdfs seq output. It depends on `nfsd_mutex` when purging the file cache from export-cache flushes. The transport-security checks inspect `svc_xprt` flags `XPT_TLS_SESSION` and `XPT_PEER_AUTH`.

## Risks and test signals
Risks are concentrated in cache lifetime and security policy: stale `svc_export` references after unregister, missed path or auth-domain references in update/free paths, malformed qword input leaking partial allocations, accepting non-exportable filesystems, idmapped mounts, unsupported subtree checking, incorrect secinfo fallback to GSS clients, and xprtsec bitmask mistakes. Test signals include export add/delete/flush under active I/O, fsid-key lookup for all supported fsid types, negative cache entries, GSS-only and mixed secinfo exports, TLS-only and mTLS-only exports, NFSv4 fsid 0 pseudoroot, fsloc/uuid parsing, expired exports, export_stats counter output, and namespace teardown with pending RCU work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/export.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/export.h

## Purpose
`export.h` defines the public data structures and helper APIs used by NFSD export lookup, export-cache management, and NFSv4 export metadata handling.

## Important APIs, types, and functions
Important types are `struct nfsd4_fs_location`, `struct nfsd4_fs_locations`, `struct exp_flavor_info`, `struct export_stats`, `struct svc_export`, and `struct svc_expkey`. It defines limits such as `MAX_FS_LOCATIONS`, `MAX_SECINFO_LIST`, and `EX_UUID_LEN`, export convenience macros `EX_ISSYNC()`, `EX_NOHIDE()`, and `EX_WGATHER()`, and declarations for `check_xprtsec_policy()`, `check_security_flavor()`, `check_nfsd_access()`, export init/shutdown/flush helpers, request lookup helpers, `exp_rootfh()`, and `exp_pseudoroot()`. Inline `exp_put()` and `exp_get()` wrap SUNRPC cache reference management.

## Control flow
The header has no control flow of its own, but it establishes the contract used by filehandle verification, NFSv3/NFSv4 request handlers, pNFS code, and export-cache code. Callers acquire `svc_export` references through lookup helpers and release them with `exp_put()`.

## State and persistence
`svc_export` is the persistent runtime representation of an exported path: client identity, flags, fsid, anonymous uid/gid, path, UUID, NFSv4 fs_locations, secinfo flavors, pNFS layout/device map, transport security modes, export stats, and cache/workqueue fields. `svc_expkey` is the runtime mapping from client and fsid bytes to a path. Neither structure represents durable storage; userspace reconstructs cache content as needed.

## Dependencies and integration points
The header depends on SUNRPC cache headers, percpu counters, workqueues, NFS export UAPI flags, and NFSv4 definitions. It is consumed by `export.c`, filehandle verification code, NFSv4 state/layout code, and request procedure implementations.

## Risks and test signals
Risk comes from structure ownership rules: `ex_path`, `ex_client`, `ex_uuid`, `ex_fslocs`, `ex_stats`, and `ek_path` must be reference-managed consistently by cache callbacks. API test signals include balanced `exp_get()`/`exp_put()` around every lookup, stable behavior with secinfo arrays at `MAX_SECINFO_LIST`, fs_locations at `MAX_FS_LOCATIONS`, and correct counter initialization/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/filecache.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/filecache.c

## Purpose
`filecache.c` implements NFSD's open-file cache. It lets NFSD reuse `struct file` objects keyed by inode, credential, namespace, access mode, and GC policy, while still closing cached files when leases, unlink/rename, export flush, namespace shutdown, memory pressure, or writeback-error handling require it.

## Important APIs, types, and functions
The primary object is `struct nfsd_file`, allocated from `nfsd_file_slab` and indexed in `nfsd_file_rhltable`. Public APIs include `nfsd_file_cache_init()`, `nfsd_file_cache_start_net()`, `nfsd_file_cache_purge()`, `nfsd_file_cache_shutdown_net()`, `nfsd_file_cache_shutdown()`, `nfsd_file_acquire_gc()`, `nfsd_file_acquire()`, `nfsd_file_acquire_opened()`, `nfsd_file_acquire_local()`, `nfsd_file_acquire_dir()`, `nfsd_file_put()`, `nfsd_file_get()`, `nfsd_file_file()`, `nfsd_file_put_local()`, `nfsd_file_close_inode_sync()`, `nfsd_file_net_dispose()`, `nfsd_file_is_cached()`, and `nfsd_file_cache_stats_show()`. Key internals include `nfsd_file_do_acquire()`, `nfsd_file_lookup_locked()`, `nfsd_file_cond_queue()`, LRU callbacks, the laundrette worker, fsnotify marks, and the lease notifier.

## Control flow
Global initialization creates the rhashtable, slabs, LRU, shrinker, lease notifier, fsnotify group, and delayed laundrette work. Per-net startup allocates a disposal queue. Acquisition verifies the filehandle, looks for a matching cached object under RCU, allocates and inserts a pending object on miss, opens or attaches a backing file, records direct-I/O alignment, installs fsnotify marks for regular files, then clears the pending bit to wake waiters. Garbage-collected acquisitions add an extra LRU reference and linger after callers drop their references. The laundrette and shrinker scan the LRU, skip active/writeback-pending objects, unhash evicted objects, and queue them to per-net disposal lists. Fsnotify, lease break notifications, unlink/rename, and purge paths unhash matching inode entries and close them synchronously or through per-net delayed disposal.

## State and persistence
State is all in-memory. Each `nfsd_file` stores the open file, captured credential, net namespace, inode key pointer, flags (`HASHED`, `PENDING`, `REFERENCED`, `GC`, `RECENT`), refcount, access mask, optional fsnotify mark, LRU/GC links, birth time, and DIO alignment fields. The hash table is global, while disposal queues are per `nfsd_net`. Per-CPU counters track hits, acquisitions, allocations, releases, aggregate age, and evictions. Shutdown purges hash contents, destroys LRU and marks after RCU/fsnotify synchronization, and resets counters.

## Dependencies and integration points
The file integrates VFS open/close helpers, `fh_verify()` and local filehandle verification, export flush paths, file leases, fsnotify, `list_lru`, shrinker infrastructure, rhashtable, RCU, per-net NFSD state, `nfslocalio`, write verifier reset logic, and tracepoints. NFSv3 COMMIT and normal read/write paths acquire cached objects; LOCALIO uses `nfsd_file_acquire_local()` and `nfsd_file_put_local()`.

## Risks and test signals
The main risks are concurrency and lifetime bugs: pending-object wait races, duplicate insertion around inode locking, refcount/LRU reference imbalance, freeing objects still linked on LRU, use of `nf_inode` as a comparison-only pointer, fsnotify mark destruction races, writeback error verifier resets, export flush while cache users are active, and LOCALIO net reference leaks. Test signals include concurrent read/write acquisition for the same inode and credential, failed opens followed by retry, `-EOPENSTALE` retry, GC under memory pressure, lease break and `FS_DELETE_SELF`/last-link events, NFS reexport unlink/rename silly-rename avoidance, per-net purge, module shutdown, LOCALIO cached pointer replacement races, and stats output after cache churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/filecache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/filecache.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/filecache.h

## Purpose
`filecache.h` declares the NFSD open-file cache interface and defines the cache object layouts shared with request, VFS, and LOCALIO code.

## Important APIs, types, and functions
It defines `NFSD_FILE_GC_BATCH`, `struct nfsd_file_mark`, and `struct nfsd_file`. `struct nfsd_file` contains the rhashtable node, inode key, backing `struct file`, credential, net namespace, flag bits, refcount, permission mask, fsnotify mark, LRU/GC links, RCU head, birth time, and DIO alignment fields. Public declarations cover cache lifecycle, reference management, backing-file access, inode close helpers, cached-inode checks, acquisition variants, and stats display.

## Control flow
The header makes acquisition style explicit: `nfsd_file_acquire_gc()` returns a reusable GC-managed object, `nfsd_file_acquire()` and `nfsd_file_acquire_opened()` return non-GC objects, `nfsd_file_acquire_dir()` opens directories, and `nfsd_file_acquire_local()` supports LOCALIO access without a normal RPC request. Callers must release returned objects with `nfsd_file_put()` or the LOCALIO wrapper path.

## State and persistence
The state described here persists only while the NFSD filecache is initialized. The inode field intentionally is not a live inode reference and must only be compared while the cache guarantees its validity through surrounding VFS/file lifetime rules.

## Dependencies and integration points
It depends on fsnotify backend types and declarations from NFSD net/filehandle/request code. The API is used by NFSv3 procedure code, LOCALIO, export flushing, VFS unlink/rename handling, and stats presentation.

## Risks and test signals
Risks include callers dereferencing `nf_inode`, missing `nfsd_file_put()` on error exits, using the wrong acquisition variant for GC semantics, and failing to hold/release net references in LOCALIO. Test signals include build coverage for all acquisition variants, Coccinelle-style reference-pair checks, and runtime tests for directory opens, existing-opened-file acquisition, and local filehandle access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/filecache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayout.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayout.c

## Purpose
`flexfilelayout.c` implements a minimal pNFS flex-file layout provider for NFSD where the metadata server is also the single data server and storage location is the same file exported over NFSv3.

## Important APIs, types, and functions
The exported integration object is `ff_layout_ops`. Its callbacks are `nfsd4_ff_proc_layoutget()`, `nfsd4_ff_proc_getdeviceinfo()`, and `nfsd4_ff_proc_layoutcommit()`, with XDR encoders supplied by `flexfilelayoutxdr.c`. It allocates and fills `struct pnfs_ff_layout` and `struct pnfs_ff_device_addr`.

## Control flow
For LAYOUTGET, the server allocates one layout descriptor, sets flags to avoid layoutcommit, discourage MDS I/O, and deny read I/O for RW layouts, adjusts uid for read-only segments to avoid write permission, derives a deviceid from the filehandle, copies the filehandle, and expands the granted segment to the whole file. For GETDEVICEINFO, it allocates one device address, sets NFSv3 version data, sizes from `svc_max_payload()`, derives netid and universal address from the request destination address, and returns it through `gd_device`. LAYOUTCOMMIT is accepted as a no-op.

## State and persistence
There is no durable layout state in this file. Per-request allocations are attached to NFSv4 layout response objects and encoded/freed by the surrounding pNFS code. Device generation is hard-coded to zero, and the layout is always a single mirror/single data-server model.

## Dependencies and integration points
The file depends on pNFS layout infrastructure, `nfsd4_set_deviceid()`, service payload sizing, RPC address formatting, and the flexfile XDR definitions. It is selected through export pNFS layout type setup and participates in NFSv4.1 pNFS operations.

## Risks and test signals
Risks include oversimplified topology assumptions, incorrect destination address selection behind NAT or multi-homed servers, uid manipulation causing unexpected client access behavior, deviceid generation collisions, and memory ownership between proc and encoder layers. Test signals include IPv4 and IPv6 GETDEVICEINFO, LAYOUTGET for read and read-write segments, whole-file segment verification, client behavior with `NO_READ_IO` and `NO_IO_THRU_MDS`, and pNFS disabled/export flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayoutxdr.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayoutxdr.c

## Purpose
`flexfilelayoutxdr.c` serializes NFSD flex-file pNFS layout and device-address data into NFSv4 XDR replies.

## Important APIs, types, and functions
The public encoders are `nfsd4_ff_encode_layoutget()` and `nfsd4_ff_encode_getdeviceinfo()`. They consume `struct pnfs_ff_layout` and `struct pnfs_ff_device_addr`, respectively. A small local `struct ff_idmap` stores decimal uid/gid strings.

## Control flow
`nfsd4_ff_encode_layoutget()` computes fixed and variable lengths for a single mirror, single data server, single filehandle flex-file layout; reserves XDR space; emits stripe unit, mirror/server counts, deviceid, efficiency, stateid, filehandle, uid/gid strings, flags, and stats hint. `nfsd4_ff_encode_getdeviceinfo()` handles the RFC 8881 zero-`gd_maxcount` probe by returning a zero length, otherwise reserves space for one netaddr and one version tuple and emits netid, universal address, NFS version/minor, rsize, wsize, and tight-coupling flag.

## State and persistence
The file has no retained state. It trusts that the layout and device structures attached by `flexfilelayout.c` remain valid for the duration of encoding.

## Dependencies and integration points
It depends on SUNRPC XDR stream helpers, NFSv4 constants, `svcxdr_encode_deviceid4()`, and flexfile structures in `flexfilelayoutxdr.h`. Its return values are NFS status codes such as `nfserr_toosmall` and `nfserr_resource` consumed by NFSv4 compound encoding.

## Risks and test signals
Risks include length miscalculation, failing to reserve enough padded XDR space, uid/gid string truncation if assumptions change, and mismatching RFC flex-file layout field order. Test signals include layout encoding under small reply buffers, zero maxcount GETDEVICEINFO, IPv6 universal addresses near `FF_ADDR_LEN`, non-root uid/gid values, and XDR decode validation by Linux and non-Linux pNFS clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayoutxdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayoutxdr.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayoutxdr.h

## Purpose
`flexfilelayoutxdr.h` defines the in-memory flex-file pNFS layout/device structures that `flexfilelayout.c` populates and `flexfilelayoutxdr.c` encodes.

## Important APIs, types, and functions
It defines flexfile flag bits `FF_FLAGS_NO_LAYOUTCOMMIT`, `FF_FLAGS_NO_IO_THRU_MDS`, and `FF_FLAGS_NO_READ_IO`; address length constants `FF_NETID_LEN` and `FF_ADDR_LEN`; `struct pnfs_ff_netaddr`; `struct pnfs_ff_device_addr`; and `struct pnfs_ff_layout`. It declares `nfsd4_ff_encode_getdeviceinfo()` and `nfsd4_ff_encode_layoutget()`.

## Control flow
There is no executable flow. The header establishes a two-stage contract: layout callbacks allocate/fill these structures, then XDR callbacks serialize them into protocol replies.

## State and persistence
The structures are per-operation response state. They contain protocol-level values such as NFS version, payload sizes, uid/gid, deviceid, stateid, and filehandle copies, but no durable server registry.

## Dependencies and integration points
The header depends on IPv6 address length definitions and NFSD NFSv4 XDR types. It is included by the pNFS flexfile provider and its encoder.

## Risks and test signals
Risks include fixed string buffers becoming too small for future netids/universal address forms, flag definitions diverging from encoder behavior, and structure ownership ambiguity. Test signals include compile-time users of both encoders, maximum-length universal address generation, and pNFS client decode coverage for every flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/flexfilelayoutxdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/idmap.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/idmap.h

## Purpose
`idmap.h` declares NFSD's NFSv4 name/id mapping interface and provides no-op lifecycle stubs when NFSv4 server support is disabled.

## Important APIs, types, and functions
The header declares `nfsd_idmap_init()`, `nfsd_idmap_shutdown()`, `nfsd_map_name_to_uid()`, `nfsd_map_name_to_gid()`, `nfsd4_encode_user()`, and `nfsd4_encode_group()`. The lifecycle functions are real only under `CONFIG_NFSD_V4`; otherwise inline stubs return success or do nothing.

## Control flow
Callers can unconditionally initialize and shut down idmapping as part of per-net NFSD setup. NFSv4 attribute encode/decode paths call the mapping helpers to translate owner/group strings to kernel ids and kernel ids to protocol strings.

## State and persistence
The header itself has no state. Enabled builds rely on per-net id-to-name and name-to-id caches stored in `struct nfsd_net`, while disabled builds eliminate that runtime state.

## Dependencies and integration points
It depends on SUNRPC service request types and kernel NFS idmap definitions. It integrates with NFSv4 ACL and attribute XDR handling, user namespace mapping, and per-net NFSD cache setup.

## Risks and test signals
Risks include enabled/disabled build drift, returning malformed owner/group names, idmapping cache misses surfacing as NFS errors, and user-namespace mismatches. Test signals include NFSv4 disabled builds, idmap cache init/shutdown per namespace, numeric and named owner/group encodes, unknown principal decode errors, and ACL paths that contain both special and named principals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/idmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/localio.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/localio.c

## Purpose
`localio.c` supports local NFS clients bypassing the network stack by opening NFSD filehandles directly through server-side authorization and filecache APIs. It also defines a hidden LOCALIO RPC version used to register/check whether a client UUID is local.

## Important APIs, types, and functions
The central helper is `nfsd_open_local_fh()`, exposed through `struct nfsd_localio_operations nfsd_localio_ops` installed by `nfsd_localio_ops_init()`. Other operation callbacks include `nfsd_net_try_get`, `nfsd_net_put`, `nfsd_file_put_local`, `nfsd_file_file`, and `nfsd_file_dio_alignment()`. RPC handling includes `localio_proc_null()`, `localio_proc_uuid_is_local()`, `localio_decode_uuidarg()`, `localio_procedures1`, and `localio_version1`.

## Control flow
LOCALIO open validates filehandle size, pins the NFSD net namespace, tries an already cached local `nfsd_file` pointer under RCU, converts an NFS filehandle into `svc_fh`, maps client RPC credentials into `svc_cred`, calls `nfsd_file_acquire_local()`, releases temporary credential state, then atomically installs the resulting file pointer for reuse. If another thread wins installation, the function drops the extra file and net references and returns the already installed object. The UUID RPC decodes a fixed UUID and calls `nfs_uuid_is_local()` to update per-net local client tracking.

## State and persistence
State is runtime-only: cached LOCALIO `nfsd_file` pointers supplied by the NFS client, net namespace references paired with those pointers, and `nfsd_net.local_clients` membership. Cached DIO alignment fields are read from `struct nfsd_file`. Shutdown invalidates local clients from the filecache purge path.

## Dependencies and integration points
It depends on NFSD VFS/filecache/filehandle verification, SUNRPC auth mapping, NFS client LOCALIO hooks (`nfs_to`), `nfslocalio`, per-net NFSD state, and the hidden RPC program/version dispatch table. It bridges client kernel context to server authorization code, which is a stronger integration boundary than normal network RPC.

## Risks and test signals
Risks include net reference leaks or premature drops, stale cached local file pointers, racing `cmpxchg()` installation, missing credential cleanup, bypassing connection-based authorization, invalid filehandle sizes, and local-client invalidation during namespace shutdown. Test signals include concurrent LOCALIO opens of the same filehandle, read/write mode combinations, server shutdown while local files are cached, failed `nfsd_net_try_get()`, credential mapping with supplemental groups, DIO alignment propagation, UUID_IS_LOCAL from multiple clients, and LOCALIO disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/localio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/lockd.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/lockd.c

## Purpose
`lockd.c` provides the binding glue that lets lockd/NLM open and close files through NFSD without creating a hard module dependency between the NFS client, lockd, and nfsd modules.

## Important APIs, types, and functions
The binding object is `nfsd_nlm_ops` with callbacks `nlm_fopen()` and `nlm_fclose()`. Public lifecycle functions are `nfsd_lockd_init()` and `nfsd_lockd_shutdown()`, which assign or clear global `nlmsvc_ops`.

## Control flow
`nlm_fopen()` constructs a temporary `svc_fh` from an NFS filehandle, computes read or write access from POSIX open flags, adds NLM-specific bypass flags, calls `nfsd_open()`, releases the filehandle, and maps NFS status values to lockd errno values. `nfserr_jukebox` is translated to `-EWOULDBLOCK` so delegation conflicts can be retried. `nlm_fclose()` simply `fput()`s the file acquired through NFSD.

## State and persistence
The only state is the global lockd binding pointer. Opened files are ordinary `struct file` references held by lockd until `nlm_fclose()`.

## Dependencies and integration points
It integrates lockd's `nlmsvc_binding` interface with NFSD filehandle verification and VFS open behavior. The access flags intentionally allow GSS bypass and `NFSD_MAY_NLM` so exports with `insecure_locks` can authorize legacy NLM requests.

## Risks and test signals
Risks include incorrect NFS-to-errno mapping, accepting AUTH_NULL/AUTH_SYS NLM where exports did not intend it, delegation conflict behavior causing client-visible lock failures, and global binding races at module shutdown. Test signals include NLM read/write lock opens, stale filehandles, GSS NFS with AUTH_SYS NLM, `NFSEXP_NOAUTHNLM` exports, delegation conflict retries, and lockd activity across nfsd module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/lockd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/netlink.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/netlink.c

## Purpose
`netlink.c` is generated Generic Netlink glue for NFSD administrative control. It defines attribute validation policies, command operation tables, and the NFSD netlink family registration object.

## Important APIs, types, and functions
The file exports nested policies `nfsd_sock_nl_policy` and `nfsd_version_nl_policy`, defines command-specific policies for thread, version, listener, and pool-mode setters, and builds `nfsd_nl_ops`. The public family is `struct genl_family nfsd_nl_family`.

## Control flow
Generic Netlink dispatch validates incoming attributes using the policy for each set operation, then calls handlers declared in `netlink.h`: RPC status dump, thread set/get, version set/get, listener set/get, and pool mode set/get. Admin-only setters carry `GENL_ADMIN_PERM`; read operations advertise do or dump capabilities. The family is namespace-aware and allows parallel operations.

## State and persistence
The file itself holds static policy/ops tables only. Persistent runtime state is managed by the handler implementations elsewhere in NFSD and by per-net `struct nfsd_net`.

## Dependencies and integration points
It is generated from `Documentation/netlink/specs/nfsd.yaml` and depends on Generic Netlink, UAPI `linux/nfsd_netlink.h`, and NFSD handler functions. It is the structured netlink counterpart to older nfsdfs control files.

## Risks and test signals
Risks include generated code drifting from the YAML spec, too-permissive or too-strict attribute policies, incorrect admin permission flags, parallel operation races in handlers, and ABI incompatibility with userspace YNL clients. Test signals include YNL conformance tests for every command, malformed nested attributes, missing optional attributes, non-admin setter attempts, network namespace isolation, and concurrent setter/getter calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/netlink.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/netlink.h

## Purpose
`netlink.h` is the generated header for the NFSD Generic Netlink family. It publishes policies, handler prototypes, and the family object to the rest of the NFSD module.

## Important APIs, types, and functions
It declares `nfsd_sock_nl_policy`, `nfsd_version_nl_policy`, handler prototypes for RPC status dump and all server thread/version/listener/pool-mode get/set commands, and `extern struct genl_family nfsd_nl_family`.

## Control flow
There is no executable flow. Including code registers `nfsd_nl_family`, while the generated ops table in `netlink.c` calls the handler prototypes declared here.

## State and persistence
The header has no state. It describes static netlink family wiring and delegates all mutable server state to handler implementations.

## Dependencies and integration points
It depends on Generic Netlink kernel headers and the NFSD netlink UAPI. Because it is generated from YAML, its contract is shared with userspace YNL tooling.

## Risks and test signals
Risks include manual edits being overwritten or diverging from generated `netlink.c`, prototype mismatches with handler implementations, and UAPI/spec drift. Test signals include regeneration from the YAML spec, build coverage for every declared handler, and userspace netlink ABI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/netns.h -->
# sources/distributed-fs/ceph-client/fs/nfsd/netns.h

## Purpose
`netns.h` defines `struct nfsd_net`, the per-network-namespace state container for NFSD. It centralizes export caches, idmapping caches, NFSv4 client/session/lock/delegation state, duplicate reply cache state, counters, server lifetime references, copy state, version settings, LOCALIO tracking, and callback infrastructure.

## Important APIs, types, and functions
Important definitions include client/session hash sizing constants, the NFSD stats counter enum, `struct nfsd_net`, `nfsd_netns_ready()`, `nfsd_support_version()`, `nfsd_net_id`, `nfsd_net_try_get()`, `nfsd_net_put()`, `nfsd_copy_write_verifier()`, and `nfsd_reset_write_verifier()`.

## Control flow
The header has no direct execution, but it defines fields used across NFSD startup, shutdown, request dispatch, NFSv4 state management, reply-cache lookup, export lookup, filecache disposal, and LOCALIO invalidation. Most users obtain it with `net_generic(net, nfsd_net_id)`.

## State and persistence
`struct nfsd_net` is dense runtime state. It includes SUNRPC caches, idmapper caches, NFSv4 grace/lease timing, client tracking structures, client/session hash tables, laundromat work, locks, reclaim tracking, service pointer/refcounts/completions, write verifier seqlock and bytes, version bitmaps, duplicate reply cache tables and shrinker, stats counters, server-to-server copy mounts, namespace server name, filecache disposal list, siphash keys, client-count limits, courtesy-client shrinker work, LOCALIO client list, filehandle key, and callback state. Persistence across restart is mediated by client tracking backends, not by this header itself.

## Dependencies and integration points
It depends on net namespaces, lock manager types, NFSv4 constants, percpu counters/refcounts, siphash, and SUNRPC stats. It is included by almost every NFSD subsystem, making it the central integration point for per-net isolation.

## Risks and test signals
Risks include lock-order mistakes among `client_mutex`, `client_lock`, `deleg_lock`, `blocked_locks_lock`, and copy/localio locks; partial initialization leaving `nfsd_netns_ready()` misleading; per-net teardown while references remain; DRC stats updated with weak locking; write verifier races; and feature fields compiled conditionally. Test signals include namespace create/destroy loops, NFSv4 grace/reclaim tests, DRC stress and shrinker paths, server thread start/stop, write verifier reset after writeback error, LOCALIO invalidation, server-to-server copy shutdown, and all supported NFS version toggles per namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/netns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs2acl.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfs2acl.c

## Purpose
`nfs2acl.c` implements the version 2 NFSACL side protocol for NFSD. It exposes NULL, GETACL, SETACL, GETATTR, and ACCESS procedures over the NFSD dispatcher using NFSv2-style filehandles and NFSv3 ACL helper structures.

## Important APIs, types, and functions
Procedure handlers are `nfsacld_proc_null()`, `nfsacld_proc_getacl()`, `nfsacld_proc_setacl()`, `nfsacld_proc_getattr()`, and `nfsacld_proc_access()`. XDR helpers decode GETACL/SETACL/ACCESS arguments and encode GETACL/ACCESS replies. Release helpers free filehandles and POSIX ACL references. The registration object is `const struct svc_version nfsd_acl_version2` backed by `nfsd_acl_procedures2`.

## Control flow
GETACL verifies the filehandle with no-op access, validates the requested mask, gets attributes, fetches access/default POSIX ACLs, synthesizes a minimal access ACL from inode mode when absent, and defers ACL release to the release hook. SETACL verifies setattr permission, obtains write access, locks the inode, sets access and default POSIX ACLs, unlocks/drops write access, gets final attributes, and releases decoded ACLs. GETATTR and ACCESS are thin wrappers around `fh_getattr()` and `nfsd_access()`. The procedure table wires decode, encode, release, cache behavior, and estimated XDR response sizes.

## State and persistence
This service stores no private state. Persistent effects occur only when SETACL writes POSIX ACLs to the target inode through the filesystem. Per-CPU procedure counters are maintained by the service dispatch layer.

## Dependencies and integration points
It depends on NFSD filehandle verification, VFS POSIX ACL helpers, NFSACL stream encode/decode helpers, NFSD attribute and access helpers, and the generic `nfsd_dispatch` path. It shares several NFSv3 ACL data structures even though it registers protocol version 2.

## Risks and test signals
Risks include mask validation differences from v3 (`nfserr_io` for bad GETACL mask), setting default ACLs on non-directories, ACL memory leaks on decode or partial failure, inode lock/write-access ordering, and Solaris compatibility assumptions. Test signals include GETACL with access/default/count masks, files without stored ACLs, SETACL with invalid masks, non-directory default ACL attempts, ACCESS with varied permission bits, release-hook leak checks, and v2 ACL client interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs2acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs3acl.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfs3acl.c

## Purpose
`nfs3acl.c` implements the NFSACL version 3 side protocol for NFSD, exposing NULL, GETACL, and SETACL procedures with NFSv3 filehandle and post-op-attribute encoding.

## Important APIs, types, and functions
Procedure handlers are `nfsd3_proc_null()`, `nfsd3_proc_getacl()`, and `nfsd3_proc_setacl()`. XDR helpers are `nfs3svc_decode_getaclargs()`, `nfs3svc_decode_setaclargs()`, `nfs3svc_encode_getaclres()`, `nfs3svc_encode_setaclres()`, and `nfs3svc_release_getacl()`. The service table is `nfsd_acl_procedures3`, exported through `nfsd_acl_version3`.

## Control flow
GETACL decodes an NFSv3 filehandle and mask, verifies access, rejects unknown mask bits with `nfserr_inval`, fetches requested access/default POSIX ACLs, synthesizes an access ACL from mode if absent, and encodes status plus post-op attrs and ACL payloads. SETACL decodes optional access/default ACLs according to the mask, verifies setattr permission, takes write access, locks the inode, sets both ACL types, unlocks/drops write access, and encodes status plus post-op attributes. Release hooks free filehandles and ACL references.

## State and persistence
The module maintains only per-CPU procedure counters. SETACL persists ACL changes in the backing filesystem; GETACL state is temporary POSIX ACL references attached to the response.

## Dependencies and integration points
It depends on NFSv3 XDR helpers in `nfs3xdr.c`, POSIX ACL VFS helpers, NFSD filehandle/access infrastructure, and `nfsd_dispatch`. It complements the core NFSv3 procedure table in `nfs3proc.c`.

## Risks and test signals
Risks include ACL reference leaks, post-op attrs after failure, invalid mask handling, setting ACLs under idmapped-mount assumptions (`nop_mnt_idmap`), and filesystem-specific ACL rejection. Test signals include Linux NFSv3 ACL client GETACL/SETACL, invalid masks, missing access ACL synthesis, default ACL on non-directory, filesystem without ACL support, and reply-size limits for maximum ACL entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs3acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs3proc.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfs3proc.c

## Purpose
`nfs3proc.c` implements NFSD's NFSv3 procedure layer. It maps decoded RPC arguments to NFSD VFS/filehandle/filecache helpers, applies NFSv3-specific semantics and status mappings, and registers the NFSv3 procedure table.

## Important APIs, types, and functions
Procedure handlers cover all NFSv3 calls: NULL, GETATTR, SETATTR, LOOKUP, ACCESS, READLINK, READ, WRITE, CREATE, MKDIR, SYMLINK, MKNOD, REMOVE, RMDIR, RENAME, LINK, READDIR, READDIRPLUS, FSSTAT, FSINFO, PATHCONF, and COMMIT. Important helpers include `nfsd3_map_status()`, `nfsd3_create_file()`, and `nfsd3_init_dirlist_pages()`. The registration objects are `nfsd_procedures3` and `const struct svc_version nfsd_version3`.

## Control flow
Each handler copies or initializes response filehandles, calls the relevant NFSD helper, maps internal status through `nfsd3_map_status()`, and returns RPC-level success so the protocol status is encoded in the reply. READ clamps count to service payload and reply buffer limits and clamps offsets to `OFFSET_MAX`. WRITE validates offset plus length before calling `nfsd_write()`. CREATE implements unchecked, guarded, and exclusive verifier semantics, including Solaris/XFS high-bit masking on verifier timestamps and post-create setattr handling. READDIR/READDIRPLUS allocate reply pages, run `nfsd_readdir()` with NFSv3 entry encoders, backpatch cookies, and recycle unused pages. COMMIT obtains a GC-managed writable `nfsd_file` before calling `nfsd_commit()`.

## State and persistence
The procedure layer is mostly stateless. Persistent effects are delegated to VFS operations for writes, creates, removes, renames, links, setattr, symlink, mknod, and commits. Runtime response state includes filehandles, weak-cache-consistency attrs, page buffers, readdir cookies, and write verifiers. Per-CPU procedure counters are maintained by the RPC service layer.

## Dependencies and integration points
It depends on `xdr3.h` decode/encode functions, `vfs.c` NFSD operation helpers, filecache acquisition for COMMIT, export flags such as `NFSEXP_NOREADDIRPLUS`, filesystem magic constants for FSINFO/PATHCONF behavior, tracepoints, and duplicate reply cache policy via `pc_cachetype`. Non-idempotent operations are marked `RC_REPLBUFF`.

## Risks and test signals
Risks include incorrect internal-to-v3 status mapping, offset/count overflow, response page accounting in READDIR, exclusive create verifier compatibility, stale filehandle release, weak-cache-consistency attr correctness, READDIRPLUS filehandle composition across mountpoints/export roots, and duplicate reply cache classification. Test signals include full NFSv3 connectathon/pynfs coverage, large read/write boundary tests, exclusive create replay, non-idempotent duplicate RPC replay, READDIRPLUS with `nordirplus`, FSINFO/PATHCONF on ext2/msdos/other filesystems, COMMIT after unstable writes, and symlink target page-boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs3proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs3xdr.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfs3xdr.c

## Purpose
`nfs3xdr.c` implements XDR decoding, encoding, directory-entry construction, and release helpers for NFSD's NFSv3 service.

## Important APIs, types, and functions
Public helpers include `svcxdr_decode_nfs_fh3()`, `svcxdr_encode_nfsstat3()`, `svcxdr_encode_post_op_attr()`, all `nfs3svc_decode_*args()` functions, all `nfs3svc_encode_*res()` functions, `nfs3svc_encode_cookie3()`, `nfs3svc_encode_entry3()`, `nfs3svc_encode_entryplus3()`, `nfs3svc_release_fhandle()`, and `nfs3svc_release_fhandle2()`. Important internals include `svcxdr_decode_sattr3()`, `svcxdr_decode_filename3()`, `svcxdr_encode_fattr3()`, `svcxdr_encode_wcc_data()`, and `compose_entry_fh()`.

## Control flow
Decode helpers validate filehandle sizes, filename length and separators, sattr discriminants, create modes, write payload count/length consistency, readdir verifiers, and commit ranges. Write decode clamps oversized payloads to `svc_max_payload()` and creates an XDR subsegment. Encode helpers emit status first, then conditionally emit post-op attrs, WCC data, filehandles, payload page references, write verifiers, and filesystem/pathconf data. READ and READLINK encoders attach page payloads with `svc_encode_result_payload()`. READDIR entry encoding reserves a placeholder cookie, commits entries only on success, backpatches the previous cookie when the next entry arrives, and rolls back `dirlist.len` on buffer exhaustion. READDIRPLUS composes per-entry filehandles and attributes unless the entry is a mountpoint or outside the export root.

## State and persistence
No durable state is stored. Transient state lives in response structures: XDR stream positions, `dirlist` buffers, page pointers, cookie offsets, scratch filehandles, status fields, and saved pre/post attributes. Encoded fsids derive from export fsid, export UUID, or superblock device encoding.

## Dependencies and integration points
It depends on SUNRPC XDR stream/page helpers, NFSD filehandle and attribute helpers, NFSv3 protocol constants, export metadata for fsid source, user namespace mapping for uid/gid encoding, lease mtime adjustment, and VFS lookup for READDIRPLUS filehandle composition. It is wired into `nfs3proc.c` procedure descriptors.

## Risks and test signals
Risks include XDR length/padding errors, accepting malformed names or handles, uid/gid mapping surprises, symlink size clamping, fsid derivation mismatches, WCC/post-op attr omission after failures, READDIR cookie corruption, READDIRPLUS races with rename/unlink/mountpoints, and buffer exhaustion handling. Test signals include XDR fuzzing, max-size filehandles and names, names containing NUL or slash, write count/opaque length mismatch, reply buffer exhaustion for every encoder, READDIR cookie replay, READDIRPLUS on `.`/`..` and mountpoints, UUID fsid exports, and user namespace id encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs3xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs4acl.c -->
# sources/distributed-fs/ceph-client/fs/nfsd/nfs4acl.c

## Purpose
`nfs4acl.c` translates between Linux POSIX ACLs/mode bits and NFSv4 ACL ACE lists for NFSD. It supports encoding filesystem ACLs as NFSv4 ACLs and converting client-supplied NFSv4 ACL attributes back into POSIX access/default ACLs.

## Important APIs, types, and functions
Public entry points include `nfsd4_get_nfs4_acl()`, `sort_pacl_range()`, `nfsd4_acl_to_attr()`, `nfs4_acl_bytes()`, `nfs4_acl_get_whotype()`, and `nfs4_acl_write_who()`. Major internal helpers include `mask_from_posix()`, `deny_mask_from_posix()`, `low_mode_from_nfs4()`, `summarize_posix_acl()`, `_posix_to_nfsv4_one()`, `sort_pacl()`, state allocation/free helpers, `process_one_v4_ace()`, `nfs4_acl_nfsv4_to_posix()`, and `ace2type()`.

## Control flow
For POSIX-to-NFSv4, the code fetches the access ACL or synthesizes one from mode, optionally fetches a directory default ACL, allocates a worst-case NFSv4 ACL, summarizes effective POSIX permissions under the mask, then emits ALLOW and DENY ACEs for owner, named users, owning group, named groups, and everyone. Default ACLs receive inheritance and inherit-only flags. For NFSv4-to-POSIX, the code initializes effective and default permission state, rejects unsupported ACE types or flags, routes inherited ACEs to default state only for directories, applies ALLOW/DENY masks in order, copies missing owner/group/other entries from effective state into default state when needed, builds POSIX ACLs, sorts named users/groups, and maps `-EINVAL` to `nfserr_attrnotsupp`.

## State and persistence
State is temporary conversion state only. `struct posix_acl_state` accumulates allow/deny masks for owner, group, other, everyone, named users, named groups, and POSIX mask. Resulting `na_pacl` and `na_dpacl` are attached to `struct nfsd_attrs` so the VFS setattr path can persist them. The special who-string table maps `OWNER@`, `GROUP@`, and `EVERYONE@`; all other names are treated as named principals.

## Dependencies and integration points
It depends on POSIX ACL APIs, NFSD ACL structures, VFS attribute setting, NFSv4 XDR streams, kernel uid/gid helpers, and filesystem ACL support. NFSv4 GETATTR/SETATTR ACL paths call these helpers during attribute encode/decode.

## Risks and test signals
Risks are semantic loss in both directions, especially DENY ordering, POSIX mask derivation, default ACL inheritance, directory delete-child handling, unsupported NFSv4 flags, named user/group sorting before `posix_acl_valid()`, and conservative permission reduction in `low_mode_from_nfs4()`. Test signals include round-trip ACL tests with owner/named user/group/everyone entries, DENY-before-ALLOW cases, inherited directory ACLs, files receiving inheritance flags, unsupported ACE types/flags, empty ACLs, ACLs without default owner/group/other entries, maximum ACE counts, special who-string encode/decode, and filesystems without POSIX ACL support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfsd/nfs4acl.c -->
