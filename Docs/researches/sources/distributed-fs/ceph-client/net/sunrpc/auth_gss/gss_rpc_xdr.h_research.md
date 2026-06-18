# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_xdr.h

Purpose: declares the subset of the GSS proxy RPC/XDR model used by the kernel server-side RPCSEC_GSS implementation. It defines protocol-facing GSSX objects, the kernel-only page-backed input token carrier, argument/result structures for `accept_sec_context`, and size estimates used by SUNRPC procedure tables.

Important APIs/types/functions: aliases `gssx_buffer`, `utf8string`, and `gssx_OID` map to `struct xdr_netobj`. Protocol structures include `gssx_option`, `gssx_status`, `gssx_call_ctx`, `gssx_name`, `gssx_cred`, `gssx_ctx`, `gssx_cb`, `gssx_arg_accept_sec_context`, and `gssx_res_accept_sec_context`. The only implemented RPC procedures are declared as `gssx_enc_accept_sec_context()` and `gssx_dec_accept_sec_context()`; all other GSSX procedure encoder/decoder macros are set to `NULL`, with argument/result sizes set to zero.

Control flow: consumers build a `gssx_arg_accept_sec_context` with optional context and credential handles, a `gssp_in_token`, optional channel bindings, output pages, and option arrays. `gss_rpc_xdr.c` encodes it and decodes into `gssx_res_accept_sec_context`, filling status, optional returned context, optional output token, and returned options such as Linux credentials.

State and persistence behavior: the header owns no state. It defines memory ownership contracts implicitly: many fields are `xdr_netobj` buffers whose data is allocated or provided by callers, and `gssp_in_token` uses page refs for large input data. Size macros are compile-time estimates, not runtime limits for all objects.

Dependencies/integration points: depends on SUNRPC XDR, client, and socket transport headers. The constants `LUCID_OPTION`, `LUCID_VALUE`, `CREDS_OPTION`, and `CREDS_VALUE` define the negotiation strings shared with gssproxy. The header is consumed by both the GSS proxy upcall client and server auth code.

Risks: the structure set mirrors a protocol that is larger than the kernel-supported subset. Unsupported procedures are represented as `NULL`, so any procedure table wiring must not invoke them. The size macros are deliberately approximate and include arbitrary maximums for status strings, principals, tokens, and credentials; underestimation can produce buffer sizing failures, while overestimation increases allocation pressure.

Test signals: build coverage should include configurations with and without SUNRPC debug. Procedure table tests should confirm only `accept_sec_context` is wired. Runtime context creation through gssproxy is the main integration signal that size constants, optional handles, and credential option names match the userspace daemon.
