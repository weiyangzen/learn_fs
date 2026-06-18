# subset-b-005684 Research

Grouped source research for lockd service/procedure/locking/XDR support, VFS file locking, mbcache, and selected minix filesystem files. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svc.c -->
# sources/distributed-fs/ceph-client/fs/lockd/svc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svc.c` is the central Linux lockd service implementation. It owns the NLM RPC service process, per-network-namespace lockd lifecycle, grace period scheduling, socket listener setup, module/sysctl/netlink configuration, request dispatch, and registration of NLM protocol versions. The source was read as a complete 791-line file for this report.

## Important APIs, Types, and Functions

Important globals are `nlmsvc_ops`, `nlmsvc_mutex`, `nlmsvc_users`, `nlmsvc_serv`, `nlmsvc_retry`, `lockd_net_id`, `nlm_timeout`, `nlm_udpport`, and `nlm_tcpport`. Public/exported entry points are `lockd_up`, `lockd_down`, and `nlmsvc_dispatch`; generic-netlink entry points are `lockd_nl_server_set_doit` and `lockd_nl_server_get_doit`. Core helpers include `get_lockd_grace_period`, `set_grace_period`, `lockd`, `make_socks`, `lockd_up_net`, `lockd_down_net`, `lockd_get`, `lockd_put`, `lockd_authenticate`, `lockd_init_net`, `init_nlm`, and `exit_nlm`. Static data includes the `nlm_sysctls` table, `lockd_net_ops`, `nlmsvc_version[]`, and `nlmsvc_program`.

## Control Flow

Module initialization registers sysctls, pernet state, the lockd netlink family, and procfs. `lockd_up` serializes with `nlmsvc_mutex`, creates the single `svc_serv` and kernel service thread on first user, then binds listeners and starts the per-net grace period. The lockd thread loops until stopped, retrying blocked locks via `nlmsvc_retry_blocked` and receiving RPCs with `svc_recv`. `nlmsvc_dispatch` decodes a request through the selected `svc_procedure`, calls the procedure function, optionally drops the reply, and encodes a response. `lockd_down` decrements per-net and global users, destroys xprts, ends grace, stops the service thread, deletes the retry timer, and releases the service.

## State and Persistence Behavior

State is in memory: global service references, per-net `struct lockd_net` values, delayed grace work, xprt listeners, and module/sysctl/netlink configuration. There is no file-backed persistence here. Grace state is persisted only for the lifetime of a net namespace and is terminated by delayed work or shutdown. Per-net netlink updates can mirror into legacy global module/sysctl values when operating on `init_net`.

## Dependencies and Integration Points

The file integrates SUNRPC server infrastructure, svc sockets/xprts, net namespaces, procfs, generic netlink, sysctl/module parameters, network address notifiers, NFS export callbacks through `nlmsvc_ops`, and the VFS lock grace API through `locks_start_grace` and `locks_end_grace`. It exposes lockd lifecycle to NFS client/server code through exported `lockd_up` and `lockd_down`.

## Risks and Edge Cases

Lifecycle correctness depends on balanced global and per-net user counts. Listener creation failures must destroy partially-created xprts. Address removal notifiers age temporary transports while the service may be concurrently stopping. Grace-period values are bounded, but per-net and legacy global values must stay consistent for `init_net`. Authentication intentionally allows callback procedures without resolving an export client, leaving each procedure responsible for host lookup.

## Test Signals

Useful signals are lockd module load/unload with sysctls enabled, `lockd_up`/`lockd_down` refcount stress across multiple net namespaces, RPC NULL calls for NLM versions 1/3/4, netlink set/get of grace and ports, listener creation on IPv4/IPv6 including `-EAFNOSUPPORT`, network-address removal aging xprts, grace-period behavior after startup, and decode/encode failure paths in `nlmsvc_dispatch`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svc4proc.c -->
# sources/distributed-fs/ceph-client/fs/lockd/svc4proc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svc4proc.c` implements the server-side NLM version 4 RPC procedure table and handlers. It bridges generated NLMv4 XDR structures to legacy lockd `struct nlm_lock`/`struct nlm_cookie` state, performs host/file lookup, invokes the common server lock/share engine, handles asynchronous callback-style procedures, and exports `nlmsvc_version4`. The source was read as a complete 1424-line file for this report.

## Important APIs, Types, and Functions

The wrapper types `nlm4_testargs_wrapper`, `nlm4_lockargs_wrapper`, `nlm4_cancargs_wrapper`, `nlm4_unlockargs_wrapper`, `nlm4_notifyargs_wrapper`, `nlm4_testres_wrapper`, `nlm4_shareargs_wrapper`, `nlm4_res_wrapper`, and `nlm4_shareres_wrapper` place the xdrgen type first so the RPC layer can cast them safely. Important helpers are `nlm4_netobj_to_cookie`, `nlm4_lock_to_nlm_lock`, `nlm4svc_lookup_host`, `nlm4svc_lookup_file`, `nlm4svc_do_lock`, and `nlm4svc_callback`. Procedure handlers cover NULL, TEST, LOCK, CANCEL, UNLOCK, GRANTED, TEST_MSG, LOCK_MSG, CANCEL_MSG, UNLOCK_MSG, GRANTED_MSG, GRANTED_RES, SM_NOTIFY, SHARE, UNSHARE, NM_LOCK, and FREE_ALL. The exported version object is `nlmsvc_version4`.

## Control Flow

The RPC dispatcher selects `nlm4svc_procedures[]`, decodes into one of the wrapper structs, and calls a procedure. Most operations resolve an `nlm_host`, convert the file handle/owner/range into an `nlm_lock`, look up an `nlm_file`, set VFS lock metadata, then call common helpers such as `nlmsvc_testlock`, `nlmsvc_lock`, `nlmsvc_cancel_blocked`, `nlmsvc_unlock`, `nlmsvc_share_file`, or `nlmsvc_unshare_file`. `_MSG` procedures allocate an `nlm_rqst`, execute the same inner operation into `call->a_res`, and send an async response through `nlm_async_reply`. `GRANTED_RES` converts the result cookie back into a lockd cookie and completes pending grant state through `nlmsvc_grant_reply`.

## State and Persistence Behavior

The file owns no persistent storage. It builds per-RPC wrapper instances in the SUNRPC request buffer, takes temporary references to `nlm_host`, `nlm_file`, `nlm_rqst`, and lock owners, and releases them before returning or through RPC call-release callbacks. Persistent lock/share/block state is delegated to `svclock.c`, `svcshare.c`, and `svcsubs.c`.

## Dependencies and Integration Points

Dependencies include generated `nlm4xdr_gen.h`, common `lockd.h`, `share.h`, NSM monitoring through `nsm_monitor`, host lookup/release, common NLM service lock/share functions, VFS lock helpers via `nlmsvc_locks_init_private`, and SUNRPC async reply machinery. It is included in the central program table by `svc.c` when `CONFIG_LOCKD_V4` is enabled.

## Risks and Edge Cases

Wrapper layout is guarded by `static_assert`; any xdrgen ABI drift would break request storage casting. Range checks reject offsets or lengths beyond `OFFSET_MAX`; missing or invalid file handles translate to NLMv4 status codes. Host/file/lock-owner references must be released on every exit path. Async callback helpers transfer host ownership and release calls through RPC callbacks. Grace period checks differ by operation, especially reclaim, cancel, unlock, share, and unshare. The private `SM_NOTIFY` path must reject unprivileged requesters.

## Test Signals

Exercise NLMv4 TEST/LOCK/CANCEL/UNLOCK/GRANTED, both synchronous and `_MSG`/`_RES` forms; check blocked-lock callbacks and grant retries; verify reclaim versus non-reclaim during grace; fuzz oversized cookie, file handle, and range values; test SHARE/UNSHARE conflict matrices; send unprivileged and privileged SM_NOTIFY; and compile with/without `CONFIG_LOCKD_V4` to catch generated XDR layout integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svc4proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svclock.c -->
# sources/distributed-fs/ceph-client/fs/lockd/svclock.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svclock.c` implements the common server-side lock engine for lockd, especially blocked locks, deferred VFS lock callbacks, client grant callbacks, lock-owner lifetime, and retry scheduling. The source was read as a complete 1076-line file for this report.

## Important APIs, Types, and Functions

Important file state includes global `nlm_blocked`, `nlm_blocked_lock`, and `nlmsvc_lock_operations`. Public/common entry points are `nlmsvc_lock`, `nlmsvc_testlock`, `nlmsvc_unlock`, `nlmsvc_cancel_blocked`, `nlmsvc_retry_blocked`, `nlmsvc_grant_reply`, `nlmsvc_traverse_blocks`, `nlmsvc_locks_init_private`, `nlmsvc_release_lockowner`, `nlmsvc_put_lockowner`, and `nlmsvc_release_call` from the paired procedure file. Key helpers include `nlmsvc_create_block`, `nlmsvc_lookup_block`, `nlmsvc_find_block`, `nlmsvc_unlink_block`, `nlmsvc_setgrantargs`, `nlmsvc_defer_lock_rqst`, `nlmsvc_grant_deferred`, `nlmsvc_notify_blocked`, `nlmsvc_grant_blocked`, and `retry_deferred_block`.

## Control Flow

`nlmsvc_lock` checks whether the backing file can lock, creates or finds an `nlm_block`, handles grace/reclaim rules, inserts the block into the retry list, then calls `vfs_lock_file`. Immediate success removes the block and returns granted; `-EAGAIN`, `FILE_LOCK_DEFERRED`, `-EDEADLK`, and other errors become NLM statuses. Filesystem callbacks enter through `nlmsvc_lock_operations.lm_notify` or `.lm_grant`, mark blocks ready, move them toward the head of `nlm_blocked`, and wake the lockd service. `nlmsvc_retry_blocked` scans ready blocks, revisits deferred requests or retries blocked grants. Successful VFS grants send `NLMPROC_GRANTED_MSG` asynchronously, then `nlmsvc_grant_reply` removes or retries the block based on the client's reply.

## State and Persistence Behavior

The file owns transient in-memory blocked lock state. Each `nlm_block` links into the global retry list and the owning `nlm_file` block list, references an `nlm_rqst`, file, host, and daemon, and is released by `kref`. Lock owners are per-host structures refcounted by VFS lock-manager callbacks. No state is persistent across lockd shutdown; remote clients recover through NSM and NLM grace/reclaim mechanisms.

## Dependencies and Integration Points

It integrates with VFS locking through `vfs_lock_file`, `vfs_test_lock`, `vfs_cancel_lock`, `locks_can_async_lock`, `locks_delete_block`, `locks_copy_lock`, and `lock_manager_operations`. It depends on SUNRPC async calls for grant callbacks, `svc_wake_up` and `nlmsvc_retry` scheduling from `svc.c`, host and file management from lockd, and the common NLM status model.

## Risks and Edge Cases

The block lifecycle is race-prone: comments call out GRANT and CANCEL crossing in flight, list traversal while callbacks move entries, and an RPC release callback that may call a path taking a mutex. File mutex and global spinlock ordering must remain correct. Deferred non-blocking locks use request-cache revisit callbacks and timeouts. `vfs_lock_file` can modify lock ranges, so grant messages preserve and restore original ranges. Lock-owner allocation failures must become no-locks statuses. Client refusal of a grant requires unlocking the VFS lock.

## Test Signals

Stress blocking and non-blocking locks with local POSIX locks and a filesystem supporting async locks; race CANCEL, UNLOCK, GRANTED_RES, service shutdown, and VFS grant callbacks; verify deadlock status translation; monitor `/proc/locks` and lockd debug output for leaked blocks; test retry timers and soft RPC callback failures; and run NFS lock recovery tests through server restarts and grace windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svclock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svcproc.c -->
# sources/distributed-fs/ceph-client/fs/lockd/svcproc.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svcproc.c` implements the NLM version 1 and version 3 server procedure handlers and procedure tables. It decodes legacy lockd arguments, resolves hosts and files, invokes the shared server lock/share implementation, handles async response procedures, status casting, statd notifications, and exports `nlmsvc_version1` and `nlmsvc_version3`. The source was read as a complete 838-line file for this report.

## Important APIs, Types, and Functions

Core helpers include `cast_status`, `nlmsvc_retrieve_args`, `__nlmsvc_proc_test`, `__nlmsvc_proc_lock`, `__nlmsvc_proc_cancel`, `__nlmsvc_proc_unlock`, `__nlmsvc_proc_granted`, and `nlmsvc_callback`. Important procedure functions include `nlmsvc_proc_null`, TEST, LOCK, CANCEL, UNLOCK, GRANTED, TEST_MSG, LOCK_MSG, CANCEL_MSG, UNLOCK_MSG, GRANTED_MSG, SHARE, UNSHARE, NM_LOCK, FREE_ALL, SM_NOTIFY, GRANTED_RES, and `nlmsvc_proc_unused`. Important data includes `nlmsvc_procedures[24]`, `union nlmsvc_xdrstore`, `nlm1svc_call_counters`, `nlm3svc_call_counters`, `nlmsvc_version1`, and `nlmsvc_version3`.

## Control Flow

The central dispatcher in `svc.c` decodes into `struct nlm_args`, `struct nlm_res`, or `struct nlm_reboot` based on `nlmsvc_procedures[]`. `nlmsvc_retrieve_args` verifies nfsd callback binding, resolves an `nlm_host`, optionally monitors it through NSM, looks up an `nlm_file`, and initializes the embedded VFS `file_lock`. Each procedure performs grace checks, calls the corresponding shared operation, casts internal statuses to legacy protocol statuses, and releases lock-owner/host/file references. `_MSG` variants allocate an async `nlm_rqst` and send a reply procedure before returning a void RPC response.

## State and Persistence Behavior

This file owns no durable state. It uses per-RPC argument/result storage and transient host/file/call references. Shared state is maintained by the host cache, `svcsubs.c` file table, `svclock.c` blocked locks, and `svcshare.c` share lists. Per-CPU call counters persist while the module is loaded.

## Dependencies and Integration Points

It depends on hand-written NLM XDR functions from `xdr.c`/`xdr.h`, host lookup and NSM monitoring, `nlmsvc_lock_operations`, VFS lock helpers, shared lock/share/free-resource helpers, and SUNRPC async reply support. Version objects are consumed by the program table in `svc.c`.

## Risks and Edge Cases

Status translation differs with `CONFIG_LOCKD_V4`: internal stale-fh and failed statuses are collapsed for v1/v3, while v4-aware builds preserve more codes when possible. Reference release paths are repetitive and must stay balanced. FREE_ALL passes `filp == NULL` to retrieve only the host. Legacy `_RES` procedures mostly decode void or results and ignore content except GRANTED_RES. The private SM_NOTIFY path must remain privileged-only.

## Test Signals

Run NLMv1 and NLMv3 TEST/LOCK/CANCEL/UNLOCK/GRANTED plus SHARE/UNSHARE/NM_LOCK/FREE_ALL. Exercise `_MSG` procedures and callback response generation. Verify status casting for stale handles, deadlocks, failed opens, and drop-reply. Test grace and reclaim behavior. Send statd notifications from privileged and unprivileged sources. Confirm per-version procedure counts and XDR storage sizes through build and RPC smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svcproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svcshare.c -->
# sources/distributed-fs/ceph-client/fs/lockd/svcshare.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svcshare.c` manages NLM DOS-style share reservations for files served by lockd. It creates, updates, removes, and bulk-traverses per-file `nlm_share` records. The source was read as a complete 125-line file for this report.

## Important APIs, Types, and Functions

The local helper `nlm_cmp_owner` compares an existing `nlm_share` owner handle with a request owner handle. Public/common functions are `nlmsvc_share_file`, `nlmsvc_unshare_file`, and `nlmsvc_traverse_shares`. State is stored in the `file->f_shares` singly-linked list of `struct nlm_share` objects.

## Control Flow

`nlmsvc_share_file` first rejects files that cannot lock, then scans existing shares. If a share for the same host and owner exists, it updates the access and mode fields. If another share conflicts by requested access/mode, it returns denied. Otherwise it allocates one object plus inline owner-handle storage, copies the owner, links it at the head of `file->f_shares`, and returns granted. `nlmsvc_unshare_file` scans the same list, removes matching host/owner entries, and returns granted even if no matching share exists. `nlmsvc_traverse_shares` removes all shares whose host matches a supplied predicate.

## State and Persistence Behavior

Share state is in-memory only and attached to `struct nlm_file`. Owner-handle bytes are stored inline after each allocated `struct nlm_share`. Shares disappear when explicitly unshared, when host resources are freed, or when the file record is reclaimed by `svcsubs.c`.

## Dependencies and Integration Points

The file integrates with lockd host/file structures from `lockd.h`, share declarations from `share.h`, and the NLM procedure handlers in `svcproc.c`/`svc4proc.c`. Resource cleanup is driven by `nlmsvc_traverse_files` in `svcsubs.c`.

## Risks and Edge Cases

Conflicts depend on bitwise overlap of access and deny modes, so procedure-layer validation of mode values matters. There is no local locking in this file; callers must serialize access through the owning file/resource traversal path. Owner handles are length-sensitive binary blobs, not NUL-terminated strings. The X/Open behavior of successful unshare for a missing reservation is intentional.

## Test Signals

Test same-host same-owner updates, conflicting and non-conflicting share combinations, unshare of present and absent entries, FREE_ALL and host-reboot cleanup through `nlmsvc_traverse_shares`, allocation failure status, and SHARE/UNSHARE during grace/reclaim from both v1/v3 and v4 handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svcshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svcsubs.c -->
# sources/distributed-fs/ceph-client/fs/lockd/svcsubs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svcsubs.c` provides support routines for the NLM server file table and resource cleanup. It maps NLM file handles to opened VFS files, tracks file references, traverses locks/blocked locks/shares, and exports cleanup helpers used by NFSD failover and network events. The source was read as a complete 521-line file for this report.

## Important APIs, Types, and Functions

Important state includes `nlm_files[FILE_NRHASH]` and `nlm_file_mutex`. Public/common functions include `lock_to_openmode`, `nlm_lookup_file`, `nlm_release_file`, `nlmsvc_mark_resources`, `nlmsvc_free_host_resources`, `nlmsvc_invalidate_all`, `nlmsvc_unlock_all_by_sb`, and `nlmsvc_unlock_all_by_ip`. Core helpers include `nlm_do_fopen`, `nlm_delete_file`, `nlm_unlock_files`, `nlm_traverse_locks`, `nlm_inspect_file`, `nlm_file_inuse`, `nlm_close_files`, and `nlm_traverse_files`.

## Control Flow

`nlm_lookup_file` hashes the NFS file handle, serializes the table with `nlm_file_mutex`, opens the needed read or write VFS file through `nlmsvc_ops->fopen`, creates a new `nlm_file` if required, links it into the hash table, and increments `f_count`. `nlm_release_file` decrements `f_count` and deletes the record if no file references, blocked locks, shares, or NLM-managed VFS locks remain. Cleanup APIs traverse every hash bucket, temporarily pin each file, call `nlmsvc_traverse_blocks`, `nlmsvc_traverse_shares`, and `nlm_traverse_locks`, then remove idle files. Superblock and IP cleanup pass match predicates to this traversal.

## State and Persistence Behavior

The file table is in-memory and global to lockd. Each `nlm_file` keeps a file handle, optional read/write `struct file` pointers, a reference count, a block list, share list, and cached lock count. VFS file opens are closed through `nlmsvc_ops->fclose` when the `nlm_file` is deleted or traversal finds it idle. There is no on-disk state here.

## Dependencies and Integration Points

It depends on NFSD-provided lockd bindings (`nlmsvc_ops->fopen`/`fclose`), VFS lock contexts from `locks_inode_context`, `vfs_lock_file`, lock manager identity `nlmsvc_lock_operations`, host matching helpers, SUNRPC address comparison, and share/block traversal functions from companion lockd files. It exports cleanup hooks for filesystems and network address handling.

## Risks and Edge Cases

File-handle hashing uses only the NFSv2-size bytes, so collisions are expected and handled by full handle comparison. Opening reexported files can block the lockd thread. `-EWOULDBLOCK` maps to an internal drop-reply status. Cleanup cannot rely on exact refcounts because VFS locks can be split/merged without lockd notification, so it scans inode lock lists. Traversal temporarily drops the file-table mutex, requiring careful `f_count` pinning. Failure to unlock all resources triggers warnings and in one path `BUG()`.

## Test Signals

Test lookup of existing and new file handles for read/write modes, stale handle and deferred open mapping, file release after lock/share/block cleanup, host resource free after client reboot/FREE_ALL, server shutdown invalidation, `nlmsvc_unlock_all_by_sb`, `nlmsvc_unlock_all_by_ip`, and leak warnings when VFS locks remain on file removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svcsubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svcxdr.h -->
# sources/distributed-fs/ceph-client/fs/lockd/svcxdr.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svcxdr.h` defines small inline XDR encode/decode helpers for basic NLM service data types shared by hand-written server XDR code. It handles status words, strings, cookies, and owner netobjs. The source was read as a complete 142-line file for this report.

## Important APIs, Types, and Functions

Inline functions are `svcxdr_decode_stats`, `svcxdr_encode_stats`, `svcxdr_decode_string`, `svcxdr_decode_cookie`, `svcxdr_encode_cookie`, `svcxdr_decode_owner`, and `svcxdr_encode_owner`. It relies on `NLM_MAXSTRLEN`, `NLM_MAXCOOKIELEN`, `XDR_MAX_NETOBJ`, `struct nlm_cookie`, and `struct xdr_netobj`.

## Control Flow

Each helper advances an `xdr_stream` by reading or reserving fixed or opaque fields. Decoders validate maximum lengths, obtain inline storage, and either copy into fixed lockd buffers or return pointers into the request buffer. Cookie decoding special-cases zero-length cookies by manufacturing a four-byte zero cookie for HPUX compatibility.

## State and Persistence Behavior

The helpers own no persistent state. String and owner decoders return pointers into the transient RPC receive buffer. Cookie decoding copies bytes into caller-provided `struct nlm_cookie` storage.

## Dependencies and Integration Points

This header is included by `xdr.c` and relies on SUNRPC `xdr_stream` helpers. The v1/v3 procedure tables use these helpers indirectly through `nlmsvc_decode_*` and `nlmsvc_encode_*` functions.

## Risks and Edge Cases

Length validation is the main safety boundary. Cookie length is intentionally limited to 32 bytes even though the protocol allows larger opaque cookies. Owner objects are limited by `XDR_MAX_NETOBJ`, while strings are limited by `NLM_MAXSTRLEN`. Returned request-buffer pointers must not outlive the RPC decode context.

## Test Signals

Fuzz XDR decode paths with oversized strings, cookies, and owner handles; validate zero-length cookie compatibility; test short/truncated streams; and run NLM v1/v3 lock procedures with binary owner handles and maximum-length caller strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/svcxdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/trace.c -->
# sources/distributed-fs/ceph-client/fs/lockd/trace.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/trace.c` instantiates the lockd tracepoints declared in `trace.h` by defining `CREATE_TRACE_POINTS` before including the header. The source was read as a complete 3-line file for this report.

## Important APIs, Types, and Functions

The file contains no functions. Its important symbols are the generated tracepoint definitions emitted from `trace.h`, including client lock event tracepoints such as `nlmclnt_test`, `nlmclnt_lock`, `nlmclnt_unlock`, and `nlmclnt_grant`.

## Control Flow

There is no runtime control flow in this file. At build time, the tracepoint framework expands declarations from `trace.h` into storage and registration code in this translation unit.

## State and Persistence Behavior

Tracepoint state is generated by the tracing subsystem and exists only while the kernel/module is loaded. This file itself owns no manually-managed state.

## Dependencies and Integration Points

It depends directly on `trace.h` and indirectly on Linux tracepoint infrastructure. Other lockd code can call generated `trace_*` helpers once this translation unit provides the definitions.

## Risks and Edge Cases

The main risk is duplicate or missing `CREATE_TRACE_POINTS` placement. If another file also instantiated the same tracepoints, build/link failures would occur; if this file were omitted, tracepoint declarations would lack definitions.

## Test Signals

Build lockd with tracing enabled, verify tracepoint symbols are present, and enable lockd trace events while running NLM client operations to confirm event registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/trace.h -->
# sources/distributed-fs/ceph-client/fs/lockd/trace.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/trace.h` declares lockd trace events for NLM client lock operations. It defines symbolic NLM status rendering and an event class capturing lock owner, server address, file-handle hash, range, and status. The source was read as a complete 107-line file for this report.

## Important APIs, Types, and Functions

Important macros include `TRACE_SYSTEM lockd`, `NLM_STATUS_LIST`, `show_nlm_status`, `DECLARE_EVENT_CLASS(nlmclnt_lock_event)`, and `DEFINE_NLMCLNT_EVENT`. Declared events are `nlmclnt_test`, `nlmclnt_lock`, `nlmclnt_unlock`, and `nlmclnt_grant`. Event fields include owner-handle CRC, `svid`, NFS file-handle hash, range start/length, sockaddr, and status.

## Control Flow

The header expands into trace event declarations and, when included by `trace.c` with `CREATE_TRACE_POINTS`, definitions. At runtime, callers hit generated tracepoint probes; the fast-assign block hashes the owner handle and file handle, stores the lock range and status, and copies the sockaddr for formatted output.

## State and Persistence Behavior

No persistent lockd state is owned here. Trace records are transient tracing-buffer entries managed by the kernel tracing subsystem.

## Dependencies and Integration Points

It includes `linux/tracepoint.h`, `linux/crc32.h`, `linux/nfs.h`, and `lockd.h`. It integrates with ftrace/perf tracepoint tooling and the generated trace include mechanism via `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE`.

## Risks and Edge Cases

The status list differs with `CONFIG_LOCKD_V4`; symbolic rendering must match available NLM constants. Trace output intentionally hashes owner and file handles rather than dumping raw bytes. The event uses `lock->lock_start` and `lock->lock_len`, so callers must keep those legacy fields populated if traces are expected to show meaningful ranges.

## Test Signals

Build with tracing, list events under the lockd trace system, enable `nlmclnt_*` events during client lock tests, and verify status names, sockaddr formatting, and range fields for NLMv3 and NLMv4 operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/xdr.c -->
# sources/distributed-fs/ceph-client/fs/lockd/xdr.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/xdr.c` provides hand-written server XDR support for legacy NLM v1/v3 procedures. It decodes request arguments into `struct nlm_args`, encodes `struct nlm_res` replies, and translates legacy 32-bit offset/length lock ranges to VFS `file_lock` ranges. The source was read as a complete 354-line file for this report.

## Important APIs, Types, and Functions

Local helpers include `s32_to_loff_t`, `loff_t_to_s32`, `svcxdr_decode_fhandle`, `svcxdr_decode_lock`, `svcxdr_encode_holder`, and `svcxdr_encode_testrply`. Exported-to-procedure-table functions include `nlmsvc_decode_void`, `nlmsvc_decode_testargs`, `nlmsvc_decode_lockargs`, `nlmsvc_decode_cancargs`, `nlmsvc_decode_unlockargs`, `nlmsvc_decode_res`, `nlmsvc_decode_reboot`, `nlmsvc_decode_shareargs`, `nlmsvc_decode_notify`, `nlmsvc_encode_void`, `nlmsvc_encode_testres`, `nlmsvc_encode_res`, and `nlmsvc_encode_shareres`.

## Control Flow

Decode functions consume fields in protocol order from `xdr_stream`: cookie, booleans, caller string, file handle, owner handle, svid, range, reclaim/state, share modes, or statd notify fields. `svcxdr_decode_lock` initializes a POSIX read lock by default, computes `fl_start`/`fl_end`, and callers set write or unlock type as needed. Encode functions write cookie/status pairs, optional conflicting holder data for denied TEST replies, and the share response sequence field.

## State and Persistence Behavior

The file owns no persistent state. Decoded strings and owner handles may point into the transient RPC receive buffer, while cookies and file handles are copied into request storage. VFS locks are initialized for later procedure-layer completion.

## Dependencies and Integration Points

It depends on SUNRPC XDR streams, NFSv2 file-handle size constants, `lockd.h`, `share.h`, `svcxdr.h`, and VFS lock initialization. Its functions are referenced by `svcproc.c` procedure descriptors.

## Risks and Edge Cases

NLM v1/v3 file handles are constrained to exactly `NFS2_FHSIZE`, not the protocol's larger generic opaque maximum. Offset conversion saturates to `NLM_OFFSET_MAX` on encode and treats zero or wrapped lengths as EOF on decode. Share-argument range checks are explicitly noted as missing in the original code. Truncated XDR input must fail without partially trusted state.

## Test Signals

Fuzz all decode routines with malformed/truncated XDR, max and zero cookies, invalid file-handle lengths, negative/overflowing ranges, and share mode values. Exercise TEST denied replies to validate holder encoding, EOF range encoding, and v1/v3 procedure-table xdr sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/xdr.h -->
# sources/distributed-fs/ceph-client/fs/lockd/xdr.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/xdr.h` defines the common lockd XDR-facing data structures, constants, NLM status macros, and prototypes for hand-written NLM v1/v3 server encode/decode helpers. The source was read as a complete 106-line file for this report.

## Important APIs, Types, and Functions

Important constants are `SM_MAXSTRLEN`, `SM_PRIV_SIZE`, `NLM_MAXCOOKIELEN`, and `NLM_MAXSTRLEN`. Status macros include `nlm_granted`, `nlm_lck_denied`, `nlm_lck_denied_nolocks`, `nlm_lck_blocked`, and `nlm_lck_denied_grace_period`. Types are `struct nsm_private`, `struct nlm_lock`, `struct nlm_cookie`, `struct nlm_args`, `struct nlm_res`, and `struct nlm_reboot`. Function prototypes declare the `nlmsvc_decode_*` and `nlmsvc_encode_*` routines implemented in `xdr.c`.

## Control Flow

This header has no runtime flow. It defines the storage layout that RPC decode routines fill, procedure handlers consume, and encode routines serialize.

## State and Persistence Behavior

No storage is allocated here. Instances are per-RPC request or response objects owned by SUNRPC service buffers, with embedded VFS `struct file_lock` state used only during request processing.

## Dependencies and Integration Points

It includes Linux fs/filelock/NFS/SUNRPC XDR headers and is consumed by lockd procedure, XDR, and trace code through `lockd.h`. The definitions bridge network protocol fields and VFS locking structures.

## Risks and Edge Cases

The cookie buffer is a deliberate implementation limit smaller than the protocol maximum. `struct nlm_lock` contains both legacy range fields and a VFS `file_lock`, so callers must keep the fields they use synchronized. Status macros are big-endian values and must not be compared as host-order integers without conversion.

## Test Signals

Compile coverage for all lockd XDR users, static checks for structure layout assumptions in procedure storage, NLM v1/v3 RPC decode/encode smoke tests, and tests that compare wire status values to expected big-endian NLM codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/lockd/xdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/locks.c -->
# sources/distributed-fs/ceph-client/fs/locks.c

## Purpose

`sources/distributed-fs/ceph-client/fs/locks.c` is the core VFS file locking implementation. It supports POSIX byte-range locks, BSD `flock` locks, open-file-description locks, leases, delegations, layout leases, blocked-lock dependency trees, deadlock detection, syscalls/fcntl entry points, lease break handling, `/proc/locks`, and exported helpers used by network lock managers such as lockd. The source was read as a complete 3097-line file for this report.

## Important APIs, Types, and Functions

Key exported APIs include `locks_alloc_lock`, `locks_alloc_lease`, `locks_release_private`, `locks_owner_has_blockers`, `locks_free_lock`, `locks_free_lease`, `locks_init_lock`, `locks_init_lease`, `locks_copy_conflock`, `locks_copy_lock`, `posix_test_lock`, `posix_lock_file`, `lease_modify`, `__break_lease`, `lease_get_mtime`, `generic_setlease`, `lease_register_notifier`, `lease_unregister_notifier`, `kernel_setlease`, `vfs_setlease`, `locks_lock_inode_wait`, `vfs_test_lock`, `vfs_lock_file`, `locks_remove_posix`, `vfs_cancel_lock`, and `vfs_inode_has_locks`. User entry points include `SYSCALL_DEFINE2(flock)`, `fcntl_getlk`, `fcntl_setlk`, and 32-bit `fcntl_getlk64`/`fcntl_setlk64` where applicable. Important state includes per-inode `file_lock_context`, per-CPU `file_lock_list`, `file_rwsem`, `blocked_hash`, `blocked_lock_lock`, kmem caches, lease sysctls, and the lease notifier chain.

## Control Flow

Lock operations allocate or initialize a `file_lock`, translate user `flock` structures into VFS ranges and owners, run security checks, then call `vfs_lock_file`. The generic POSIX path creates an inode lock context if needed, checks conflicts, optionally adds blocked requests with deadlock detection, merges adjacent same-owner locks, splits/downgrades replaced ranges, wakes blocked trees, and disposes removed locks. The flock path is whole-file and file-owner based. Lease operations add or modify lease records, notify on conflicting opens, break or downgrade leases with signals/callbacks, and optionally wait for break completion. Close paths remove POSIX, OFD, flock, and lease state. `/proc/locks` iterates global per-CPU lock lists and blocked dependency trees.

## State and Persistence Behavior

All state is in memory and attached to inodes, files, or global lock lists. `file_lock_context` persists while the inode lives and is freed with leak checks. Active locks and leases are stored on context lists and mirrored on global lists for `/proc/locks`; blocked waiters are linked beneath blockers and in `blocked_hash` for deadlock detection. There is no disk persistence; locks vanish with file close, process/file-owner cleanup, inode teardown, or filesystem/network-manager cleanup.

## Dependencies and Integration Points

The file integrates with LSM via `security_file_lock`, filesystem `file_operations->lock`, `->flock`, and `->setlease`, signal/fasync ownership for leases, procfs/seq_file, trace events from `trace/events/filelock.h`, sysctl, pid namespaces, SRCU notifiers, and network lock managers through `lock_manager_operations` hooks such as `lm_notify`, `lm_grant`, `lm_get_owner`, and `lm_put_owner`.

## Risks and Edge Cases

Concurrency is the main risk: `flc_lock`, `blocked_lock_lock`, `file_rwsem`, per-CPU list locks, and inode/file locks have strict roles. POSIX range updates must handle EOF, negative lengths, splitting into two locks, merging, and close/fcntl races. Deadlock detection is bounded and skipped for OFD locks. Async filesystem locks may return `FILE_LOCK_DEFERRED` only under documented conditions, and lock managers must later call `lm_grant`. Lease break timeouts can downgrade or remove leases. `/proc/locks` must traverse while preserving consistency and avoiding invisible PIDs.

## Test Signals

Run LTP/flock/fcntl/OFD lock suites, multithreaded range merge/split/unlock tests, deadlock-detection tests, close/fcntl race tests, filesystem `->lock` async/deferred tests with lockd, lease acquisition and break tests for read/write/delegation/layout leases, `/proc/locks` formatting tests across pid namespaces, kmemleak/KASAN lock lifecycle runs, and sysctl coverage for lease enable/break-time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/locks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mbcache.c -->
# sources/distributed-fs/ceph-client/fs/mbcache.c

## Purpose

`sources/distributed-fs/ceph-client/fs/mbcache.c` implements the metadata block cache used by ext2/ext4 for extended attribute block/value deduplication. It is a fixed-size hash table keyed by a 32-bit hash with unique key/value pairs, reusable-entry search, reference-counted entries, LRU-like reclaim, and shrinker integration. The source was read as a complete 444-line file for this report.

## Important APIs, Types, and Functions

The private `struct mb_cache` stores hash buckets, bucket sizing, max entries, a list and count protected by `c_list_lock`, a shrinker, and shrink work. Important exported APIs are `mb_cache_entry_create`, `__mb_cache_entry_free`, `mb_cache_entry_wait_unused`, `mb_cache_entry_find_first`, `mb_cache_entry_find_next`, `mb_cache_entry_get`, `mb_cache_entry_delete_or_get`, `mb_cache_entry_touch`, `mb_cache_create`, and `mb_cache_destroy`. Internal helpers include `mb_cache_entry_head`, `__entry_find`, `mb_cache_count`, `mb_cache_shrink`, `mb_cache_scan`, and `mb_cache_shrink_worker`.

## Control Flow

Cache creation allocates the cache, hash buckets, shrinker, and work item. Entry creation may schedule background shrinking or perform synchronous shrinking, allocates an entry with two refs, checks for a duplicate key/value under the bucket bit-lock, inserts into the hash and global list, increments count, and drops the setup ref. Lookup by key scans reusable entries and returns a ref; lookup by key/value returns a matching entry ref. Delete-or-get removes an unused key/value entry by atomically moving refcount from two to zero, otherwise returns a live ref. Shrinking scans the list, gives referenced or busy entries another chance, and frees unreferenced entries.

## State and Persistence Behavior

State is in-memory cache metadata only. Entries persist until dropped by explicit deletion, shrinker reclaim, or cache destruction. A hash-table reference normally holds entries alive; external users hold additional refs. Reusable and referenced bits influence lookup and reclaim but do not persist beyond memory.

## Dependencies and Integration Points

It depends on kernel list, bit-lock hlist, workqueue, shrinker, slab, and exported `linux/mbcache.h` entry helpers such as `mb_cache_entry_put`. ext2/ext4 xattr code are the primary callers.

## Risks and Edge Cases

The key is not unique; the key/value pair must be unique. Reference-count transitions are subtle, especially delete-or-get and shrinker freeing. Locking deliberately avoids nesting list locks into bucket bit-locks for RT. Destruction assumes no users except the shrinker can reach the cache. Background shrink may lag, so synchronous shrinking handles excessive growth.

## Test Signals

Test duplicate insertion, key collision iteration, reusable versus non-reusable lookup, delete-or-get under concurrent refs, shrinker reclaim of referenced and unreferenced entries, cache destroy after user drain, ext2/ext4 xattr block deduplication, and KASAN/KCSAN refcount stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/mbcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/Kconfig -->
# sources/distributed-fs/ceph-client/fs/minix/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/Kconfig` declares configuration options for the Minix filesystem driver and architecture-specific endian handling. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

Configuration symbols are `MINIX_FS`, `MINIX_FS_NATIVE_ENDIAN`, and `MINIX_FS_BIG_ENDIAN_16BIT_INDEXED`. `MINIX_FS` is a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`. The endian symbols are derived booleans with architecture dependencies.

## Control Flow

There is no runtime control flow. Kconfig controls whether `fs/minix` is built into the kernel, as a module, or omitted, and selects the bitmap/index endianness behavior compiled into the driver.

## State and Persistence Behavior

No runtime state is owned by this file. It affects build-time configuration and therefore which code paths and modules exist in the built kernel.

## Dependencies and Integration Points

It integrates with the kernel Kconfig system, block layer availability, buffer-head support, and architecture symbols that require native-endian or big-endian 16-bit indexed Minix bitmap behavior.

## Risks and Edge Cases

The root filesystem cannot be a module, which the help text documents. Incorrect architecture endian selection would corrupt bitmap interpretation. Selecting `BUFFER_HEAD` reflects the driver's dependence on buffer-head-based block IO.

## Test Signals

Build `MINIX_FS=y`, `m`, and `n`; verify `BUFFER_HEAD` selection; cross-build listed endian architectures; mount Minix v1/v2/v3 images; and confirm module name `minix` when built as a module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/Makefile -->
# sources/distributed-fs/ceph-client/fs/minix/Makefile

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/Makefile` defines how the Minix filesystem driver is built. The source was read as a complete 8-line file for this report.

## Important APIs, Types, and Functions

The build variables are `obj-$(CONFIG_MINIX_FS) += minix.o` and `minix-objs := bitmap.o itree_v1.o itree_v2.o namei.o inode.o file.o dir.o`.

## Control Flow

There is no runtime flow. Kbuild links the listed object files into `minix.o` when `CONFIG_MINIX_FS` is enabled.

## State and Persistence Behavior

No runtime state is owned. The file controls build composition only.

## Dependencies and Integration Points

It integrates with Kbuild and the `MINIX_FS` Kconfig symbol. The object list ties allocation bitmap handling, inode tree implementations, name lookup, inode operations, regular file operations, and directory operations into one filesystem module.

## Risks and Edge Cases

Missing any listed object would create unresolved symbols or incomplete filesystem behavior. Adding source files without updating this list would leave them unbuilt.

## Test Signals

Build Minix as built-in and module, verify all object files link, and run a mount/read/write smoke test on Minix images after build changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/minix/bitmap.c

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/bitmap.c` manages Minix block and inode allocation bitmaps and raw on-disk inode access for Minix v1/v2 layouts. It allocates/frees blocks and inodes, counts free resources, clears deleted inode records, and initializes new VFS inodes. The source was read as a complete 269-line file for this report.

## Important APIs, Types, and Functions

Important state is `bitmap_lock`, shared by inode and zone bitmap mutations. Public functions include `minix_free_block`, `minix_new_block`, `minix_count_free_blocks`, `minix_V1_raw_inode`, `minix_V2_raw_inode`, `minix_free_inode`, `minix_new_inode`, and `minix_count_free_inodes`. Internal helpers are `count_free` and `minix_clear_inode`.

## Control Flow

Block allocation scans zone bitmap buffers for the first zero bit, sets it under `bitmap_lock`, marks the bitmap buffer dirty, translates the bitmap bit to an on-disk data zone, and validates the range. Freeing a block validates the data-zone range, clears the corresponding bit, and marks the buffer dirty. Inode allocation obtains a fresh VFS inode, scans and sets an inode bitmap bit, validates the inode number, initializes owner/timestamps/private Minix fields, inserts into the inode hash, and marks it dirty. Inode freeing clears the on-disk mode/link count before clearing the bitmap bit.

## State and Persistence Behavior

Persistent state is the on-disk inode and zone bitmaps plus raw inode table blocks, updated through buffer heads and marked dirty for writeback. In-memory state includes the new VFS inode and Minix private inode data. Free counts are computed by scanning bitmap buffers rather than maintaining counters here.

## Dependencies and Integration Points

It depends on `minix.h` for superblock layout, bitmap endian helpers, inode-private data, and version constants; buffer-head IO through `sb_bread`, `mark_buffer_dirty`, and `brelse`; VFS inode allocation and ownership helpers; and Minix inode tree/truncate code through shared inode structures.

## Risks and Edge Cases

Range checks protect against freeing blocks outside the data zone and inode numbers outside the inode table. Bitmap bit indexes include reserved inode/zone offsets and are easy to miscompute. `count_free` deliberately treats bitmap words endian-insensitively for zero-bit counting. Allocation can find a bit that maps outside valid zones or inode range and returns corruption/errors. On-disk inode clearing must match v1 versus v2 inode formats.

## Test Signals

Create/delete files until ENOSPC, verify free block/inode counts, run fsck after allocation/free cycles, test v1 and v2 images, inject out-of-range inode/block numbers, run concurrent creates/unlinks to stress `bitmap_lock`, and verify dirty bitmap/inode-table buffers are written after sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/dir.c -->
# sources/distributed-fs/ceph-client/fs/minix/dir.c

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/dir.c` implements Minix directory file operations and directory-entry manipulation. It reads directory entries, finds names, adds/removes links, initializes empty directories, checks directory emptiness, updates existing links, locates `..`, and resolves inode numbers by name. The source was read as a complete 458-line file for this report.

## Important APIs, Types, and Functions

Important exported objects/functions are `minix_dir_operations`, `minix_find_entry`, `minix_add_link`, `minix_delete_entry`, `minix_make_empty`, `minix_empty_dir`, `minix_set_link`, `minix_dotdot`, and `minix_inode_by_name`. Local helpers include `minix_readdir`, `minix_last_byte`, `dir_commit_chunk`, `minix_handle_dirsync`, `dir_get_folio`, `minix_next_entry`, and `namecompare`. The code handles both `struct minix_dir_entry` and `struct minix3_dir_entry`.

## Control Flow

Directory iteration aligns `ctx->pos` to the fixed Minix directory record size, maps each folio, walks entries up to the last valid byte, chooses v1/v2 or v3 entry layout, and emits nonzero inode entries. Lookup scans folios for a matching fixed-length name. Add-link scans existing pages and one possible expansion page for an empty slot or duplicate, prepares the directory chunk, writes the name and inode, commits the chunk, updates timestamps, and optionally syncs. Delete and set-link prepare and commit one directory record. `minix_make_empty` creates `.` and `..` in the first folio. `minix_empty_dir` accepts only valid `.` and `..` entries.

## State and Persistence Behavior

Directory entries are persistent on disk through the page cache and buffer-head writeback. `dir_commit_chunk` can grow `i_size`, updates the page cache, unlocks the folio, and marks the inode dirty. Dirsync paths call `filemap_write_and_wait` and `sync_inode_metadata`. Folio mappings are transient and must be released with `folio_release_kmap` or `folio_put`.

## Dependencies and Integration Points

It depends on Minix superblock fields `s_dirsize`, `s_namelen`, and `s_version`, folio/page-cache helpers, `minix_prepare_chunk`, generic directory/file operations, and VFS namei/inode code that calls these helpers from Minix `namei.c`.

## Risks and Edge Cases

Fixed-size directory entries require strict alignment and name truncation rules. The v3 directory format has a 32-bit inode and different name offset than v1/v2. Add-link operates beyond `i_size` while holding the target folio lock. Error paths must release kmap/folio locks correctly. `namecompare` rejects longer on-disk names when the lookup name is shorter. Dirsync failures must propagate after metadata changes.

## Test Signals

Run create/unlink/rename/mkdir/rmdir/link lookup tests on Minix v1/v2/v3 images, test maximum and near-maximum name lengths, directory expansion across folios, dirsync mounts, empty-directory checks with malformed `.`/`..`, fsck after directory mutation, and fault injection in `read_mapping_folio` or `minix_prepare_chunk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/file.c -->
# sources/distributed-fs/ceph-client/fs/minix/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/minix/file.c` defines regular-file operations and inode operations for Minix files. It wires generic VFS read/write/mmap/splice behavior to Minix fsync and handles attribute changes, including truncation. The source was read as a complete 61-line file for this report.

## Important APIs, Types, and Functions

Important functions and objects are `minix_fsync`, `minix_file_operations`, local `minix_setattr`, and `minix_file_inode_operations`. File operations use `generic_file_llseek`, `generic_file_read_iter`, `generic_file_write_iter`, `generic_file_mmap_prepare`, `filemap_splice_read`, and Minix-specific `minix_fsync`. Inode operations expose `.setattr` and `minix_getattr`.

## Control Flow

`minix_fsync` delegates to `mmb_fsync` with the Minix inode metadata buffer-head list. Regular file reads/writes and mmap setup use generic VFS helpers. `minix_setattr` validates requested attributes with `setattr_prepare`, checks and applies size changes through `inode_newsize_ok`, `truncate_setsize`, and `minix_truncate`, then copies attributes and marks the inode dirty.

## State and Persistence Behavior

Persistent state includes file data blocks, inode size, inode metadata, and Minix metadata buffer heads. `fsync` flushes file data and metadata buffers. Attribute changes update in-memory inode state and mark it dirty for writeback; truncation updates block mappings through Minix truncate code.

## Dependencies and Integration Points

It depends on `minix.h`, buffer-head metadata tracking, generic VFS file operations, attribute helpers, and Minix inode/truncate/getattr support. It is linked into the Minix module by the Makefile and referenced by inode setup code.

## Risks and Edge Cases

Truncation must validate new size before changing `i_size`, then free blocks consistently through `minix_truncate`. The code uses `nop_mnt_idmap`, so idmapped mount semantics are not applied here. Fsync correctness depends on `i_metadata_bhs` tracking all metadata buffers that need flushing.

## Test Signals

Test reads, writes, mmap setup, splice reads, fsync after data and metadata updates, truncate grow/shrink, setattr permission failures, timestamp/size changes, crash/fsck after fsync, and Minix regular-file operations on v1/v2/v3 images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/file.c -->
