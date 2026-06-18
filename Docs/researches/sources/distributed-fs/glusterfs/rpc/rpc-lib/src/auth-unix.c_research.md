## sources/distributed-fs/glusterfs/rpc/rpc-lib/src/auth-unix.c

Purpose: implements server-side `AUTH_UNIX` credential decoding and request identity population.

Important APIs: `auth_unix_authenticate` decodes `authunix_parms` using `xdr_to_auth_unix_cred`, places auxiliary groups in `req->auxgidsmall`, and assigns `req->uid`, `req->gid`, and `req->auxgidcount`. `rpcsvc_auth_unix_init` returns a static `rpcsvc_auth_t` with auth number `AUTH_UNIX`.

Control flow: request init is a no-op. Authentication rejects NULL requests, decodes machine name and credential fields, logs identity details, and accepts on successful decode.

State and persistence: all state is per request. No heap allocation is performed here; aux gids use the request's embedded small array.

Dependencies and integration: registered by `rpcsvc_auth.c` and depends on `xdr-rpc.h` helpers. It is enabled by default unless `rpc-auth.auth-unix` is disabled.

Risks: classic UNIX AUTH credentials are client-asserted. Without trusted network or transport controls, they are not strong authentication. The fixed small auxgid storage depends on decode helper behavior to avoid overflow.

Test signals: valid/invalid XDR credential decode tests, aux group boundary tests, and service authorization tests involving UNIX uid/gid.
