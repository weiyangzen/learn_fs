# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/auth_gss.c

## Purpose
`auth_gss.c` implements client-side RPCSEC_GSS for SUNRPC. It creates GSS auth handles, manages user-space `rpc.gssd` upcalls through `rpc_pipefs`, imports GSS security contexts, maintains GSS credentials and context references, constructs RPCSEC_GSS credentials/verifiers, and wraps or unwraps RPC payloads for none, integrity, and privacy services.

## Important APIs, Types, and Functions
Key private types are `struct gss_auth`, `struct gss_pipe`, `struct gss_upcall_msg`, `struct gss_cred`, and `struct gss_cl_ctx`. Important authops and credops are `authgss_ops`, `gss_credops`, and `gss_nullops`. Upcall functions include `gss_alloc_msg()`, `gss_add_msg()`, `gss_setup_upcall()`, `gss_create_upcall()`, `gss_refresh_upcall()`, `gss_pipe_downcall()`, `gss_v0_upcall()`, and `gss_v1_upcall()`. Credential/context functions include `gss_create_new()`, `gss_create_hashed()`, `gss_destroy()`, `gss_create_cred()`, `gss_cred_init()`, `gss_match()`, `gss_destroy_cred()`, and `gss_send_destroy_context()`. Wire operations are `gss_marshal()`, `gss_validate()`, `gss_wrap_req()`, `gss_unwrap_resp()`, and service-specific wrap/unwrap helpers.

## Control Flow
Module init registers `RPC_AUTH_GSS`, initializes server-side GSS support, and registers per-net operations. Auth creation resolves the Kerberos mechanism by pseudoflavor, validates the service, requires `gssd_running()`, initializes the generic cred cache, and creates two upcall pipes: new text pipe `gssd` and legacy mechanism-named pipe such as `krb5`. Credential lookup creates a `RPCAUTH_CRED_NEW` credential so refresh forces an upcall. The downcall payload is parsed by `gss_fill_context()`: lifetime, sequence window, opaque wire context, imported mechanism context, and optional acceptor name. After context installation, request marshalling reserves credential fields, allocates/increments RPCSEC_GSS sequence numbers, computes a MIC over the RPC header credential bytes, and writes the verifier. Payload wrapping either passes data unchanged, adds integrity framing plus MIC, or allocates scratch pages and calls mechanism privacy wrapping. Reply processing validates the verifier MIC, unwraps integrity/privacy data, checks reply sequence numbers, and then calls the procedure decoder.

## State and Persistence
`gss_auth` objects are cached in `gss_auth_hash_table` by common parent RPC client, flavor, and target name. Contexts are RCU-published through `gc_ctx`, refcounted, and finally released via `call_rcu()`. `pipe_version` in `sunrpc_net` tracks whether legacy or new upcall protocol is active while a pipe is open. Upcall messages are deduplicated per pipe, UID, and service in `pipe->in_downcall`, with wait queues for synchronous and asynchronous refresh paths. Credentials carry negative-cache state after `-EKEYEXPIRED` to delay retries.

## Dependencies and Integration Points
This file depends on generic RPC auth (`auth.c`), GSS mechanism switching (`gss_mech_get_by_pseudoflavor()`, `gss_import_sec_context()`, `gss_get_mic()`, `gss_wrap()`, `gss_unwrap()`), `rpc_pipefs`, per-net SUNRPC state, server GSS init/shutdown, XDR buffers, kernel credentials, RCU, workqueues, wait queues, and tracepoints. User-space `rpc.gssd` is a required runtime integration for acquiring contexts.

## Risks and Edge Cases
The code is concurrency-heavy: upcall deduplication, context replacement, pipe version selection, and credential refresh all rely on careful locking and refcounting. If no gssd pipe is open, refresh can sleep and retry; create-time upcalls convert sustained absence into `-EACCES`. Buffer slack is security-critical for privacy and integrity services, with compile-time checks against Kerberos maximum slack. Sequence numbers can expire at `MAXSEQ`; retransmit re-encoding uses a window-aware compare to avoid reusing stale sequence numbers. Downcall parsing treats gssd error windows specially and maps most import failures to retry-oriented errors.

## Test Signals
Direct tests are mostly integration-level: NFS/RPC calls using krb5, krb5i, and krb5p; gssd availability/failure paths; credential expiration; retransmission re-encoding; and server destroy-context calls. Tracepoints under `rpcgss` expose context import, upcall, MIC, wrap, unwrap, slack update, bad sequence, and reencode decisions.
