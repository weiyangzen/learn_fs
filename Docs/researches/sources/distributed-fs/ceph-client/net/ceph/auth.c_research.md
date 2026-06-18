# sources/distributed-fs/ceph-client/net/ceph/auth.c

## Purpose
Implements the generic Ceph authentication client dispatcher for monitor auth and messenger v2 authentication. It negotiates protocol selection, serializes auth requests, decodes replies, owns the auth mutex, and delegates protocol-specific behavior to `auth_none` or CephX ops.

## Important APIs, Types, and Functions
Core APIs include `ceph_auth_init()`, `ceph_auth_destroy()`, `ceph_auth_reset()`, `ceph_auth_build_hello()`, `ceph_handle_auth_reply()`, `ceph_build_auth()`, `ceph_auth_is_authenticated()`, `__ceph_auth_get_authorizer()`, `ceph_auth_get_authorizer()`, `ceph_auth_add_authorizer_challenge()`, `ceph_auth_verify_authorizer_reply()`, `ceph_auth_handle_reply_more()`, `ceph_auth_handle_reply_done()`, `ceph_auth_handle_bad_method()`, `ceph_auth_handle_svc_reply_more()`, `ceph_auth_handle_svc_reply_done()`, and `ceph_auth_handle_bad_authorizer()`. It manipulates `struct ceph_auth_client`, `struct ceph_auth_client_ops`, and `struct ceph_auth_handshake`.

## Control Flow
`ceph_auth_init()` creates a negotiating client with name, optional key, and preferred/fallback connection modes. Monitor v1 auth begins with `ceph_auth_build_hello()`, which encodes supported protocols and entity name. `ceph_handle_auth_reply()` decodes monitor replies, initializes or switches protocol handlers during negotiation, sets global id through the backend, and builds a follow-up request on `-EAGAIN`. `ceph_build_auth()` emits later requests if the selected backend says authentication is needed.

For msgr2, `ceph_auth_get_request()` initializes the expected protocol directly from key presence, encodes connection modes, entity name, and global id. Reply-more/done functions delegate backend payload handling. Service authorization uses `__ceph_auth_get_authorizer()` to create or update authorizers, then wraps authorizer length/mode metadata. Bad-method handlers decide whether errors are retryable with different auth settings or fatal.

## State and Persistence
`struct ceph_auth_client` holds global id, selected protocol, backend private state, key pointer, wanted service keys, and mode preferences. All mutable auth state is protected by `ac->mutex`. There is no disk persistence; tickets and secrets live in backend memory and are destroyed with the auth client.

## Dependencies and Integration Points
Depends on Ceph protocol encoders/decoders, monitor request headers, `ceph_auth_none_init()`, `ceph_x_init()`, messenger connection modes, and exported helpers used by monitor, OSD, MDS, and messenger code. The service-authorizer callbacks integrate with msgr2 challenge/reply and message-signature hooks.

## Risks
Protocol switching during negotiation destroys existing backend state; callers must not hold stale authorizers across reset/invalidation. Buffer encoding uses explicit bounds but relies on correct caller-provided lengths. `ceph_auth_get_request()` warns if protocol and key-derived expectation diverge. Bad-method handling must match server-allowed protocol/mode arrays or clients can retry when they should fail. Global-id changes are logged but still assigned.

## Test Signals
Exercise auth-none monitor flow, CephX multi-step monitor flow, msgr2 request/reply-more/reply-done, backend `-EAGAIN` follow-up generation, bad method with disallowed protocol or mode, authorizer create/update/invalidate paths, malformed reply bounds, global-id assignment, and concurrent callers under lockdep.
