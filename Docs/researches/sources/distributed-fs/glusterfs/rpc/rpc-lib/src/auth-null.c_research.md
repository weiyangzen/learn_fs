## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/auth-null.c

Purpose: implements the server-side `AUTH_NULL` handler.

Important APIs: `auth_null_request_init` is a no-op, `auth_null_authenticate` always returns `RPCSVC_AUTH_ACCEPT`, and `rpcsvc_auth_null_init` returns a static `rpcsvc_auth_t` with auth number `AUTH_NULL`.

Control flow: initialization does not allocate state. When selected for a request, authentication immediately succeeds.

State and persistence: no mutable module state and no per-request fields are populated by this handler.

Dependencies and integration: registered by `rpcsvc_auth.c`, used as the fallback handler when an incoming credential flavour has no enabled handler. It also becomes enabled by default unless disabled through `rpc-auth.auth-null`.

Risks: this handler intentionally provides no identity validation. Any service path that allows `AUTH_NULL` for operations requiring identity must rely on external authorization or accept anonymous access. Because `rpcsvc_auth_get_handler` falls back to `AUTH_NULL`, deployments must be careful about disabled or missing stronger auth handlers.

Test signals: handler registration, fallback behavior, and service-specific min-auth enforcement tests.
