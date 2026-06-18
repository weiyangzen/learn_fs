# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_upcall.c

## Purpose
`gss_rpc_upcall.c` implements the kernel-side RPC client used by server-side SUNRPC GSS auth to talk to `gssproxy` over a local Unix-domain transport. Its main public service performs an `ACCEPT_SEC_CONTEXT` gssproxy call and converts returned handles, tokens, mechanism OID, and credentials into kernel structures.

## Important APIs, Types, and Functions
The file defines gssproxy program constants, procedure numbers, `gssp_procedures[]`, and `gssp_program`. Client lifecycle functions are `gssp_rpc_create()`, `init_gssp_clnt()`, `set_gssp_clnt()`, `clear_gssp_clnt()`, and `get_gssp_clnt()`. RPC execution uses `gssp_call()`. Receive-page helpers are `gssp_alloc_receive_pages()` and `gssp_free_receive_pages()`. Principal helpers are `gssp_stringify()` and `gssp_hostbased_service()`. The main public function is `gssp_accept_sec_context_upcall()`, with cleanup by `gssp_free_upcall_data()`.

## Control Flow
`set_gssp_clnt()` creates an AF_LOCAL RPC client connected to `/var/run/gssproxy.sock` with null auth and no idle timeout, then stores it under the per-net `gssp_lock`. `gssp_accept_sec_context_upcall()` builds XDR argument/result structs, optionally includes an input context handle, preallocates receive pages sized for group data, synchronously calls gssproxy, then copies major/minor status and output fields. If credential options are returned, it steals a `svc_cred`, stringifies source and target principals, and converts service principals from `service/host@REALM` to host-based `service@host`.

## State and Persistence
The persistent state is `sunrpc_net->gssp_clnt`, protected by `gssp_lock` and refcounted while calls are in progress. Per-call state includes allocated receive pages, output handle/token buffers, copied mechanism OID, and optional service credentials. `gssp_free_upcall_data()` releases all caller-owned outputs after use.

## Dependencies and Integration Points
It depends on SUNRPC local transports, generated gssproxy XDR routines from `gss_rpc_xdr.c/h`, per-net SUNRPC state, server auth credentials, Unix socket addressing, and gssproxy availability. It integrates with server-side RPCSEC_GSS acceptor paths rather than the client `rpc.gssd` pipefs path.

## Risks and Edge Cases
Connection errors are normalized: protocol unsupported becomes `-EINVAL`, connection refusal/timeouts/not connected become `-EAGAIN`, and interrupted calls can become `-EINTR`. Receive pages are sized from `NGROUPS_MAX`, so group-heavy credentials stress allocation. The options decoder currently expects only one credential option and would need iteration for future options. Principal conversion mutates copied strings and drops non-service principals.

## Test Signals
Integration tests with gssproxy are the main signal: setup/clear per-net client, accept a context, verify returned creds/principals/tokens, and exercise connection failure mappings. XDR encode/decode correctness is coupled to `gss_rpc_xdr` tests or runtime gssproxy interoperability.
