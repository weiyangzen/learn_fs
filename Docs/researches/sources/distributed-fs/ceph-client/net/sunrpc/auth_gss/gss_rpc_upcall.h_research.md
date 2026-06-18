# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_upcall.h

## Purpose
This header declares the gssproxy RPC upcall interface used by SUNRPC server-side GSS auth code. It exposes the per-call data carrier and lifecycle functions for the per-network gssproxy RPC client.

## Important APIs, Types, and Functions
`struct gssp_upcall_data` carries input context handle, input token, output handle, output token, mechanism OID, service credentials, a `found_creds` flag, and major/minor GSS status values. Public functions are `gssp_accept_sec_context_upcall()`, `gssp_free_upcall_data()`, `init_gssp_clnt()`, `set_gssp_clnt()`, and `clear_gssp_clnt()`.

## Control Flow
Callers initialize `gssp_upcall_data` with an input token and optional input handle, call `gssp_accept_sec_context_upcall()`, inspect status and output fields, then call `gssp_free_upcall_data()` to release allocated handles, tokens, and credentials. Per-net setup calls `init_gssp_clnt()` and `set_gssp_clnt()`; teardown calls `clear_gssp_clnt()`.

## State and Persistence
The struct contains caller-visible ownership of dynamically allocated netobjects and `svc_cred` internals after a successful or partially successful call. Per-net persistent client state lives in `sunrpc_net`, not in the header.

## Dependencies and Integration Points
It includes public GSS API and auth headers, gssproxy XDR definitions, and SUNRPC net namespace state. It is consumed by server-side GSS authentication code that needs gssproxy to accept security contexts.

## Risks and Edge Cases
The ownership contract is important: output fields can be populated even when the RPC returns an error because the implementation fetches data for cleanup. Callers must use `gssp_free_upcall_data()` consistently. Mechanism OID storage is fixed by `rpcsec_gss_oid` storage in the struct, so oversized OIDs must be rejected by XDR handling.

## Test Signals
Compile-time users validate the header contract. Runtime tests should verify output cleanup after success, partial failure, and no-credential responses.
