# sources/distributed-fs/ceph-client/net/sunrpc/auth.c

## Purpose
`auth.c` is the generic RPC client authentication dispatcher. It owns registration of auth flavors, creation and replacement of per-client `rpc_auth` instances, generic credential-cache management, credential binding to RPC tasks, and the dispatch points for marshalling, refresh, verifier validation, request wrapping, and response unwrapping. RPCSEC_GSS plugs into this file through `rpcauth_register(&authgss_ops)` as flavor `RPC_AUTH_GSS`.

## Important APIs, Types, and Functions
The private `struct rpc_cred_cache` stores an RCU-visible hash table plus a spinlock and hash width. `auth_flavors[]` is an RCU-protected flavor-to-`rpc_authops` registry preloaded with NULL, UNIX, and TLS auth ops. `rpcauth_register()` and `rpcauth_unregister()` install or remove authops with `cmpxchg`; `rpcauth_get_authops()` handles module autoload via `request_module("rpc-auth-%u")` and module refcounting. Public helpers include `rpcauth_create()`, `rpcauth_release()`, `rpcauth_init_credcache()`, `rpcauth_destroy_credcache()`, `rpcauth_lookup_credcache()`, `rpcauth_lookupcred()`, `rpcauth_init_cred()`, `put_rpccred()`, `rpcauth_marshcred()`, `rpcauth_refreshcred()`, and wrap/unwrap/verifier dispatcher functions. `rpc_machine_cred()` exposes a static machine credential marker used by credential binding.

## Control Flow
Client setup calls `rpcauth_create()`, which maps GSS pseudoflavors to `RPC_AUTH_GSS`, gets the authops, calls `ops->create()`, and swaps `clnt->cl_auth`. Task execution calls `rpcauth_refreshcred()`: if no request credential is bound, `rpcauth_bindcred()` chooses an operation-specific cred, a process cred, a machine principal cred, a root fallback, null creds, or a newly looked-up current cred. Encoding then enters the per-credential ops: marshal credentials, wrap procedure args, validate the reply verifier, and unwrap/decode the response.

## State and Persistence
Credential cache entries are hash-linked with `RPCAUTH_CRED_HASHED` and carry one extra reference for hash-table residency. Unused up-to-date cached creds are placed on the global `cred_unused` LRU, counted by `number_cred_unused`, and reclaimed by a shrinker or by `auth_max_cred_cachesize` enforcement. Expired creds observe a 60-second GC moratorium based on `cr_expire`. Authops registration persists until module unregister; auth instances persist by `au_count`.

## Dependencies and Integration Points
The file depends on Linux credentials, RCU, refcounts, spinlocks, shrinkers, XDR streams, SUNRPC client/task/request types, auth modules, tracepoints, and module autoloading. It integrates with auth-specific ops from `auth_null`, `auth_unix`, TLS, and RPCSEC_GSS. It also integrates with transport request sequence tracking via `xprt_rqst_add_seqno()` indirectly through auth-specific marshalers.

## Risks and Edge Cases
Concurrency hinges on lock ordering between `rpc_credcache_lock` and per-cache locks. `put_rpccred()` has race-breaking checks when moving creds to the LRU or unhashed state. A malformed `auth_hashtable_size` module parameter is rejected unless it maps to 4..16384 buckets. `pseudoflavor_to_flavor()` treats values greater than `RPC_AUTH_MAXFLAVOR` as GSS, which is intentional for pseudoflavors but makes GSS module availability critical. Shrinker scanning avoids sleeping in the loop and refuses non-`GFP_KERNEL` reclaim.

## Test Signals
There are no direct unit tests in this file. Behavior is exercised by SUNRPC auth users, RPCSEC_GSS KUnit tests for mechanism pieces, and integration tests that perform authenticated RPC calls. Useful probes are SUNRPC tracepoints and cache-pressure tests that verify credential reuse, expiry, invalidation, and request re-encoding.
