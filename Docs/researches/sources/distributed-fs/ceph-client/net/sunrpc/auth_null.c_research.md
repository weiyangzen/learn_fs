# sources/distributed-fs/ceph-client/net/sunrpc/auth_null.c

Purpose: implements the AUTH_NULL client authentication flavor for SUNRPC. It supplies a singleton auth handle and singleton credential that marshal empty credential and verifier bodies and accept only empty NULL reply verifiers.

Important APIs/types/functions: exported operation table is `authnull_ops`; the static credential ops table is `null_credops`. Core functions are `nul_create`, `nul_destroy`, `nul_lookup_cred`, `nul_destroy_cred`, `nul_match`, `nul_marshal`, `nul_refresh`, and `nul_validate`. State objects are static `null_auth` and `null_cred`.

Control flow: client creation increments the singleton auth refcount and returns `null_auth`. Credential lookup returns a reference to `null_cred`; matching always succeeds. Request marshalling reserves four XDR words for AUTH_NULL credential and AUTH_NULL verifier, both with zero length. Refresh simply sets `RPCAUTH_CRED_UPTODATE`. Reply validation decodes two words and requires flavor `rpc_auth_null` and length zero.

State and persistence behavior: all state is process-global static kernel memory. There is no per-user credential allocation, no cache, and no persistent state. Destroy hooks are no-ops because the singleton objects are never dynamically freed.

Dependencies/integration points: plugs into the generic `rpcauth` framework through `struct rpc_authops` and `struct rpc_credops`. It uses `rpcauth_wrap_req_encode` and `rpcauth_unwrap_resp_decode` for pass-through request/response body handling.

Risks: because `nul_match()` always returns true, any caller selecting AUTH_NULL gets no identity isolation. The reply verifier parser is intentionally strict; servers returning non-empty verifiers fail validation. Singleton refcounts must remain initialized high enough for static lifetime assumptions.

Test signals: send NULL and ordinary RPC calls using AUTH_NULL and verify the credential/verifier fields are zero-length AUTH_NULL. Negative tests should feed non-NULL or nonzero reply verifiers and expect `-EIO`. Refcount/lifetime tests should repeatedly create and release AUTH_NULL clients.
