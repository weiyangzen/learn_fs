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
