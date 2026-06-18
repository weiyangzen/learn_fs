# subset-b-009716 research

Grouped research for NFS-Ganesha include headers under `sources/user-network-fs/nfs-ganesha/src/include`. Each file section is bounded for reconciliation into the mapped source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_api.h -->
# sources/user-network-fs/nfs-ganesha/src/include/fsal_api.h

Purpose: This is the central object-oriented FSAL contract. It defines API versioning, request operation context, module/export/object/data-server operation vectors, and public base structs that every FSAL and stacked FSAL must honor.

Important APIs/types/functions: `FSAL_MAJOR_VERSION`/`FSAL_MINOR_VERSION` gate out-of-tree module compatibility. `struct req_op_context` is the thread-local operation envelope for credentials, client, export, paths, pNFS DS, protocol data, and conditional logging. `struct fsal_ops`, `struct export_ops`, `struct fsal_obj_ops`, and `struct fsal_pnfs_ds_ops` are the main vtables. `struct fsal_module`, `struct fsal_export`, `struct fsal_obj_handle`, `struct fsal_pnfs_ds`, and `struct fsal_ds_handle` are public bases embedded by private FSAL implementations. Inline helpers handle module and export-root reference counts.

Control flow: The core loads a module, calls module config/create-export hooks, then dispatches protocol operations through export and object vectors. Lookup/open/create paths instantiate `fsal_obj_handle` values with references already held. I/O uses `read2`/`write2` callbacks and `struct fsal_io_arg`; pNFS MDS/DS calls flow through layout and DS handle vectors.

State and persistence: The header encodes long-lived module/export/object parentage, refcounts, export stacking, FSAL lists, per-operation `op_ctx`, file handle conversion invariants, pNFS segment bookkeeping, and layout return/commit state. Persistent NFS identity depends on stable wire-to-host-to-key and handle-to-key behavior.

Dependencies and integration points: It includes FSAL types, pNFS, config parsing, SAL shared state, AVL trees, atomics, refcounted strings, client/export managers, and upcalls. Integrates with MDCACHE, NFSv3/v4/9P paths, pNFS, DBus stats, export reload, delegation transitions, and state management.

Risks: ABI changes require version bumps. Mismatched handle conversion breaks cache identity. Incorrect reference ownership can unload modules, exports, or objects too early. Attribute masks and ACL ownership are easy leak points. Async callbacks must preserve request state and not run forbidden backend operations in callback context.

Test signals: Exercise export load/update/unexport, root lookup, handle round trips, open/create variants, read/write callback paths, lock/delegation/share behavior, pNFS layoutget/return/commit, DS read/write/commit, reference-count shutdown, and stacked FSAL pass-through.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_convert.h -->
# sources/user-network-fs/nfs-ganesha/src/include/fsal_convert.h

Purpose: This header defines conversion helpers between POSIX/kernel filesystem representations and FSAL-neutral types.

Important APIs/types/functions: `posix2fsal_error` and inline `posix2fsal_status` convert `errno` to `fsal_status_t`. `fsal2posix_openflags`, `fsal2posix_testperm`, `posix2fsal_attributes`, and `posix2fsal_attributes_all` bridge flags, permission checks, and `struct stat`. Inline `fsal2unix_mode`, `unix2fsal_mode`, and `posix2fsal_time` mask mode bits and build `timespec`. `posix2fsal_type`, `posix2fsal_fsid`, `posix2fsal_devt`, and `object_file_type_to_str` cover object type, fsid/device encoding, and diagnostics.

Control flow: VFS-like FSALs call these helpers after syscalls or before issuing POSIX operations. Attribute conversion fills an `fsal_attrlist` and sets masks that upper FSAL/cache/protocol layers consume.

State and persistence: It does not own persistent state, but its mapping decisions affect persistent NFS file attributes, fsids, device ids, and status propagation.

Dependencies and integration points: Depends on `sys/stat.h`, `unistd.h`, and `fsal_types.h`. It is used by POSIX-backed FSALs, object creation, getattr, permission checks, and error translation into NFS replies.

Risks: Incomplete errno mapping can leak wrong NFS status. Mode conversion intentionally strips file type bits via `S_IALLUGO`; callers must not expect it to preserve `S_IFMT`. Attribute masks must match filled fields or cache/protocol code may trust uninitialized data.

Test signals: Validate errno-to-FSAL mapping, open flag conversion, permission mask conversion, all POSIX file type mappings, device/fsid round trips, and stat-to-attr conversion for regular files, directories, symlinks, and special nodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_convert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_handle_syscalls.h -->
# sources/user-network-fs/nfs-ganesha/src/include/fsal_handle_syscalls.h

Purpose: This header abstracts platform-specific by-handle filesystem syscalls for VFS-style FSAL handle creation/opening.

Important APIs/types/functions: `VFS_HANDLE_LEN` fixes the maximum opaque VFS handle payload at 59 bytes. `vfs_file_handle_t` stores a one-byte `handle_len` plus handle bytes; the length byte is not sent on the wire. `vfs_handle_invalid` rejects oversized `gsh_buffdesc` values. `vfs_alloc_handle` allocates and initializes a stack handle via `alloca`; `vfs_malloc_handle` allocates the same shape with `gsh_calloc`.

Control flow: Callers allocate a handle wrapper, platform headers supply Linux or FreeBSD syscall definitions, and FSAL code uses those functions to convert between file handles and opened files. Compile-time platform selection includes `os/linux/fsal_handle_syscalls.h` or `os/freebsd/fsal_handle_syscalls.h`.

State and persistence: The header itself owns no durable state. The serialized handle bytes are persistent identity material for VFS file handles and must remain within `VFS_HANDLE_LEN`.

Dependencies and integration points: It depends on `config.h`, POSIX headers, `gsh_types.h`, and platform syscall headers. It is intentionally top-level even though the TODO says it belongs under FSAL_VFS.

Risks: Oversized handles cause invalidation; too-small limits can break filesystems with larger native handles. Stack allocation via `alloca` must stay scoped. Compile guards fail builds on unsupported or very old platforms without `AT_FDCWD`.

Test signals: Build on Linux/FreeBSD, verify unsupported-platform failure, test valid and oversized descriptors, ensure zero initialization and `handle_len` setup, and run VFS handle open-by-handle regression tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_handle_syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_pnfs.h -->
# sources/user-network-fs/nfs-ganesha/src/include/fsal_pnfs.h

Purpose: This header defines FSAL-level pNFS structures for metadata server layout handling, device IDs, data server handles, and layout return/commit bookkeeping.

Important APIs/types/functions: `struct pnfs_segment` models layout IO mode, offset, and length. `enum fsal_id` assigns FSAL IDs embedded in pNFS `deviceid4`. `struct pnfs_deviceid` is the host-order FSAL view of a deviceid. `struct fsal_layoutget_arg`/`res`, `struct fsal_layoutreturn_arg`, `struct fsal_layoutcommit_arg`/`res`, and `struct fsal_getdevicelist_res` are the argument contracts consumed by `fsal_api.h` layout vectors.

Control flow: An MDS advertises support, answers `GETDEVICEINFO`/`GETDEVICELIST`, grants layouts via `layoutget`, receives returns through `layoutreturn`, and accepts client write aggregation through `layoutcommit`. FSAL-provided segment data is saved by the state layer and passed back on return/commit.

State and persistence: Layout state includes segment ranges, per-segment FSAL data, layoutget context, return-on-close flags, recall cookies, cookie verifiers, and client-visible device IDs. The header warns that allocated segment/context data must be freed at disposal or completion boundaries.

Dependencies and integration points: Includes `nfs4.h` and feeds the FSAL object/export operation vectors, NFSv4.1 layout operations, pNFS DS read/write/commit paths, and upcall layout recall.

Risks: Device IDs are host-order opaque data, so cross-platform assumptions are risky. Forgetting to set `last_segment` or free `fsal_seg_data`/contexts leaks or loops. Multiple-segment support is possible but production clients often expect a single segment.

Test signals: Test layout type advertisement, layoutget single and multi-segment paths, getdevicelist cookies/verifiers, layoutreturn circumstances including revoke/reclaim/shutdown, layoutcommit size/time changes, and recall-cookie satisfaction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_pnfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_types.h -->
# sources/user-network-fs/nfs-ganesha/src/include/fsal_types.h

Purpose: This is the shared FSAL type vocabulary for object kinds, credentials, export permissions, ACLs, attributes, status codes, filesystem capabilities, quotas, locking, open/share state, and generic FD coordination.

Important APIs/types/functions: `object_file_type_t`, `struct user_cred`, `struct export_perms`, `fsal_fsid_t`, `fsal_dev_t`, ACL structs/macros, `attrmask_t` and `struct fsal_attrlist` define metadata surfaces. `fsal_accessflags_t`, `fsal_openflags_t`, create/readdir modes, `fsal_staticfsinfo_t`, `fsal_status_t`, `fsal_dynamicfsinfo_t`, quota, lock/share/delegation types, `struct fsal_fd`, `init_fsal_fd`, `destroy_fsal_fd`, and `struct fsal_share` define operational state.

Control flow: FSAL methods receive requested masks, fill valid masks, return `fsal_status_t`, and use capability booleans to drive protocol behavior. FD helpers initialize mutex/condition-backed descriptors used by FSAL FD management and LRU reclaim.

State and persistence: Attribute structs carry NFS-visible metadata, ACL references have locks/refcounts, fsids/fileids form stable identity, static fsinfo describes per-export durable capability policy, and FD/share structures track active open/share state.

Dependencies and integration points: Depends on `nfsv41.h`, pthread primitives, XDR-related constants, op context through `FSAL_FD_INIT`, and list utilities. It is included by most FSAL and protocol bridge headers.

Risks: Mask misuse is the main hazard: setting bits without valid data or omitting supported masks changes client-visible behavior. ACL reference locking, FD condition variables, and share counters must remain balanced. `FSAL_MAXIOSIZE` ties IO limits to RPC/XDR caps.

Test signals: Validate attribute masks, ACL inheritance/evaluation, status mapping, open/share deny matrix, fd init/destroy for temp and non-temp descriptors, static fsinfo feature queries, quota/lock/delegation conversions, and NFSv3/v4 metadata encoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_up.h -->
# sources/user-network-fs/nfs-ganesha/src/include/fsal_up.h

Purpose: This header defines FSAL upcalls used by backing filesystems to invalidate or update cache state, grant/announce locks, recall layouts/delegations, notify device changes, and release cache entries.

Important APIs/types/functions: Update flags such as `fsal_up_update_filesize_inc` and invalidation flags such as `FSAL_UP_INVALIDATE_ATTRS`, `CONTENT`, `DIR_CHUNKS`, `CLOSE`, and `PARENT` control cache changes. `struct layoutrecall_spec` scopes layout recalls. `struct fsal_up_vector` stores the upcall vtable plus readiness synchronization. Async wrappers like `up_async_invalidate`, `up_async_update`, `up_async_layoutrecall`, and `up_async_delegrecall` post work to a `fridgethr`.

Control flow: FSALs normally call methods through their export's `up_ops`. Calls are synchronous and intended for notification threads; FSAL method contexts should use delayed execution or async wrappers to avoid illegal re-entry such as recalling layouts from inside layoutget.

State and persistence: Upcall state is mostly transient, but it mutates persistent cache/state-layer views of file attributes, ACLs, layouts, locks, delegations, device IDs, and object liveness. The vector's `up_ready`/`up_cancel` condition protects startup/shutdown readiness.

Dependencies and integration points: Includes `gsh_status.h`, `fsal_api.h`, and `sal_data.h`; integrates FSAL implementations with MDCACHE, state management, pNFS, delegation recall, and async worker infrastructure.

Risks: Calling synchronous upcalls from the wrong stack can deadlock or violate layout/state ordering. Update flags must not modify immutable identity fields. Invalidating too little leaves stale cache; invalidating too much hurts performance or closes active files unexpectedly.

Test signals: Exercise attribute-only and content invalidations, parent invalidation, update increment semantics, lock grant/availability callbacks, delegation recall, layout recall with client specs, notify-device events, async wrapper callbacks, and ready/cancel synchronization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/fsal_up.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_config.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_config.h

Purpose: This header defines the global NFS-Ganesha configuration model and defaults for core protocol service, RPC/TIRPC, duplicate request caches, NFSv4, recovery, directory services, metrics, and optional protocol features.

Important APIs/types/functions: `enum protos` enumerates enabled RPC programs by compile-time feature. Defaults cover NFS/RQUOTA/RDMA ports, worker counts, DRC sizing, buffers, monitoring, NFSv4 lease/grace, and identity mapping. `nfs_core_parameter_t`, `nfs_version4_parameter_t`, `directory_services_param_t`, and `nfs_parameter_t` make up global `nfs_param`. Macros `NFS_pcp`, `NFS_options`, and `NFS_program` provide shorthand access.

Control flow: Startup populates `nfs_param` defaults, config parsing updates fields, and runtime subsystems read the global settings to bind sockets, size caches, select protocols, enable stats, configure idmapping, recovery, pNFS, RDMA, DBus heartbeat, and memory trimming.

State and persistence: The structs hold daemon-wide persistent runtime configuration. NFSv4 lease/grace/recovery fields and recovery backend settings directly affect client state recovery after restart or failover.

Dependencies and integration points: Includes `nfs4.h`, `gsh_recovery.h`, and password/name service wrappers. Conditional fields integrate with NLM, RQUOTA, NFSACL, RDMA, GSSAPI, and monitoring builds.

Risks: Compile-time conditionals change struct layout. Defaults can materially affect correctness, especially DRC sizing/checksums, grace behavior, idmapping, delegation/pNFS flags, and connection management. Global mutable config requires careful reload/update handling.

Test signals: Validate default initialization, config parser coverage for each stanza, reload behavior, protocol enable masks, DRC bounds, NFSv4 grace/lease recovery, idmapping cache limits, RDMA version masks, DBus heartbeat prefixing, and metrics toggles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_dbus.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_dbus.h

Purpose: This header defines Ganesha's low-level DBus service provider interface, introspection model, heartbeat, broadcast queue, and path registration helpers.

Important APIs/types/functions: Constants define the base object path and admin interface. Argument helper macros define common DBus signatures and terminators. `dbus_prop_access_t`, `struct gsh_dbus_prop`, `gsh_dbus_arg`, `gsh_dbus_method`, `gsh_dbus_signal`, and `gsh_dbus_interface` model introspection and dispatch. Broadcast support uses `dbus_bcast_callback` and `struct dbus_bcast_item`. Public functions include `add_dbus_broadcast`, `del_dbus_broadcast`, `init_heartbeat`, `gsh_dbus_pkginit`, `gsh_dbus_pkgshutdown`, `gsh_dbus_thread`, `gsh_dbus_register_path`, and `gsh_dbus_broadcast`.

Control flow: Packages register object paths with interface arrays. A DBus thread runs the loop, dispatches method callbacks, emits broadcasts, and sends periodic heartbeat when configured.

State and persistence: Runtime DBus state includes registered paths, scheduled broadcast items with next time/count/interval, and heartbeat health. There is no disk persistence in this header.

Dependencies and integration points: Depends on libdbus, logging, optional 9P types, and list utilities. Exposes admin/status/stats integration to external controllers and monitoring.

Risks: Variable argument broadcasting depends on matching DBus type signatures. Interface arrays are NULL terminated; missing terminators can overrun. Callback code must be thread-safe relative to the shared DBus loop.

Test signals: Register a path with properties/methods/signals, verify introspection, heartbeat, status replies, broadcast count/interval behavior, shutdown cleanup, and optional 9P argument parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_dbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_intrinsic.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_intrinsic.h

Purpose: This small portability header centralizes compiler branch prediction hints and cache-line padding constants.

Important APIs/types/functions: `likely(x)` and `unlikely(x)` expand to GCC/GLIBC `__builtin_expect` when available and to plain expressions otherwise. `GSH_CACHE_LINE_SIZE` is 128 on PPC64 and 64 elsewhere. `GSH_CACHE_PAD(_n)` declares a named padding byte array.

Control flow: Runtime code uses the macros in hot paths to hint common branches and to separate frequently written fields across cache lines.

State and persistence: No state is stored. Padding affects in-memory struct layout and false-sharing behavior.

Dependencies and integration points: It relies only on preprocessor/compiler definitions and is safe as a low-level include for infrastructure headers.

Risks: Padding changes ABI/layout when embedded in public structs. Branch hints can make code less readable and, if overused or wrong, can modestly hurt performance. Non-GCC compilers fall back to no-op behavior.

Test signals: Compile on GLIBC and non-GLIBC targets, inspect struct sizes where padding is used, and benchmark hot paths only if changing likely/unlikely placement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_intrinsic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_list.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_list.h

Purpose: This header provides Ganesha's intrusive doubly linked list primitives and `container_of` helper.

Important APIs/types/functions: `struct glist_head` is the embedded node/head. Initialization macros/functions include `GLIST_HEAD_INIT`, `GLIST_HEAD`, and `glist_init`. Mutation helpers include `glist_add`, `glist_add_tail`, `glist_del`, `glist_move_tail`, `glist_add_list_tail`, `glist_splice_tail`, `glist_swap_lists`, `glist_split`, and `glist_insert_sorted`. Iteration and container helpers include `glist_for_each`, safe variants, `glist_first_entry`, `glist_last_entry`, `glist_entry`, next/previous entry macros, and `glist_length`.

Control flow: Callers embed `glist_head` in owner structs, initialize heads to self-pointing empty lists, splice/move/delete nodes, and recover owners through `container_of`.

State and persistence: List state is purely in-memory. Deleted nodes are poisoned with NULL next/prev so `glist_null` can identify unlinked nodes.

Dependencies and integration points: Used throughout FSAL module/export/object lists, DBus broadcast queues, hash/FD LRU users, and many daemon collections. No locking is provided; callers must synchronize.

Risks: Adding an already-linked node corrupts lists. Using list operations without caller-held locks races. `glist_split` assumes a non-empty source and empty destination. `container_of` relies on GNU `typeof`.

Test signals: Unit-test empty/non-empty insert/delete/splice/swap/split cases, safe deletion during iteration, sorted insertion ordering, node poisoning, and list length after each mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_lttng/gsh_lttng.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_lttng/gsh_lttng.h

Purpose: This header wraps generated LTTng tracepoint macros with Ganesha context fields and no-op fallbacks when tracing is disabled.

Important APIs/types/functions: Under `USE_LTTNG`, `GSH_AUTO_TRACEPOINT` and `GSH_UNIQUE_AUTO_TRACEPOINT` add `__FILE__`, line, function placeholder, `nfs_param.core_param.unique_server_id`, and thread-local `op_ctx->op_id` to trace messages before calling generated macros. Without LTTng, `gsh_empty_function` consumes variadic arguments to avoid unused warnings. Helpers format sessions, verifiers, truncated byte/string/int arrays, and change-info fields.

Control flow: Instrumented code calls the GSH macros. Builds with LTTng emit provider events; builds without LTTng compile argument expressions but perform no tracing.

State and persistence: Trace output is external runtime telemetry. The only read state is global `nfs_param` and thread-local `op_ctx`.

Dependencies and integration points: Depends on `gsh_config.h`, generated `lttng_generator.h`, LTTng tracepoint headers, and NFSv4 constants. Used by general Ganesha trace instrumentation and by transport wrappers.

Risks: Trace arguments may still be evaluated in no-op mode, so expensive or side-effecting expressions are risky. Missing `op_ctx` is handled with op_id zero. Format strings must match generated tracepoint expectations.

Test signals: Build with and without `USE_LTTNG`, verify no unused warnings, emit a trace with and without `op_ctx`, check server/op identifiers, and validate truncated array macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_lttng/gsh_lttng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_recovery.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_recovery.h

Purpose: This header declares the recovery backend selector used by NFSv4 recovery configuration.

Important APIs/types/functions: `enum recovery_backend` lists filesystem, newer filesystem, RADOS key-value, newer RADOS, RADOS cluster, and disabled recovery modes. `RECOVERY_BACKEND_DEFAULT` is `RECOVERY_BACKEND_FS`.

Control flow: Config code stores one of these enum values in `nfs_version4_parameter_t`; recovery subsystems switch on it to choose the implementation for client/state recovery data.

State and persistence: The enum controls where persistent recovery records live. It does not itself store recovery state.

Dependencies and integration points: Included by `gsh_config.h` and any code interpreting NFSv4 recovery backend options.

Risks: Adding or reordering enum values can break config serialization or switch handling. `RECOVERY_BACKEND_NONE` disables recovery semantics and must be treated carefully around grace behavior.

Test signals: Verify config parsing for each backend, default behavior, switch exhaustiveness, and startup/restart behavior with filesystem and RADOS recovery modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_recovery.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_refstr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_refstr.h

Purpose: This header defines an RCU-friendly refcounted string object used for shared paths and other mutable pointer-to-string configuration.

Important APIs/types/functions: `struct gsh_refstr` contains a `urcu_ref` and flexible string buffer. `gsh_refstr_alloc` allocates a buffer of caller-specified length. Inline `gsh_refstr_dup` duplicates a C string. `gsh_refstr_release` is the refcount release callback. `gsh_refstr_get` increments a nonzero refcount using `urcu_ref_get_unless_zero` when available or a compare/exchange fallback. `gsh_refstr_put` releases references.

Control flow: Writers publish/replace pointers under RCU-style discipline. Readers fetch a pointer, take a reference while protected, use `gr_val`, then put it.

State and persistence: Refcounted strings are in-memory lifetime-managed state. In this subset they are important for `req_op_context` fullpath/pseudopath references that remain valid during an operation even if exports are updated.

Dependencies and integration points: Depends on liburcu refcount APIs, atomics, and standard string allocation headers. Used by export/op-context path management and any shared string needing stable references.

Risks: `gsh_refstr_get` aborts if the refcount is zero or wraps, so callers must obey RCU/ref ownership rules. Allocation lengths must include the terminating NUL. Forgetting puts leaks path/config strings.

Test signals: Test duplicate contents, concurrent get/put under RCU, fallback compare/exchange path if supported, zero-ref protection, release callback freeing, and op-context path replacement scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_refstr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_rpc.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_rpc.h

Purpose: This header is Ganesha's central RPC include and utility surface, intentionally isolating direct TIRPC/RPC includes behind one project header.

Important APIs/types/functions: Lookahead flags describe request classes and `NFS_LOOKAHEAD_HIGH_LATENCY` identifies latency-heavy operations. XDR maximum constants bound arrays, strings, generic bytes, and IO bytes. GSS/Kerberos defaults and `nfs_krb5_parameter_t` are defined when GSSAPI is enabled. Utility APIs include `log_sperror_gss`, `str_gc_proc`, `copy_xprt_addr`, `display_xprt_sockaddr`, `xprt_type_to_str`, `xdr_READ4res_uio_setup`, global `ntirpc_pp`, `struct io_data`, and `xdr_io_data`.

Control flow: RPC service code includes this header, classifies decoded requests with lookahead flags, uses TIRPC transport helpers for addresses, and serializes scatter/gather IO through `io_data`.

State and persistence: Holds no persistent state except references to global TIRPC package params and Kerberos config structs. Runtime IO data may carry release callbacks for buffer ownership.

Dependencies and integration points: Includes project atomics before RPC headers to avoid name conflicts, then TIRPC, GSSAPI conditionals, utilities, memory, lists, logging, and worker threads. It feeds NFS protocol decoders, transports, GSS security, and XDR helpers.

Risks: XDR limits are security and resource controls; changing them affects memory exposure. Include ordering protects against header name collisions. IO release callbacks must match buffer ownership.

Test signals: Build with/without GSSAPI and RDMA, validate XDR size enforcement, display local/remote transport addresses, test lookahead classification, serialize/deserialize `io_data`, and check Kerberos default config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_status.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_status.h

Purpose: This header defines Ganesha's unified state/SAL status enum.

Important APIs/types/functions: `state_status_t` enumerates success and many failure classes, including allocation, LRU/hash/cache errors, FSAL errors, permissions, stale entries, locks, grace, share denied, bad handles, bad ranges, and server faults. `STATE_FSAL_ESTALE` aliases `STATE_ESTALE`.

Control flow: SAL/cache/state/upcall code returns these values to describe internal outcomes independently of raw FSAL status, allowing callers to map them to protocol replies or retry/cleanup behavior.

State and persistence: No state is stored. The enum values encode control decisions around lock blocking, grace period, stale state, and cache consistency.

Dependencies and integration points: Standalone header used by FSAL upcalls, state management, cache inode, and related layers.

Risks: Many errors overlap semantically with FSAL and NFS errors; inconsistent mapping can return wrong protocol status. Adding enum values requires auditing switch statements and stringification/mapping code.

Test signals: Verify FSAL-to-state mappings, upcall return handling, lock conflict/block/deadlock paths, grace-period behavior, stale handle handling, and switch exhaustiveness in status conversion helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_types.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_types.h

Purpose: This header provides small cross-layer primitive types used throughout Ganesha.

Important APIs/types/functions: `nsecs_elapsed_t` is a 64-bit nanosecond duration type, with `NS_PER_USEC`, `NS_PER_MSEC`, and `NS_PER_SEC` constants. `struct gsh_buffdesc` is a counted buffer descriptor with `addr` and `len`.

Control flow: Buffer descriptors are passed through FSAL handle conversion, hash table keys/values, upcalls, and protocol helpers instead of raw pointer/length pairs. Nanosecond constants support elapsed-time calculations.

State and persistence: The header owns no state. `gsh_buffdesc` often points into caller-owned memory, so ownership and lifetime are external.

Dependencies and integration points: Depends only on standard integer and allocation headers and is included by many core utility and FSAL headers.

Risks: `gsh_buffdesc` does not encode capacity, mutability, or ownership; APIs must document whether `len` is input size or output size. Null `addr` with nonzero length is unsafe unless a callee explicitly permits it.

Test signals: For APIs using `gsh_buffdesc`, test boundary lengths, zero-length buffers, output length updates, and ownership behavior. For elapsed-time users, check unit conversions and overflow assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_wait_queue.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_wait_queue.h

Purpose: This header defines a simple pthread-based wait queue building block.

Important APIs/types/functions: `wait_entry_t` combines a mutex and condition variable. Wait queue flags include `Wqe_LFlag_None`, `Wqe_LFlag_WaitSync`, and `Wqe_LFlag_SyncDone`. `wait_q_entry_t` tracks flags, waiter count, left/right wait entries, and an intrusive `glist_head`. Inline helpers initialize and destroy wait entries and queue entries.

Control flow: Callers embed or allocate a `wait_q_entry_t`, initialize its list node and condition variables, enqueue it via `glist`, and use the left/right wait entries for synchronization protocols implemented outside this header.

State and persistence: Queue state is in-memory: waiter counts, flags, two condition-variable endpoints, and queue membership. No persistent storage is involved.

Dependencies and integration points: Depends on pthreads, `gsh_list.h`, and `common_utils.h` for pthread wrapper macros. It is a utility for thread coordination elsewhere in the server.

Risks: The header only initializes primitives; it does not define locking rules. Destroying while waiters exist, failing to initialize `flags`/`waiters` explicitly, or list misuse can cause races or deadlocks.

Test signals: Test init/destroy paths, queue insertion/removal around initialized entries, wait/signal users for both left and right entries, flag transitions, and shutdown with no active waiters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_wait_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_xprt_tracepoint.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gsh_xprt_tracepoint.h

Purpose: This header adds transport-aware wrappers around the generic Ganesha LTTng tracepoint macros.

Important APIs/types/functions: `GSH_XPRT_AUTO_TRACEPOINT` and `GSH_XPRT_UNIQUE_AUTO_TRACEPOINT` prepend `XPRT_FMT` and `XPRT_VARS(_xprt)` to the caller's format/arguments, then delegate to `GSH_AUTO_TRACEPOINT` or `GSH_UNIQUE_AUTO_TRACEPOINT`.

Control flow: RPC transport code calls these macros when logging events tied to an `SVCXPRT`. The lower GSH tracepoint layer supplies server/op IDs and LTTng/no-op behavior.

State and persistence: It stores no state. Trace output captures runtime transport metadata extracted from the transport argument.

Dependencies and integration points: Includes `gsh_lttng/gsh_lttng.h` and `rpc/svc.h`; relies on ntirpc-provided `XPRT_FMT` and `XPRT_VARS` macros.

Risks: `_xprt` must be valid for `XPRT_VARS`. Format and argument ordering must remain aligned after macro expansion. No include guard is present in the file, so repeated inclusion relies on the idempotence of included macros and definitions.

Test signals: Compile transport tracing call sites, build with/without LTTng, emit traces with TCP/RDMA/local transports, validate format fields, and test null/invalid transport avoidance at call sites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gsh_xprt_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gss_credcache.h -->
# sources/user-network-fs/nfs-ganesha/src/include/gss_credcache.h

Purpose: This header declares GSS/Kerberos credential cache management functions imported from the gssd-style credential refresh layer.

Important APIs/types/functions: `struct gssd_k5_kt_princ` is forward declared for keytab principal data. Global `ccachesearch[]` lists credential cache search locations. Public functions initialize, shut down, and clear the credential cache, verify mechanisms with `gssd_check_mechs`, and refresh machine credentials with `gssd_refresh_krb5_machine_credential`.

Control flow: Ganesha's GSS/RPC security startup initializes the cache, checks available mechanisms, refreshes machine credentials from keytabs/principals, and clears/shuts down during lifecycle events.

State and persistence: Credential cache state is external Kerberos/GSS state, potentially backed by filesystem or memory caches. The header controls access but does not define storage.

Dependencies and integration points: Includes BSD queue, RPC/GSS, Kerberos, and GSSAPI headers. Integrates with NFS_KRB5 configuration, RPCSEC_GSS callbacks, and machine credential renewal.

Risks: Credential cache paths and keytab principal handling are security-sensitive. Refresh failures can break secure NFS callbacks. Build depends on Kerberos/GSS headers and ABI compatibility with imported gssd structures.

Test signals: Build with GSS support, initialize/shutdown repeatedly, validate mechanism detection, refresh credentials for valid and invalid keytabs/principals, clear caches, and exercise secure NFS callback authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/gss_credcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/hashtable.h -->
# sources/user-network-fs/nfs-ganesha/src/include/hashtable.h

Purpose: This header declares Ganesha's concurrent non-intrusive hash table built from partitioned red-black trees with optional front-end caching.

Important APIs/types/functions: `struct hash_data` stores key/value `gsh_buffdesc` pairs. `struct hash_param` supplies hash, index, combined hash, comparison, display, naming, logging, and cache settings. `hash_stat_t`, `struct hash_partition`, `hash_table_t`, and `struct hash_latch` model table internals and latched lookup state. Public primitives include `hashtable_init`, destroy, get/acquire/release latch, set/delete latched, delete-all, logging, test-and-set, getref, and for-each. Inline wrappers `HashTable_Get`, `HashTable_Set`, and `HashTable_Del` implement common operations.

Control flow: Callers initialize with partition/hash functions, perform lookups by key, optionally latch a partition/tree position, then set/delete while holding latch state. Partitions use rwlocks; nodes and data come from pools.

State and persistence: In-memory table state includes per-partition counts, RBTs, locks, optional caches, and pooled key/value buffers. Stored buffer ownership is governed by caller/destructor callbacks.

Dependencies and integration points: Depends on RBT, pthreads, logging, display, memory pools, and `gsh_types.h`. Used by caches, duplicate request/state maps, and other keyed registries.

Risks: Hash function and comparator must agree or lookups fail. `HashTable_Set` defaults to no overwrite to avoid leaks. Latched paths require release on all outcomes. `HashTable_Del` fall-through behavior is intentional but easy to misread.

Test signals: Test create/destroy with destructors, get/set/delete success and missing-key paths, overwrite/no-overwrite/test-only behavior, latch release on errors, partition concurrency, cache-enabled lookup, stats/log display, and for-each traversal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/hashtable.h -->
