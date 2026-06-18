## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/rpcsvc-auth.c

Purpose: orchestrates server-side RPC authentication scheme registration, initialization, request credential setup, authentication dispatch, and auth-related service options.

Important APIs: `rpcsvc_auth_add_initer`, `rpcsvc_auth_add_initers`, `rpcsvc_auth_init_auth`, `rpcsvc_auth_init_auths`, `rpcsvc_auth_init`, `rpcsvc_auth_reconf`, `rpcsvc_auth_request_init`, `rpcsvc_authenticate`, `rpcsvc_auth_array`, and `rpcsvc_auth_unix_auxgids`. Option helpers set address name lookup, insecure-port allowance, root squash, and all squash.

Control flow: initialization sets service auth options, registers initers for `auth-glusterfs-v3`, `auth-unix`, and `auth-null`, defaults those schemes to on when not configured, and initializes each handler. Per request, `rpcsvc_auth_request_init` reads credential and verifier flavours/lengths from the RPC call, finds a handler, runs optional request init, and resets auxgid pointers. `rpcsvc_authenticate` checks minimal auth strength placeholder, gets the handler, and calls its authenticate op. If no exact handler exists, lookup falls back to `AUTH_NULL`.

State and persistence: mutates `rpcsvc_t`: auth scheme list, option dict defaults, squashing flags, anonymous uid/gid, insecure allowance, and address lookup flag. Per-request state includes credential metadata, auxgid storage pointers, uid/gid fields, and auth errors.

Dependencies and integration: depends on auth modules (`auth-null`, `auth-unix`, `auth-glusterfs`), dict options, RPC call parsing helpers, and optional GNFS code for auth arrays and unix auxgids.

Risks: fallback to `AUTH_NULL` can weaken behavior when a stronger handler is unavailable unless program-level minauth is enforced. The minauth check is currently a FIXME with hardcoded zero. Defaults enable null, unix, and glusterfs auth unless explicitly disabled. Squash settings are global service flags that downstream actors must honor.

Test signals: initialization defaults, disabling schemes, fallback behavior, request credential parsing, root/all squash option parsing, reconfigure tests, and GNFS auth array generation.
