# sources/distributed-fs/ceph-client/net/sunrpc/svcauth.c

## Purpose
`svcauth.c` provides the generic server-side authentication dispatch layer for SUNRPC. It maps incoming RPC auth flavors to `auth_ops`, drives accept/set-client/release operations, supports dynamic auth flavor registration, maps local client credentials to service credentials, and manages shared `auth_domain` objects.

## Important APIs, Types, And Functions
Important APIs include `svc_authenticate()`, `svc_set_client()`, `svc_authorise()`, `svc_auth_register()`, `svc_auth_unregister()`, `svc_auth_flavor()`, `svcauth_map_clnt_to_svc_cred_local()`, `auth_domain_put()`, `auth_domain_lookup()`, `auth_domain_find()`, and `auth_domain_cleanup()`. The global `authtab` starts with NULL, UNIX, and TLS authenticators.

## Control Flow
`svc_authenticate()` decodes the credential flavor from the request stream, obtains the registered auth ops under RCU with a module reference, initializes `rq_cred`, stores `rq_authop`, and calls the flavor's `accept()`. Program dispatch can later call `svc_set_client()`, which delegates domain/client selection to the active flavor. `svc_authorise()` clears `rq_authop`, calls flavor release to emit/finalize verifiers and drop request resources, and releases the module reference. Auth domains are looked up by hashed name with RCU and kref protection; final put removes the domain and invokes the flavor's release method under the lock handoff.

## State And Persistence
Persistent state includes the RCU-protected `authtab` array and the global auth-domain hash table protected by `auth_domain_lock`. Per-request state includes auth status, auth slack, selected auth ops, service credentials, and optional auth domain/client. Local credential mapping creates transient `svc_cred` values and group-info references.

## Dependencies And Integration Points
The file integrates with `svc.c` request processing, `svcauth_unix.c` built-in auth operations, optional loadable auth flavors, RPC XDR opaque auth decoding, Linux credential and user namespace translation, module refcounts, RCU, krefs, and tracepoints.

## Risks And Edge Cases
Unknown or out-of-range auth flavors must produce proper RPC auth errors without leaking module refs. `svc_authorise()` must be called on all request paths after successful `svc_authenticate()` to release credentials and auth ops. `svc_auth_unregister()` removes pointers with RCU assignment, so users need grace-period-safe lifetime. `auth_domain_cleanup()` can only warn about leaks because domain release callbacks may live in unloaded modules.

## Test Signals
Useful tests include bad credential flavor, malformed credential stream, NULL/UNIX/TLS auth dispatch, dynamic auth flavor registration conflicts/unregistration, program-level `svc_set_client()` behavior, local credential user-namespace mapping, auth domain lookup/refcount/release, and leak warnings on module unload.
