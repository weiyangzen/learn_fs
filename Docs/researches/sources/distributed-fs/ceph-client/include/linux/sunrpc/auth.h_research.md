# sources/distributed-fs/ceph-client/include/linux/sunrpc/auth.h

Purpose: declares the client-side SUNRPC authentication framework, credential cache objects, auth flavor operations, and transmit/receive wrapping hooks.

Important APIs and types: `struct auth_cred` describes kernel credentials plus optional machine principal. `struct rpc_cred` is refcounted, hash/LRU-linked, RCU-freed credential state with flags such as `RPCAUTH_CRED_UPTODATE` and `RPCAUTH_CRED_NEGATIVE`. `struct rpc_auth` represents an auth handle with slack sizes, flavor, operations, refcount, and credential cache. `struct rpc_authops` creates/destroys auth modules and maps GSS info/flavors. `struct rpc_credops` initializes, marshals, refreshes, validates, wraps, unwraps, and stringifies credentials.

Control flow: RPC client creation calls `rpcauth_create()`, tasks look up credentials via `rpcauth_lookupcred()` or the cache, marshal credentials into `xdr_stream`, refresh stale credentials, and validate reply verifiers. GSS/privacy flavors can wrap requests and unwrap responses.

State and persistence: state is in-memory and refcounted/RCU-managed: auth modules, auth handles, credential cache entries, flags, expiry times, and kernel `cred` references.

Dependencies and integration points: integrates with `rpc_task`, XDR streams, message protocol constants, modules, RCU, uid/gid credentials, UTS nodename sizing, and GSS flavor mapping.

Risks and test signals: risks include stale or negative credentials, refcount/RCU lifetime bugs, auth slack underestimation, async lookup failures, and reencode requirements after refresh. Test with AUTH_NULL, AUTH_UNIX, TLS auth, RPCSEC_GSS, credential expiry, cache pressure, and KASAN/RCU debug.
