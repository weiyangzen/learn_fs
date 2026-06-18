# subset-b-009717 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/idmapper.h -->
# sources/user-network-fs/nfs-ganesha/src/include/idmapper.h

## Purpose

`idmapper.h` is the public and semi-private declaration point for Ganesha's ID mapper. It binds numeric UID/GID values, group lists, GSS principals, and NFSv4 owner/group strings together for protocol request handling. The header also exposes cache lifecycle APIs and DBus cache inspection hooks.

## Important APIs, Types, and Functions

The cache API is split between positive caches (`idmapper_add_user`, `idmapper_add_group`, lookup by name/id) and negative caches (`idmapper_negative_cache_add_*`, lookup, clear, destroy, reap). The five exported `pthread_rwlock_t` objects protect user, group, and negative-cache maps shared by `idmapper.c` and `idmapper_cache.c`. Public conversion APIs include `name2uid`, `name2gid`, `xdr_encode_nfs4_owner`, `xdr_encode_nfs4_group`, and optional `_HAVE_GSSAPI` `principal2uid`. `PWENT_BEST_GUESS_LEN`, `PWENT_MAX_SIZE`, and `GROUP_MAX_SIZE` bound passwd/group-entry buffer growth.

## Control Flow

Typical NFSv4 processing decodes an owner string with `name2uid` or encodes numeric IDs with the XDR helpers. The implementation first consults idmapper caches, may call libc/nfsidmap/winbind/GSS backends, inserts success or negative results, and exposes periodic cleanup through `idmapper_cache_reap` and `idmapper_negative_cache_reap`.

## State and Persistence Behavior

State is in process memory only: positive maps, negative maps, and timing/stat counters. `idmapper_clear_cache` and `idmapper_destroy_cache` are explicit invalidation/lifetime controls; no durable mapping database is declared here.

## Dependencies and Integration Points

The header depends on `gsh_rpc.h`, `gsh_types.h`, XDR, POSIX IDs, pthread locks, optional GSSAPI/MSPAC, optional DBus, and monitoring update functions for winbind, group-cache, and DNS latencies. It integrates with NFSv4 ACL/attribute encoding, credential establishment, and admin cache diagnostics.

## Risks and Test Signals

Risks are stale mappings, negative-cache poisoning after directory-service recovery, lock-order bugs across user/group caches, huge passwd/group records up to 64 MiB, and GSS conditional ABI differences. Tests should cover cache hit/miss/reap paths, name/domain variants, unmapped names, principal mapping with and without MSPAC, DBus cache display, cache clear during live requests, and owner/group XDR round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/idmapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/idmapper_monitoring.h -->
# sources/user-network-fs/nfs-ganesha/src/include/idmapper_monitoring.h

## Purpose

`idmapper_monitoring.h` declares the metrics surface for ID mapping. It gives idmapper implementations stable enum label sets for external resolver latency, operation success/failure, cache usage, group-count observations, and cache eviction/reap accounting.

## Important APIs, Types, and Functions

The enums define metric dimensions: `idmapping_utility_t` distinguishes pwutils, nfsidmap, and winbind; `idmapping_op_t` names UID/user/group/principal/SID resolution flows; `idmapping_cache_t` names positive and negative cache lookup classes; `idmapping_cache_entity_t` aggregates entity types; and `idmapping_status_t` separates success and failure. Update functions include `idmapper_monitoring__external_request`, `__cache_usage`, `__resolution`, `__user_groups`, `__evicted_cache_entity`, `__reaped_cache_entity`, and `__cache_entries_total_set`.

## Control Flow

The monitoring package is registered once through `idmapper_monitoring__init`. Resolver code records elapsed times with start/end `timespec` values, cache lookup code records hit/miss events, and cache maintenance records evicted or reaped entity classes.

## State and Persistence Behavior

No cache state is owned by this header. Implementations likely keep metric handles registered with the dynamic metrics subsystem; exported values are process-lifetime counters, gauges, or histograms.

## Dependencies and Integration Points

It depends on `common_utils.h` for elapsed-time types and on the ID mapper's resolver/cache code. Metrics consumers are monitoring exporters and operational dashboards that need to diagnose directory-service latency, cache effectiveness, and max-group-limit behavior.

## Risks and Test Signals

The enum order is a metrics label ABI; inserting values in the middle can break dashboards. Callers must not pass out-of-range enum values and should consistently mark success/failure. Tests should initialize metrics, emit each enum path, verify cache hit/miss counters, confirm latency buckets use nonnegative durations, and validate max-groups and cache-entry gauges after cache mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/idmapper_monitoring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/ip_utils.h -->
# sources/user-network-fs/nfs-ganesha/src/include/ip_utils.h

## Purpose

`ip_utils.h` centralizes socket address and CIDR utilities used by export/client matching, duplicate request cache keys, logging, and network identity handling. It covers IPv4, IPv6, optional VSOCK, loopback/any checks, display formatting, hashing, and IPv4-mapped IPv6 normalization.

## Important APIs, Types, and Functions

`sockaddr_t` aliases `sockaddr_storage`; `CIDR` stores an address and mask. CIDR APIs allocate, duplicate, parse from string, render to string, compare, normalize v4-mapped addresses, compute family/protocol/version, and test containment. Socket APIs include `sockaddr_cmp`, `hash_sockaddr`, `ip_str_to_sockaddr`, `get_port`, `get_sockport`, address conversion helpers, `is_loopback`, `is_inaddrany`, and display helpers. Inline `socket_addr`, `socket_addr_len`, and `sprint_sockip` abstract per-family payload access.

## Control Flow

Callers parse configuration or client identities into `sockaddr_t`/`CIDR`, normalize comparable forms, hash or compare addresses with optional port inclusion, and format addresses for logs or metrics. Export client matching can use CIDR containment and HA/proxy-aware address selection upstream.

## State and Persistence Behavior

The utilities are stateless except for allocated `CIDR` and string results owned by callers. Network identities may become persistent only when other subsystems store parsed addresses in caches or export/client entries.

## Dependencies and Integration Points

The header depends on libc networking headers, byte-order helpers, `display.h`, and optional RPC VSOCK definitions. It integrates with `log.h`, `nfs_dupreq.h`, client/export managers, IP-name cache, and conditional logging.

## Risks and Test Signals

Risks include inconsistent IPv4-mapped IPv6 normalization, comparing ports when callers expect host-only identity, VSOCK length/hash mistakes, buffer truncation in `sprint_sockip`, and ownership leaks from `cidr_to_str`. Tests should cover IPv4/IPv6/v4-mapped parsing, CIDR edge masks, port-sensitive and port-insensitive compare/hash, AF_LOCAL/VSOCK branches when enabled, display buffer truncation, and invalid input rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/ip_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/log.h -->
# sources/user-network-fs/nfs-ganesha/src/include/log.h

## Purpose

`log.h` is Ganesha's main logging interface. It declares initialization, component log-level control, cleanup/fatal handling, log facilities, DBus integration, backtrace helpers, rate limiting, and the macro family used throughout the server.

## Important APIs, Types, and Functions

Core functions include `init_logging`, `SetNamePgm`, `SetNameHost`, `SetNameFunction`, `SetClientIP`, `DisplayLogComponentLevel`, `SetComponentLogLevel`, `read_log_config`, and `LogMallocFailure`. Facility APIs create, enable, disable, set destination, and set level for named sinks. Global state includes `component_log_level`, `conditional_component_log_level`, `cond_log_match_policy`, `conditional_logging_configured`, and `LogComponents`. Logging macros cover fatal, major, critical, warning, event, info, debug, mid-debug, full-debug, alternate-component logging, opaque/byte formatting, warn-once, and rate-limited event/warn messages.

## Control Flow

Most macros first call `isLevel` to avoid formatting work when disabled, then call `DisplayLogComponentLevel` with source location and function. Conditional logging can override component levels when request context marks a conditional match. Rate-limited macros keep a static `ratelimit_state` per call site and emit missed-message counts.

## State and Persistence Behavior

Logging keeps process-wide component levels, facility state, program/host/client/function names, cleanup callbacks, and per-call-site static rate-limit state. Output persists only through configured sinks such as syslog, file, stderr/stdout, test log, or custom facilities.

## Dependencies and Integration Points

It depends on `log_common.h`, config parsing, display buffers, list helpers, `ip_utils.h`, pthreads, syslog, and optional DBus/unwind. Every subsystem integrates through component macros, making this header a high-blast-radius API.

## Risks and Test Signals

Risks include format-string mismatches, expensive macro arguments evaluated unexpectedly in custom wrappers, conditional logging races, static rate-limit contention, fatal abort behavior in tests, and facility lifetime leaks. Tests should cover level parsing, component threshold behavior, conditional request logging, file/syslog/test destinations, DBus level changes, rate-limit missed counts, backtrace calls, and compile-time printf attribute checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/log_common.h -->
# sources/user-network-fs/nfs-ganesha/src/include/log_common.h

## Purpose

`log_common.h` provides shared logging enums separated from the heavier logging API. It defines severity levels, component identifiers, and conditional logging match policy values used by log configuration, DBus, macros, and subsystem code.

## Important APIs, Types, and Functions

`log_levels_t` ranges from `NIV_NULL` through `NIV_FULL_DEBUG`, with `NB_LOG_LEVEL` as a bound. `log_components_t` enumerates all server components such as FSAL, NFS protocol, exports, file handles, dispatch, MDCACHE, duplicate requests, init, idmapper, NLM, TIRPC, callbacks, state, DBus, QoS, recovery, and RDMA. `cond_log_match_policies_t` defines any/all client/export matching.

## Control Flow

This header has no runtime code, but enum values drive array indexing in `component_log_level` and `LogComponents`, config parsing, and `isLevel` decisions in `log.h`.

## State and Persistence Behavior

No state is stored here. The enum ordering is persistent in the sense that logs, configs, DBus views, and arrays depend on stable component indexes.

## Dependencies and Integration Points

The file has no includes, making it safe for broad inclusion. It is consumed by logging facilities, config parsers, generated diagnostics, and subsystem code that declares its component.

## Risks and Test Signals

Adding or reordering components can break array initializers and external tooling that expects names/order. Tests should verify every enum has a matching `LogComponents` entry, config names map to the intended component, level strings round trip, and `COMPONENT_COUNT` bounds all arrays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/log_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/mdcache.h -->
# sources/user-network-fs/nfs-ganesha/src/include/mdcache.h

## Purpose

`mdcache.h` declares the external control surface for the MDCACHE stackable FSAL. MDCACHE sits above a lower FSAL to provide metadata caching, export stacking, invalidation, and runtime cache policy behavior.

## Important APIs, Types, and Functions

Export lifecycle APIs are `mdcache_fsal_create_export`, `mdcache_fsal_update_export`, and `mdcache_export_uninit`. Package/config APIs are `mdcache_pkginit`, `mdcache_set_param_from_conf`, `mdcache_handle_deleg_transition`, and `init_fds_limit`. The function signatures expose dependencies on FSAL modules, parsed config trees, export handles, Ganesha export objects, config errors, and FSAL upcall vectors.

## Control Flow

During startup or export load, the server initializes the package, parses MDCACHE settings, and creates an MDCACHE export at the top of an FSAL stack. Reloads use `mdcache_fsal_update_export` and delegation transition handling when export policy changes.

## State and Persistence Behavior

The header does not define the cache structures, but it controls process-resident metadata caches and export stack state. Cache entries, file descriptor limits, and delegation modes are runtime state; underlying filesystem persistence remains lower-FSAL-owned.

## Dependencies and Integration Points

It depends on `config.h`, `fsal_types.h`, and `fsal_up.h`. Integration points are FSAL module loading, export manager reloads, upcall invalidation, delegation policy, and startup cleanup on init failure.

## Risks and Test Signals

Risks include cache state surviving failed init, reload transitions leaving stale delegation/cache policy, FD limit misconfiguration, and lower-FSAL operation mismatch. Tests should create/update/unexport MDCACHE-backed exports, inject lower-FSAL errors, verify config parsing bounds, exercise upcall invalidation, and check cleanup after partial initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/mdcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/mount.h -->
# sources/user-network-fs/nfs-ganesha/src/include/mount.h

## Purpose

`mount.h` is the rpcgen-style MOUNT protocol declaration for MOUNT v1/v3 support. It defines mount status codes, export and mount list wire structures, procedure numbers, auth flavor constants, and XDR prototypes.

## Important APIs, Types, and Functions

Key types are `mountstat3`, `fhandle3`, `mnt3_dirpath`, `groupnode`, `exportnode`, `mountbody`, `mountres3_ok`, and `mountres3`. Constants include `MOUNTPROG`, `MOUNT_V1`, `MOUNT_V3`, `MOUNTPROC*_MNT/DUMP/UMNT/UMNTALL/EXPORT`, `MNT_V3_NB_COMMAND`, `MNTPATHLEN`, `MNTNAMLEN`, and MOUNT-specific RPCSEC_GSS flavor IDs. XDR functions encode/decode each wire type.

## Control Flow

MOUNT service descriptors use the procedure numbers to decode requests into these types, call handlers declared in `nfs_proto_functions.h`, and encode mount results or export lists. The `mountres3` union only carries `mountinfo` on `MNT3_OK`.

## State and Persistence Behavior

The header defines wire data only. Runtime mount lists and export lists are built by server code and freed by corresponding protocol free functions.

## Dependencies and Integration Points

It depends on `gsh_refstr.h` for reference-counted export path storage. It is included by `nfs23.h` and `nfs_proto_data.h`, and integrates with export manager, MOUNT dispatch tables, and XDR code.

## Risks and Test Signals

The comment that `fhandle3` is overlaid with `nfs_fh3` is a compatibility risk: layout changes can break MOUNT/NFS handle interchange. Tests should XDR round-trip mount responses, verify auth flavor arrays, validate export path/group list freeing, confirm procedure table bounds using `MNT_V3_NB_COMMAND`, and compile C/C++ flexible-array branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/murmur3.h -->
# sources/user-network-fs/nfs-ganesha/src/include/murmur3.h

## Purpose

`murmur3.h` declares the MurmurHash3 non-cryptographic hash routines used wherever the server needs stable, fast hashing of byte keys such as addresses, handles, or cache keys.

## Important APIs, Types, and Functions

The API consists of `MurmurHash3_x86_32`, `MurmurHash3_x86_128`, and `MurmurHash3_x64_128`. Each takes a key pointer, byte length, 32-bit seed, and caller-provided output buffer.

## Control Flow

Callers choose the width/architecture variant, provide an initialized output object of the expected size, and use the hash result for table indexing or key derivation. The header does not provide endian or size wrappers.

## State and Persistence Behavior

The hash functions are stateless. Persisting their output externally would create compatibility constraints around implementation version and seed choice.

## Dependencies and Integration Points

The only direct dependency is `<stdint.h>`. Implementations integrate with hash tables and cache subsystems. The public-domain notice means this file's licensing differs from most LGPL headers.

## Risks and Test Signals

Murmur3 is not suitable for authentication or adversarial collision resistance. Risks include output-buffer size mistakes, signed `int len` overflow for very large inputs, and platform/endian mismatches if persisted. Tests should compare known Murmur3 vectors for all variants, zero-length keys, unaligned buffers, different seeds, and architecture-specific output sizes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/murmur3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/netgroup_cache.h -->
# sources/user-network-fs/nfs-ganesha/src/include/netgroup_cache.h

## Purpose

`netgroup_cache.h` declares a small cache wrapper around `innetgr()` for export/client access decisions based on netgroups.

## Important APIs, Types, and Functions

The API is `ng_cache_init`, `ng_clear_cache`, and `ng_innetgr(group, host)`. `ng_innetgr` returns whether a host is a member of a netgroup and is expected to cache both lookup results and possibly misses.

## Control Flow

Export/client authorization code initializes the cache, calls `ng_innetgr` during client matching, and clears cached results after configuration or directory-service changes.

## State and Persistence Behavior

State is process-local cache contents derived from system name-service lookups. There is no durable persistence; correctness depends on explicit clear/reinit or TTL behavior in the implementation.

## Dependencies and Integration Points

The header is intentionally minimal. It integrates with export access lists, libc/NSS netgroup support, and configuration reload paths.

## Risks and Test Signals

Risks include stale netgroup membership, host canonicalization mismatches, NSS latency hidden by cache, and missing `<stdbool.h>` if included in isolation. Tests should cover hit/miss caching, cache clearing, host aliases/FQDNs, negative results, NSS failure recovery, and concurrent lookups during reload.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/netgroup_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs23.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs23.h

## Purpose

`nfs23.h` is the mixed rpcgen/hand-maintained wire contract for NFSv2 compatibility and NFSv3 service support. It defines status codes, scalar aliases, file handle layouts, attribute/result structures, every NFSv3 procedure argument/result type, procedure numbers, and XDR routines.

## Important APIs, Types, and Functions

Important constants include NFSv2 limits, `NFS3_FHSIZE`, verifier sizes, `NFS_PROGRAM`, `NFS_V2`, `NFS_V3`, and `NFSPROC3_*`. Core wire types include `nfsstat3`, `ftype3`, `nfs_fh3`, `nfstime3`, `fattr3` aliasing `struct fsal_attrlist`, `post_op_attr`, `pre_op_attr`, `wcc_data`, `sattr3`, `diropargs3`, read/write data structures, directory entry lists with `xdr_uio`, and FSINFO/PATHCONF/COMMIT results. XDR declarations cover every scalar, compound, operation argument/result, and optimized readdir entry encoder/release helper.

## Control Flow

RPC dispatch tables decode requests into these structures, call NFSv3 handlers, then encode status-specific result unions. Many result unions carry weak-cache-consistency data on both success and failure. READ/WRITE carry `io_data`; READDIR/READDIRPLUS can stream via `xdr_uio`.

## State and Persistence Behavior

The header has no runtime state but defines how persistent filesystem attributes, file IDs, handles, cookies, and write verifiers are exposed on the wire. Because `fattr3` aliases FSAL attributes, FSAL attribute lifetime and initialization directly affect encoded protocol data.

## Dependencies and Integration Points

It depends on `gsh_rpc.h`, `extended_types.h`, `mount.h`, and `fsal_types.h`. It is central to `nfs_proto_data.h`, protocol function descriptors, file-handle conversion, NFSACL, MOUNT, metrics, and NFSv3 XDR implementation.

## Risks and Test Signals

Risks include layout coupling with `mount.h` `fhandle3`, manual divergence from rpcgen, flexible-array C/C++ differences, union free mistakes, wrong WCC data on failures, and readdir UIO lifetime bugs. Tests should XDR round-trip every op, fuzz lengths and handles, verify procedure table bounds, exercise READ/WRITE payloads, READDIRPLUS streaming/release, 32/64-bit scalar encoding, and NFSv3 conformance cases for status-specific unions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs23.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs4.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs4.h

## Purpose

`nfs4.h` is a compact wrapper that pulls in local RPC definitions and the generated NFSv4.1 protocol header. It also defines a local maximum NFSv4 domain length fallback.

## Important APIs, Types, and Functions

The header includes `gsh_rpc.h` before `nfsv41.h` so Ganesha's RPC/GSS compatibility definitions are visible. `NFS4_MAX_DOMAIN_LEN` defaults to 512 when not defined elsewhere.

## Control Flow

There is no executable control flow. Compilation units include this header to access NFSv4 scalar, operation, compound, callback, session, and status types from `nfsv41.h`.

## State and Persistence Behavior

No state is defined. The protocol types it exposes describe NFSv4 client/server state such as stateids, sessions, layouts, delegations, and callbacks in other headers and implementation files.

## Dependencies and Integration Points

It integrates every NFSv4 protocol implementation file with generated protocol definitions, local GSS switch behavior, `nfs_proto_data.h`, callback code, file-handle handling, metrics, and ID mapping.

## Risks and Test Signals

Risks are include-order dependency on `gsh_rpc.h`, generated `nfsv41.h` drift, and mismatched domain length assumptions. Tests should compile NFSv4 units under GSS/no-GSS configurations, validate generated XDR compatibility, and exercise owner/group domains near `NFS4_MAX_DOMAIN_LEN`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs4_acls.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs4_acls.h

## Purpose

`nfs4_acls.h` declares the FSAL-side NFSv4 ACL cache/allocation interface. It provides allocation, reference management, cache entry creation, and package initialization for ACL data used by NFSv4 attributes and FSAL objects.

## Important APIs, Types, and Functions

`fsal_acl_status_t` status values distinguish success, generic error, existing entry, internal error, inappropriate key, hash set failure, init-entry failure, and not-found. APIs include `nfs4_acl_alloc`, `nfs4_ace_alloc`, `nfs4_acl_free`, `nfs4_ace_free`, `nfs4_acl_entry_inc_ref`, `nfs4_acl_new_entry`, `nfs4_acl_release_entry`, and `nfs4_acls_init`.

## Control Flow

Callers allocate ACE arrays and ACL objects, normalize them into cached ACL entries with `nfs4_acl_new_entry`, increment references when sharing entries, and release entries when FSAL attributes or cache records are dropped.

## State and Persistence Behavior

ACL data is runtime memory and likely hash-table backed in the implementation. Persistent ACL storage remains in the lower filesystem/FSAL; this layer manages in-memory sharing and lifetime.

## Dependencies and Integration Points

The header depends on `fsal_types.h` for `fsal_acl_t`, `fsal_ace_t`, and `fsal_acl_data_t`. It integrates with NFSv4 attribute encode/decode, FSAL ACL support checks, and `COMPONENT_NFS_V4_ACL` logging.

## Risks and Test Signals

Risks include refcount leaks, duplicate ACL canonicalization mistakes, hash collisions, status codes not translated to protocol errors, and ACE count allocation overflow. Tests should allocate/free empty and large ACLs, deduplicate identical ACL data, verify refcount release, inject hash/allocation failures, and perform NFSv4 GETATTR/SETATTR ACL round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs4_acls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs4_fs_locations.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs4_fs_locations.h

## Purpose

`nfs4_fs_locations.h` declares lifecycle helpers for NFSv4 `fs_locations` referral/replication data stored in FSAL attributes.

## Important APIs, Types, and Functions

The API includes `nfs4_fs_locations_new(fs_root, rootpath, count)`, `nfs4_fs_locations_get_ref`, `nfs4_fs_locations_release`, and `nfs4_fs_locations_free`. The type is `fsal_fs_locations_t` from `fsal_types.h`.

## Control Flow

Export or FSAL code constructs a locations object for a root/path and server-location count, passes references through attributes, and releases references when attributes or exports are destroyed. The free function is the terminal cleanup path.

## State and Persistence Behavior

The structure is process memory with reference counting. The actual referral configuration persists in export/FSAL config or backend metadata, not in this helper.

## Dependencies and Integration Points

It integrates with NFSv4 GETATTR `fs_locations`, referrals, pseudo filesystem exports, and FSAL attribute conversion code.

## Risks and Test Signals

Risks include reference leaks across cached attributes, use-after-free on shared fs_locations, path normalization errors, and count/allocation mismatches. Tests should create zero and multi-location objects, exercise get/release from multiple owners, encode NFSv4 attributes, and reload exports carrying referrals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs4_fs_locations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_convert.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_convert.h

## Purpose

`nfs_convert.h` declares common conversion helpers for protocol statuses, procedure names, auth statuses, byte order, and FSAL-to-NFS error mapping.

## Important APIs, Types, and Functions

String helpers include `nfsstat3_to_str`, `nfsstat4_to_str`, `nfstype3_to_str`, `nfs_req_result_to_str`, `auth_stat2str`, optional `nfsproc3_to_str`, and `nfsop4_to_str`. Numeric helpers are `nfs_htonl64` and `nfs_ntohl64`. Error conversion flows through `nfs4_Errno_verbose`/`nfs4_Errno_status` and optional `nfs3_Errno_verbose`/`nfs3_Errno_status`.

## Control Flow

Protocol handlers receive FSAL statuses, map them into NFSv3 or NFSv4 status codes with function-name context, and use string helpers for logs/metrics. Procedure/opcode stringification supports tracing and diagnostics.

## State and Persistence Behavior

The header has no state. It affects externally visible protocol status values and diagnostics.

## Dependencies and Integration Points

It depends on NFSv3, NFSv4, MOUNT, and FSAL headers. Integration points include all protocol operation handlers, metrics labels, logging, duplicate request results, and auth diagnostics.

## Risks and Test Signals

Incorrect mapping can expose wrong retry semantics or hide access/stale errors. Tests should table-check FSAL error to NFSv3/v4 status conversion, procedure/opcode strings including unknown values, 64-bit byte-order round trips, and logs generated by verbose conversion paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_convert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_core.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_core.h

## Purpose

`nfs_core.h` declares central server runtime state and service-thread interfaces: host identity, callback RPC call structures, health counters, event channels, boot/write verifiers, config blocks, admin thread controls, RPC transport initialization, worker selection, reaper lifecycle, and optional 9P/RDMA hooks.

## Important APIs, Types, and Functions

Important globals include `nfs_host_name`, `cid_server_owner`, `cid_server_scope`, `nfs_health_`, `nfs_ServerBootTime`, `nfs_ServerEpoch`, NFS write verifiers, config paths, netconfig pointers, `admin_shutdown`, and parsed config blocks. `nfs4_compound_t`, `rpc_call_t`, and `rpc_call_func` model outbound callback RPC calls. Core functions initialize/destroy RPC (`nfs_Init_netconfig`, `nfs_Init_svc`, `Clean_RPC`, `nfs_rpc_dispatch_stop`), select event/worker channels, manage admin and reaper threads, encode/decode base64, compare state IDs, and destroy callback channels.

## Control Flow

Startup initializes netconfigs, service sockets, config blocks, admin thread, and reapers. Dispatch uses event channel IDs and worker queues; callback code uses `rpc_call_t` and `rpc_call_channel_t` from `nfs_proto_data.h`. Shutdown stops dispatch, admin, reapers, and RPC channels.

## State and Persistence Behavior

State is process-global and long-lived: boot epoch, verifiers, health counters, config paths, netconfigs, admin state, RPC channels, and reaper state. Boot/write verifier values are externally visible to clients for cache and write stability semantics.

## Dependencies and Integration Points

It depends on SAL data, Ganesha config, optional GSS, optional 9P/RDMA, and error injection. It integrates with initialization, worker dispatch, callback RPC, DBus diagnostics, NFSv4 state/session handling, and cleanup.

## Risks and Test Signals

Risks include global initialization order, shutdown races, callback channel lifetime, incorrect boot epoch/verifier changes, event-channel bounds, and optional-feature compile paths. Tests should cover startup/shutdown cycles, health counter behavior, netid lookup, worker queue selection distribution, reaper wake/shutdown, callback channel destruction, and builds with GSS/9P/RDMA toggles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_creds.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_creds.h

## Purpose

`nfs_creds.h` declares RPC credential extraction, comparison, squashing, and export access checks for NFS requests.

## Important APIs, Types, and Functions

Lifecycle APIs are `init_credentials` and `clean_credentials`. Request handling uses `nfs_req_creds` to populate operation context, `nfs_rpc_req2client_cred` to extract raw credential data, `nfs_compare_clientcred` for equality, `nfs4_export_check_access` for export-level access, `nfs_access_op` for object access checks, and `squash_setattr` to apply anonymous UID/GID squashing to setattr attributes.

## Control Flow

For each RPC, dispatch extracts AUTH_SYS or GSS credentials, maps them into `nfs_client_cred_t` and request context, applies export security/access policy, performs FSAL access checks, and squashes setattr ownership when export options require it.

## State and Persistence Behavior

Credential tables or helper state are initialized process-wide. Per-request credential state lives in request/op context. Squashing modifies attribute lists before they reach the FSAL; persistent effect occurs only if the FSAL setattr succeeds.

## Dependencies and Integration Points

It depends on FSAL types, SAL data, RPC request structures, export options, idmapper/GSS, and protocol handlers.

## Risks and Test Signals

Risks include trusting client-supplied groups when `Manage_Gids` should override, incorrect root/all-anonymous squashing, auth flavor mismatch, GSS principal mapping failure, and stale op context. Tests should cover AUTH_NONE/AUTH_SYS/RPCSEC_GSS, root squash variants, group list handling, export security denial, object access masks, setattr owner squashing, and credential equality edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_creds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_dupreq.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_dupreq.h

## Purpose

`nfs_dupreq.h` defines the duplicate request cache (DRC), which prevents repeated non-idempotent NFS requests from being processed multiple times and enables replay/resume behavior after client retries.

## Important APIs, Types, and Functions

`drc_t` stores DRC type, red-black lookup tree, FIFO completed queue, mutex, partition/cache sizes, refcount, retry window, and TCP recycle metadata. `dupreq_entry_t` stores request identity, hash key, completion flag, refcount, result pointer, request result code, duplicate count, and a queue of up to `DUPREQ_MAX_DUPES` suspended duplicate requests. APIs include `dupreq2_pkginit`, `drc_get_tcp_drc`, `drc_release_tcp_drc`, `nfs_dupreq_start`, `nfs_dupreq_finish`, `nfs_dupreq_delete`, `nfs_dupreq_rele`, `for_each_tcp_drc`, and `get_tcp_drc_recycle_qlen`.

## Control Flow

Dispatch calls `nfs_dupreq_start` before protocol execution. New requests proceed, completed duplicates replay cached results, in-flight duplicates are queued/suspended, and failures can resume queued retries. Completion calls `nfs_dupreq_finish`; retryable drops/auth errors use `nfs_dupreq_delete` to allow reprocessing.

## State and Persistence Behavior

DRC state is in-memory per connection/address and stores completed response data until eviction. It is not durable across restart. Cached responses and suspended requests affect externally visible at-most-once behavior.

## Dependencies and Integration Points

It depends on NFS core/data types, address utilities, pools, red-black trees, queues, and async dispatch. It integrates with RPC worker dispatch, XDR response storage, metrics, and transport lifecycle.

## Risks and Test Signals

Risks include refcount leaks, replaying mutable response buffers after free, hash/checksum collisions, deadlocks between DRC and entry locks, unbounded suspension if duplicate queues fail to drain, and TCP reconnect identity mistakes. Tests should cover concurrent duplicate non-idempotent requests, send-failure retry resume, eviction watermarks, UDP/TCP v3/v4 differences, recycle queue behavior, and request result replay correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_dupreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_exports.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_exports.h

## Purpose

`nfs_exports.h` declares export-list configuration, access-option masks, export-root initialization, export reload/free routines, export security checks, and export logging helpers.

## Important APIs, Types, and Functions

Key types are `global_export_perms`, `exportlist_client_entry`, `client_ha_proxy_protocol_type`, and `log_exports_parms`. The many `EXPORT_OPTION_*` masks describe filesystem ID, caching, max I/O, security labels, squashing, read/write/metadata access, privileged ports, commit, ACL, auth flavors, protocols, transports, delegations, managed gids, and readdirplus. APIs include `get_anonymous_uid`, `get_anonymous_gid`, `export_check_access`, `export_check_security`, `init_export_root`, `nfs_export_get_root_entry`, `release_export`, `ReadExports`, `reread_exports`, `free_export_resources`, `exports_pkginit`, `log_an_export`, and `export_check_options`.

## Control Flow

Startup/reload parses export config into global and per-client permissions, initializes export roots, builds pseudo exports, and validates client security/access on each request. `export_can_be_mounted` filters NFSv4 mountable exports by protocol support, pseudo path, nonzero export ID, and non-root pseudopath.

## State and Persistence Behavior

Exports, client permission lists, locks, root object references, and parsed config are process state. Persistent filesystem data stays in FSALs; export reload can change client-visible access, file handles, and pseudo filesystem topology.

## Dependencies and Integration Points

It depends on config parsing, client/export managers, FSAL types, logging, GSS, and pthread locks. It integrates with NFS credentials, file handle export IDs, MOUNT export lists, pseudo FS, DBus/admin reload, and QoS export classes.

## Risks and Test Signals

Risks include bitmask collisions, incorrect squash/access precedence, reload races under `export_opt_lock`, stale root refs, protocol/transport mismatch, HA proxy policy mistakes, and logging exposure of sensitive paths. Tests should parse all export options, evaluate client-specific permissions, validate auth flavor and privileged-port checks, reload exports under traffic, verify mountability, and ensure root object release/free behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_exports.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_fh.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_fh.h

## Purpose

`nfs_fh.h` defines Ganesha's internal wire file-handle headers for NFSv3 and NFSv4. These structures prefix opaque FSAL handle bytes with version, flags, export/server IDs, and opaque length.

## Important APIs, Types, and Functions

Constants are `GANESHA_FH_VERSION`, `FILE_HANDLE_V4_FLAG_DS`, and `FH_FSAL_BIG_ENDIAN`. `file_handle_v3_t` contains version, flags, network-order export ID, `fs_len`, and flexible `fsopaque`. `file_handle_v4_t` is packed and contains version, flags, an export/server ID union, `fs_len`, and flexible opaque bytes.

## Control Flow

Conversion code in `nfs_file_handle.h` and implementation files packs FSAL handle keys into these structs, writes them into NFS file handle buffers, validates lengths/version/flags on inbound requests, and extracts export/server IDs for routing.

## State and Persistence Behavior

NFS file handles are persistent client-visible tokens. Any layout, version, byte order, or size change can invalidate client handles or break stale-handle detection.

## Dependencies and Integration Points

It depends on portable compiler attributes and is consumed by file-handle conversion, export lookup, pNFS data-server handle checks, NLM/NFSACL logging, and protocol XDR buffers.

## Risks and Test Signals

Risks include packed/alignment differences, flexible array misuse, endian flag handling, export ID overflow, and client compatibility when layout changes. Tests should verify exact offsets/sizes, NFSv3/v4 handle length limits, export ID round trips, DS flag detection, stale/invalid handles, and compatibility with handles generated by prior releases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_fh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_file_handle.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_file_handle.h

## Purpose

`nfs_file_handle.h` provides allocation, validation, FSAL conversion, export-ID extraction, sanity checking, and logging helpers for NFSv3/NFSv4/NLM/NFSACL file handles.

## Important APIs, Types, and Functions

Inline helpers allocate/free fixed-size NFSv3 and NFSv4 buffers, compute actual and padded handle sizes, validate v4 lengths with optional v3-handle compatibility, test empty v4 handles, extract v3/NLM export IDs, and render file handles in debug logs. Public conversion/validation functions include `nfs3_FhandleToCache`, `nfs4_FSALToFhandle`, `nfs3_FSALToFhandle`, `nfs3_Is_Fh_Invalid`, `nfs4_Is_Fh_Invalid`, `nfs4_Is_Fh_DSHandle`, `nfs4_sanity_check_FH`, and `nfs4_sanity_check_saved_FH`.

## Control Flow

Protocol handlers allocate output handles, convert FSAL object handles to wire handles on lookup/create/getfh, validate inbound handles before dispatching operations, resolve handles to cache/export objects, and use sanity checks to enforce required object types and DS-handle permissions.

## State and Persistence Behavior

Allocated NFS handle buffers are request/result memory. The encoded handles persist at clients and refer to export/FSAL state. Logging macros read function descriptor arrays and component levels but do not mutate handle state.

## Dependencies and Integration Points

It depends on logging, display, SAL data, export manager, handle layout, and protocol function descriptors. It integrates with NFSv3, NFSv4 compound state, NLM, NFSACL, pNFS DS handles, and export lookup.

## Risks and Test Signals

Risks include missing allocation checks, incorrect padding compatibility, NULL handle logging, byte-order export ID extraction, invalid DS handle acceptance, and opaque logging buffer truncation. Tests should cover handle allocation/free, invalid length/version/flag combinations, export ID extraction, FSAL round trips, v3-for-v4 compatibility toggles, DS handle restrictions, and debug macro builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_file_handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_init.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_init.h

## Purpose

`nfs_init.h` declares server prerequisite initialization, config loading, package startup, service start, init-completion synchronization, worker RPC validators, and a malloc behavior guard.

## Important APIs, Types, and Functions

`nfs_start_info_t` carries startup flags for default config dump, low-watermark trigger, and capability dropping. `struct nfs_init` provides mutex/condition/init-complete fields. APIs include `nfs_prereq_init_mutexes`, `nfs_init_init`, `nfs_init_cleanup`, `nfs_init_complete`, `nfs_init_wait`, `nfs_init_wait_timeout`, `nfs_prereq_init`, `nfs_prereq_destroy`, `nfs_set_param_from_conf`, `init_server_pkgs`, `nfsv4_init_params`, and `nfs_start`. `nfs_check_malloc` fatally validates `malloc(0)` and `calloc(0,0)` behavior.

## Control Flow

Main/library startup initializes prerequisites, parses config, initializes packages and NFSv4 parameters, starts services, and signals init completion. Other threads can wait for completion. Worker validation functions screen incoming RPCs for NFS, MOUNT, NLM, RQUOTA, NFSACL, and RDMA when compiled.

## State and Persistence Behavior

State includes init synchronization, DBus thread ID, config-derived runtime parameters, and started service packages. Persistent effects are pid/log/config side effects and network listeners.

## Dependencies and Integration Points

It depends on `log.h` and `nfs_core.h`, and integrates with main daemon startup, library embedding, DBus, worker dispatch, optional protocols, and capability management.

## Risks and Test Signals

Risks include init wait deadlocks, timeout misuse, partial-start cleanup gaps, allocator assumptions on unusual libc implementations, config reload divergence, and optional validator compile paths. Tests should run prerequisite init/destroy cycles, wait/timeout behavior, config parse failures, malloc guard on supported platforms, service startup smoke tests, and validator behavior for each enabled RPC program.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_ip_stats.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_ip_stats.h

## Purpose

`nfs_ip_stats.h` declares the IP-address-to-hostname cache used for client-name diagnostics and possibly access/logging paths.

## Important APIs, Types, and Functions

Constants define return values (`IP_NAME_SUCCESS`, `IP_NAME_INSERT_MALLOC_ERROR`, `IP_NAME_NOT_FOUND`) and `IP_NAME_PREALLOC_SIZE`. `nfs_ip_name_t` stores a timestamp followed by a flexible hostname string. APIs are `nfs_ip_name_get`, `nfs_ip_name_add`, and `nfs_ip_name_remove`.

## Control Flow

Callers look up a `sockaddr_t` in the cache, add successful reverse-resolution results with a hostname and size, and remove entries when invalidating or updating names.

## State and Persistence Behavior

State is in-memory hashtable entries with timestamps and variable-size hostnames. No durable persistence is declared; stale entries depend on implementation TTL or explicit removal.

## Dependencies and Integration Points

It depends on `hashtable.h`, network address types from surrounding includes, and hostname limits from `<netdb.h>`. It integrates with `nfs_Init_ip_name`, logging, client manager, and address utilities.

## Risks and Test Signals

Risks include missing direct include for `sockaddr_t` if included standalone, hostname buffer size errors, stale reverse DNS, timestamp overflow/TTL bugs, and allocation failure handling. Tests should add/get/remove IPv4 and IPv6 names, handle oversized hostnames, simulate allocation failure, validate timestamp aging, and stress concurrent lookups if the implementation is shared.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_ip_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_lib.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_lib.h

## Purpose

`nfs_lib.h` exposes a minimal embeddable library interface for starting and reloading the Ganesha server from another process or test harness.

## Important APIs, Types, and Functions

It exports `nfs_config_path`, `nfs_libmain(config_path, log_path, debug_level)`, and `reread_config()`.

## Control Flow

An embedding caller sets or passes a config path/log path/debug level to `nfs_libmain`, which drives the normal prerequisite/config/package/server startup path. Later, `reread_config` triggers configuration reload behavior.

## State and Persistence Behavior

The library interface mutates global daemon state: config path, logging, exports, network services, caches, and worker threads. Reload persists only in process memory and configured runtime side effects.

## Dependencies and Integration Points

It is intentionally lightweight and integrates with `nfs_init.h`, config reload, logging, exports, and service lifecycle implementation.

## Risks and Test Signals

Risks include multiple `nfs_libmain` calls in one process, concurrent reloads, global path lifetime ownership, and shutdown limitations not declared here. Tests should embed-start with valid/invalid configs, verify log path/debug level application, perform reload success/failure, and check behavior when called twice or from multiple threads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_metrics.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_metrics.h

## Purpose

`nfs_metrics.h` declares the monitoring hooks for RPC-level, NFSv3 request, NFSv4 operation/compound, GSS drop, and Ganesha build/info metrics.

## Important APIs, Types, and Functions

`ganesha_info` is a gauge handle. APIs include `nfs_metrics__init`, `register_ganesha_info_metrics`, `nfs_metrics__rpc_received`, `nfs_metrics__rpc_completed`, `nfs_metrics__rpcs_in_flight`, `nfs_metrics__gss_request_dropped`, `nfs_metrics__nfs4_op_completed`, `nfs_metrics__nfs4_compound_completed`, `nfs_metrics__nfs3_request`, and `nfs_metrics__nfs4_request`.

## Control Flow

Metrics initialize during server startup. Dispatch increments received/in-flight/completed counters around each RPC. NFSv4 compound handling records per-op and compound statuses/latency. NFSv3/NFSv4 request functions emit dynamic metrics with proc/op, result/status, export ID, path, and client IP.

## State and Persistence Behavior

Metric handles and counters are process-local and exported to monitoring backends. They do not affect protocol state, but labels can expose paths/client IPs.

## Dependencies and Integration Points

It depends on `dynamic_metrics.h`, NFSv4.1, NFSv3, export IDs, and elapsed-time types. It integrates with dispatcher, protocol operations, QoS monitoring, GSS handling, and server info registration.

## Risks and Test Signals

Risks include high-cardinality path/client labels, negative in-flight gauges, inconsistent success/failure status classification, unregistered metrics, and overhead in hot paths. Tests should initialize metrics once, record NFSv3 and NFSv4 requests, verify label values/status buckets, check in-flight increments/decrements under errors, and confirm info metrics include server scope.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_data.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_data.h

## Purpose

`nfs_proto_data.h` defines the common protocol request/result unions, dispatch descriptor shape, request object, callback channel types, client credential representation, NFSv4 compound execution state, and helper for current object state management.

## Important APIs, Types, and Functions

`nfs_arg_t` and `nfs_res_t` union all NFSv3, NFSv4 compound, MOUNT, NLM, RQUOTA, extended RQUOTA, and NFSACL argument/result types. `nfs_function_desc_t` binds service/free/XDR decode/XDR encode names and dispatch behavior flags (`MAKES_WRITE`, `NEEDS_CRED`, `CAN_BE_DUP`, `SUPPORTS_GSS`, `MAKES_IO`). `nfs_request_t` embeds `svc_req`, lookahead, op context, args, result pointer, function descriptor, and duplicate-request queue linkage. Callback networking uses `rpc_call_channel_t`, netid/nc mappings, and `gsh_addr_t`. `compound_data` tracks current/saved FH/object/DS/stateid, export permissions, request, op arrays, credentials, NFSv4.1 slot/session/replay data, QoS flags, sequence/slot IDs, response sizing, and op-specific resume data. `set_current_entry` manages refcounts and DS release.

## Control Flow

Dispatcher decodes into `nfs_arg_t`, selects an `nfs_function_desc_t`, initializes request/op context, calls the protocol handler, stores `nfs_res_t`, and frees via descriptor free functions. NFSv4 compound processing walks op arrays while mutating `compound_data` current/saved state.

## State and Persistence Behavior

Per-request state is transient but contains references to persistent objects, exports, client IDs, sessions, slots, stateids, and cached compound results. Refcount correctness in `set_current_entry`/`set_saved_entry` controls object lifetime.

## Dependencies and Integration Points

It depends on FSAL API, RQUOTA, NFSv3/v4, NLM, NFSACL, SAL data, RPC channels, pNFS DS handles, QoS, and TIRPC netid mappings. This is a central include for dispatch, duplicate request cache, callbacks, and protocol handlers.

## Risks and Test Signals

Risks include union misuse/free omissions, dispatch flag mismatches, stale object refs, saved/current DS lifetime mistakes, NFSv4.1 replay slot cache leaks, response-size accounting errors, and credential lifetime bugs. Tests should exercise each protocol descriptor, compound current/saved FH transitions, refcounting under failure, session replay, async resume data, response-size limits, and duplicate request integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_functions.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_functions.h

## Purpose

`nfs_proto_functions.h` declares all protocol service handlers, NFSv4 operation handlers, result free/copy helpers, async completion/resume hooks, pseudo filesystem operations, and NFSv4.1 slot cleanup.

## Important APIs, Types, and Functions

The header exports protocol descriptor arrays for enabled NFSv3, NFSv4, MOUNT, NLM, RQUOTA, and NFSACL. It declares service handlers for MOUNT, NLM, RQUOTA, NFSACL, NFS NULL, NFSv3 procedures, and `nfs4_Compound`. NFSv4 op handlers cover core v4.0, v4.1 sessions/pNFS, v4.2 operations, and v4.3 xattrs, with matching `*_Free` and selected `*_CopyRes` helpers. Additional APIs include `nfs_rpc_complete_async_request`, `drc_resume`, `compound_data_Free`, `get_nfs4_opcodes`, `xdr_COMPOUND4res_extended`, pseudo FS mount/unmount/prune helpers, and inline `release_slot`.

## Control Flow

Dispatch tables call protocol handlers through `nfs_function_desc_t`. NFSv4 compound dispatch maps opcodes to `nfs4_op_*`, handles async read/write/read-plus resume, frees each op result, and caches/copies selected results for NFSv4.1 replay. Pseudo FS helpers maintain export visibility during export load/reload.

## State and Persistence Behavior

Handlers mutate filesystem/export/session/state state through FSAL and SAL layers. Free functions own cleanup of result unions and cached compound references; `release_slot` releases a cached compound result and clears the slot pointer.

## Dependencies and Integration Points

It depends on NFS core, SAL data, and protocol data. It integrates with every protocol implementation file, duplicate request cache, async I/O, pseudo filesystem, NFSv4 session replay, pNFS, xattr support, and optional protocol builds.

## Risks and Test Signals

Risks include descriptor arrays not matching procedure counts, missing free routines for new ops, duplicated declarations hiding mismatches, async completion races, pseudo FS prune mistakes, and stale slot cached results. Tests should validate dispatch tables against constants, run every protocol op through decode/handler/free, exercise async read/write resume, NFSv4.1 replay/copy, pseudo export mount/unmount reload, and memory leak checks for all free paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_functions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_tools.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_tools.h

## Purpose

`nfs_proto_tools.h` declares protocol utility helpers for NFSv3 WCC/attributes, NFSv4 attribute bitmap encoding/decoding, UTF-8/path validation, FSAL attribute conversion, response-size accounting, pNFS layout return, mounted-on fileid, quotas, and optional NFSACL conversion.

## Important APIs, Types, and Functions

`fattr4_dent_t` and `fattr4tab` describe each NFSv4 attribute's name, support/encode flags, size, access, FSAL masks, and encode/decode/compare callbacks. Inline bitmap helpers scan/set/clear/check attributes and special WRONGSEC/rdattr_error cases. Utility APIs include NFSv3 WCC setters, `nfs_RetryableError`, `nfs3_Sattr_To_FSAL_attr`, `nfs4_Fattr_Free`, `file_To_Fattr`, access/support/compare checks, FSAL/NFS attr conversion, error fattr filling, readdir entry encoding, unsupported-attr removal, path UTF-8 scanning, pathname alloc/free, response room checks, mounted-on fileid, and optional POSIX ACL encode/decode.

## Control Flow

NFSv3 handlers build pre/post/WCC attributes around FSAL operations. NFSv4 GETATTR/SETATTR/VERIFY/NVERIFY and READDIR use bitmaps to decide which attributes to encode/decode, convert FSAL attributes through `fattr4tab`, enforce UTF-8/path rules, and guard response size.

## State and Persistence Behavior

Most helpers are stateless conversions. They may read config flags such as delay-error dropping and UTF-8 enforcement, and they mutate FSAL attrlists or response buffers. Persistent filesystem state changes only when converted setattr/ACL data reaches FSAL operations.

## Dependencies and Integration Points

It depends on hashtables, logging, file handles, SAL data, FSAL APIs, optional POSIX ACLs, and NFS parameters. It is central to NFSv3/v4 protocol handlers, readdir encoding, ACL support, quotas, and pNFS layout handling.

## Risks and Test Signals

Risks include bitmap off-by-one errors beyond three words, unsupported attribute leakage, wrong attr access classification, UTF-8 validation bypass, response-size undercount, WCC values from stale attrs, and ACL conversion loss. Tests should cover bitmap iteration, all `fattr4tab` entries, setattr conversion, GETATTR errors, readdir encoded entries, path filter flags, response room exhaustion, retryable FSAL errors, and POSIX ACL round trips when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_proto_tools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_qos.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_qos.h

## Purpose

`nfs_qos.h` declares optional QoS support for NFS I/O throttling. When `ENABLE_QOS` is set, it defines bandwidth, IOPS, and token accounting for per-export, per-client, or per-export-per-client classes.

## Important APIs, Types, and Functions

Flags mark QoS I/O, read bypass, compound I/O, and IOPS accounting. Defaults and bounds cover bandwidth, IOPS, tokens, and refresh intervals. Types include `qos_status_t`, `qos_class_type_t`, `qos_op_type_t`, `qos_op_cb_arg`, `timer_entry_t`, `qos_client_entry_t`, `qos_bucket_t`, `qos_block_config_t`, and `qos_class_t`. APIs include class insertion/free/copy, client lookup, BW/IOPS drainers, read/write/compound callbacks, `qos_process`, `qos_process_iops`, `qos_init`, and `shutdown_qos`.

## Control Flow

NFSv4 read/write/compound processing calls QoS functions with size, op type, compound data, and DS flag. QoS buckets account bandwidth/IOPS/tokens, enqueue timer entries when limits are exceeded, possibly disable transport receive for token-exhausted clients, and resume callbacks when timers expire or credits refresh.

## State and Persistence Behavior

QoS state is in memory: global config, export/client classes, per-bucket counters, wait queues, token renewal timestamps, locks, metrics handles, and suspended transport state. It does not persist across restart, but it directly delays client I/O.

## Dependencies and Integration Points

It depends on Ganesha lists, pthreads, compound data, exports/clients, SVCXPRT, config blocks, and optional metrics. Integration points are NFSv4 read/write, export/client managers, config reload, DBus QoS manager, and monitoring.

## Risks and Test Signals

Risks include deadlocks around bucket/class locks, failed wakeups for queued I/O, incorrect combined read/write accounting, transport receive left disabled, token refresh overflow, config bounds errors, and high-cardinality metrics. Tests should enable each QoS mode, throttle read/write/compound IOPS, verify callbacks resume, reload config, exhaust tokens, drain queues on shutdown, and compare metrics/counters with observed throughput.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_qosmgr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_qosmgr.h

## Purpose

`nfs_qosmgr.h` declares optional DBus management hooks for QoS when `ENABLE_QOS` is compiled.

## Important APIs, Types, and Functions

It exports `g_qos_config_lock`, `dbus_qosmgr_init`, `get_export_client_count`, and `lookup_client(DBusMessageIter *args, char **errormsg)`.

## Control Flow

DBus initialization registers QoS manager methods. DBus handlers lock QoS config, parse client arguments, find client objects, inspect export/client counts, and return errors through `errormsg` when lookup fails.

## State and Persistence Behavior

The header exposes shared QoS config lock and reads live QoS/export/client state. Changes are runtime-only unless implementation writes back to config elsewhere.

## Dependencies and Integration Points

It depends on `gsh_dbus.h`, QoS class definitions from `nfs_qos.h`, client manager types, and DBus message iterators. It integrates with admin/DBus thread initialization and QoS runtime classes.

## Risks and Test Signals

Risks include DBus/QoS lock ordering, stale client pointers, malformed DBus argument handling, and exposing inconsistent counts during reload. Tests should initialize DBus QoS manager, lookup valid/invalid clients, query export-client counts under concurrent client changes, and run with QoS disabled to ensure guarded declarations are not referenced.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_qosmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_rpc_callback.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_rpc_callback.h

## Purpose

`nfs_rpc_callback.h` declares the NFSv4 callback RPC dispatch API for v4.0 callback channels and v4.1 backchannel/session callbacks.

## Important APIs, Types, and Functions

`nfs4_cb_tag_t` models callback tags. `cb_compound_init_v4`, `cb_compound_add_op`, and `cb_compound_free` build callback compound requests. `nfs_cb_call_states` tracks dispatch/finished/aborted call states. Allocation helpers create/free `rpc_call_t`, callback argop/resop arrays, and channel down flags on `nfs_client_id_t`. Channel and call APIs include `nfs_rpc_get_chan`, package init/shutdown, optional GSS status, `nfs_rpc_create_chan_v40`, `nfs_rpc_create_chan_v41`, `nfs_rpc_call`, `nfs_rpc_cb_single`, `nfs41_release_single`, and `nfs_test_cb_chan`.

## Control Flow

State/delegation/session code builds callback compounds, obtains or creates a callback channel, submits an RPC call with optional completion hook, and updates channel-down state or releases v4.1 single-call resources after completion.

## State and Persistence Behavior

Callback channels are live process state tied to client IDs or sessions, with CLIENT/AUTH/GSS objects declared in `nfs_proto_data.h`. Channel-down flags affect future callback attempts and delegation behavior.

## Dependencies and Integration Points

It depends on config, logging, NFS core, NFSv4 generated callback types, client ID/session state, GSS, and RPC channel destruction. It integrates with delegations, recalls, layouts, session backchannels, and callback simulator builds.

## Risks and Test Signals

Risks include callback compound allocation leaks, channel lifetime races with client/session destruction, stale channel-down state, GSS enable mismatch, and completion hook use-after-free. Tests should create v4.0 and v4.1 channels, send/test callbacks, simulate client channel failure/recovery, verify completion callbacks and resource release, and run delegation recall flows under reconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_rpc_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_rpc_callback_simulator.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfs_rpc_callback_simulator.h

## Purpose

`nfs_rpc_callback_simulator.h` declares lifecycle hooks for a callback simulator package intended to exercise or emulate NFSv4 callback dispatch behavior.

## Important APIs, Types, and Functions

The API is `nfs_rpc_cbsim_pkginit` and `nfs_rpc_cbsim_pkgshutdown`. The comments describe an intended small set of nonblocking backchannel service threads.

## Control Flow

Tests or optional simulator startup initialize the package before callback use and shut it down during cleanup. The implementation likely owns simulator threads and nonblocking socket state.

## State and Persistence Behavior

Any simulator state is process-local and should be removed on shutdown. It does not persist protocol state except through interactions with callback test clients.

## Dependencies and Integration Points

It depends on config and logging. It complements `nfs_rpc_callback.h` and is useful for callback/backchannel tests without requiring a full client implementation.

## Risks and Test Signals

Risks include simulator threads not stopping, mismatch with real callback semantics, and bitrot as v4.1 support evolves. Tests should init/shutdown repeatedly, run callback dispatch through simulator channels, verify nonblocking cleanup, and compare simulator behavior with real callback tests where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfs_rpc_callback_simulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfsacl.h -->
# sources/user-network-fs/nfs-ganesha/src/include/nfsacl.h

## Purpose

`nfsacl.h` defines the NFSACL v3 auxiliary RPC protocol data structures for POSIX ACL get/set support over NFSv3. It is a version-controlled mix of rpcgen-generated and hand-edited text.

## Important APIs, Types, and Functions

Mask constants include `NFS_ACL`, `NFS_ACLCNT`, `NFS_DFACL`, `NFS_DFACLCNT`, `NFS_ACL_MASK`, and `NFS_DFACL_MASK`. Types include `attr3`, `posix_acl_entry`, flexible `posix_acl`, `getaclargs`, `getaclresok`, `getaclres`, `setaclargs`, `setaclresok`, and `setaclres`. Program constants are `NFSACLPROG`, `NFSACL_V3`, `NFSACLPROC_NULL`, `NFSACLPROC_GETACL`, and `NFSACLPROC_SETACL`. XDR declarations cover every type.

## Control Flow

NFSACL dispatch decodes `getaclargs` or `setaclargs`, converts ACL wire entries to/from FSAL/POSIX ACL representations via protocol tools, executes ACL operations, and returns status plus optional attributes and access/default ACL arrays.

## State and Persistence Behavior

The header defines wire objects only. Persistent ACL state is stored by the underlying filesystem/FSAL after SETACL; GETACL returns snapshots of that state. Variable-size ACL arrays require careful allocation/free.

## Dependencies and Integration Points

It depends on `<rpc/rpc.h>` and on NFSv3 types from `nfs23.h` being available in including contexts. It integrates with `nfs_proto_data.h`, NFSACL service handlers/free functions, POSIX ACL conversion in `nfs_proto_tools.h`, export ACL options, and FSAL ACL operations.

## Risks and Test Signals

Risks include flexible array allocation mistakes, access/default ACL count mismatches, mask interpretation errors, status-to-attribute union misuse, missing include order for NFSv3 types, and memory leaks in XDR free paths. Tests should XDR round-trip GETACL/SETACL, encode/decode access and default ACLs, reject malformed counts/masks, verify directory vs non-directory default ACL behavior, and run NFSv3 ACL conformance against ACL-capable and ACL-disabled exports.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/nfsacl.h -->
