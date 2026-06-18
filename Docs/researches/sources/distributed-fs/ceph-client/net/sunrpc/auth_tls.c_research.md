# sources/distributed-fs/ceph-client/net/sunrpc/auth_tls.c

Purpose: implements the special AUTH_TLS client credential used only to probe whether a remote peer supports RPC-over-TLS STARTTLS negotiation. It behaves like a singleton credential flavor with a custom `.ping` operation that sends a probe and validates the STARTTLS response token.

Important APIs/types/functions: exported auth operation table is `authtls_ops`, with `.ping = tls_probe`. Static objects include `tls_auth`, `tls_cred`, `rpcproc_tls_probe`, and `rpc_tls_probe_ops`. Core functions are `tls_probe`, `tls_create`, `tls_lookup_cred`, `tls_marshal`, `tls_refresh`, and `tls_validate`.

Control flow: when an RPC client using AUTH_TLS is pinged, `tls_probe()` runs a soft, soft-connection RPC task with `tls_cred`. The call prepare hook clears `RPC_TASK_NO_RETRANS_TIMEOUT` and starts the normal RPC call FSM. Request marshalling emits an AUTH_TLS credential with zero body and an AUTH_NULL verifier. Reply validation requires an AUTH_NULL verifier followed by an opaque `STARTTLS` token of exactly eight bytes.

State and persistence behavior: state is limited to static singleton auth and credential objects plus immutable `STARTTLS` constants. No per-principal credential or persistent storage exists. Probe task state is normal transient `rpc_task` state.

Dependencies/integration points: integrates with `rpc_create()`/`rpc_ping()` through the authops `.ping` hook, the generic rpc task scheduler, and RPC-over-TLS transport setup code that interprets a successful probe as STARTTLS support. It uses the same pass-through wrap/unwrap helpers as AUTH_NULL.

Risks: `authtls_ops.au_name` is `"NULL"` despite flavor `RPC_AUTH_TLS`, which could confuse diagnostics. The validation path is intentionally narrow; any server returning a different verifier flavor or token length is treated as `-EPROTONOSUPPORT`. The empty procedure encoder/decoder assumes the STARTTLS signal lives in the verifier stream, not in procedure payload.

Test signals: probe a server that supports RPC-over-TLS and confirm `STARTTLS` validation succeeds; test servers that omit the token, return wrong length, wrong flavor, or wrong bytes and expect `-EPROTONOSUPPORT` or `-EIO`. Confirm probe tasks are soft and do not retain no-retrans-timeout behavior.
