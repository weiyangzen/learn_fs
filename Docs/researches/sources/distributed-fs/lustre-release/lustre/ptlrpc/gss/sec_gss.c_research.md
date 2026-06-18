# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/sec_gss.c

## Purpose
`sec_gss.c` is the main Lustre PTLRPC RPCSEC_GSS security policy implementation. It formats and verifies GSS wire headers, signs and verifies integrity-protected messages, wraps and unwraps privacy-protected messages, manages client and server GSS context lifetimes, enforces sequence replay windows, allocates/enlarges secure request and reply buffers, handles server-side request admission, and initializes all GSS mechanisms and policy support.

## Important APIs, types, and functions
- Wire helpers: `gss_header_swabber()`, `gss_swab_header()`, `gss_mech_payload()`, `gss_sign_msg()`, `gss_verify_msg()`, and `gss_unseal_msg()`.
- Client context lifecycle: `cli_ctx_expire()`, `cli_ctx_check_death()`, `gss_cli_ctx_uptodate()`, `gss_cli_ctx_finalize()`, `gss_cli_ctx_init_common()`, and `gss_cli_ctx_fini_common()`.
- Sequence protection: `gss_do_check_seq()` and `gss_check_seq_num()` implement main and back replay windows.
- Client request/reply operations: `gss_cli_ctx_sign()`, `gss_cli_ctx_verify()`, `gss_cli_ctx_seal()`, `gss_cli_ctx_unseal()`, and `gss_cli_ctx_handle_err_notify()`.
- Security object helpers: `gss_sec_create_common()`, `gss_sec_destroy_common()`, `gss_sec_kill()`, `gss_sec_install_rctx()`, and `gss_copy_rvc_cli_ctx()`.
- Buffer APIs: `gss_alloc_reqbuf()`, `gss_free_reqbuf()`, `gss_alloc_repbuf()`, `gss_free_repbuf()`, and `gss_enlarge_reqbuf()`.
- Server operations: `gss_svc_accept()`, `gss_svc_handle_init()`, `gss_svc_handle_data()`, `gss_svc_handle_destroy()`, `gss_svc_verify_request()`, `gss_svc_unseal_request()`, `gss_svc_alloc_rs()`, `gss_svc_authorize()`, `gss_svc_free_rs()`, `gss_svc_invalidate_ctx()`, and `gss_pack_err_notify()`.
- Module lifecycle: `sptlrpc_gss_init()` and `sptlrpc_gss_exit()`.

## Control flow
On the client side, request allocation chooses a layout from the negotiated service: NULL/AUTH/INTG use an outer GSS header, embedded Lustre message, optional user and bulk descriptors, and optional MIC; PRIV uses a clear inner Lustre message plus an encrypted outer token. `gss_cli_ctx_sign()` fills a GSS header and MIC for non-private traffic, incrementing the context sequence and repacking if the sequence falls too far behind concurrent sends. `gss_cli_ctx_seal()` wraps the clear message into a privacy token. Replies are verified by `gss_cli_ctx_verify()` for integrity modes or unwrapped by `gss_cli_ctx_unseal()` for privacy. Server GSS error notifications can expire and replace dead client contexts to recover from server reboot or stale handles.

On the server side, `gss_svc_accept()` decodes the GSS header, allocates `gss_svc_reqctx`, saves the wire context, restores byte order for MIC coverage, and dispatches by `gh_proc`. INIT requests are parsed by `gss_svc_handle_init()` and delegated to `gss_svc_upcall_handle_init()`. DATA requests find an established service context, then verify MIC or unwrap privacy data, unpack user/bulk descriptors, and set request pointers. DESTROY requests verify with INTG service and invalidate the context. Reply allocation and authorization mirror the selected service: `gss_svc_sign()` signs integrity replies, while `gss_svc_seal()` wraps privacy replies.

The recovery-sensitive sequence algorithm uses phase 0 before integrity verification to reject obvious replays without advancing the window, phase 1 after verification to commit main-window sequence numbers, and phase 2 to allow a limited back window for requests that fell behind during expensive verification or unwrap processing.

## State and persistence behavior
The file keeps early-reply offset caches in `gss_at_reply_off_integ` and `gss_at_reply_off_priv`. Client contexts hold GSS mechanism contexts, handles, service handles, sequence counters, expiry times, flags, request lists, and generation/connection counters. Service request contexts carry a policy reference and refcount; reply states hold an extra reference until freed. Sequence windows live in the service context and are protected by spinlocks. Security objects hold imports, mechanism references, nodemap names, flavor, garbage-collection interval, and reverse-context state. All state is in-memory and reconstructed through GSS upcalls, reconnect, or reverse-context copy.

## Dependencies and integration points
`sec_gss.c` sits between PTLRPC core, Lustre message packing, sptlrpc policy registration, GSS mechanisms (`null`, Kerberos, and shared-key), keyring/upcall code, bulk security descriptors, nodemap identity, OBD import/export state, and adaptive timeout early replies. It calls into `gss_svc_upcall.c` for service-context lookup/install/destroy and into `lproc_gss.c` statistics for out-of-sequence tracking. Module init orders tunables, client upcall, service upcall, mechanisms, and keyring so the registered policy is usable immediately.

## Risks
- Message layout calculations must stay synchronized across allocation, enlargement, signing, sealing, verifying, and reply authorization.
- The sequence replay algorithm is intentionally permissive for delayed valid requests; mistakes can either reject legitimate traffic under load or allow replay.
- Error-notify handling can trigger context replacement and resend; wrong conditions could loop or hide real authorization failures.
- Privacy paths copy decrypted data back into the incoming Lustre message buffer and assume output fits the original buffer.
- Request enlargement mutates `rq_reqmsg` while replay traversals can inspect requests; the code uses import locking as a narrow race workaround.
- Reverse context cleanup deliberately avoids some final RPCs and must not destroy a callback context still needed for recovery.

## Test signals
Strong coverage includes NULL/AUTH/INTG/PRIV request and reply round trips, bulk read/write descriptors, user descriptor packing, early replies with checksum and AT offsets, duplicate/reordered/high sequence numbers, context INIT/CONTINUE/DESTROY, stale handle and bad MIC error notifications, server reboot/failover with context replacement, request buffer enlargement under replay, privacy unwrap with malformed ciphertext, and module init unwind across each mechanism/keyring failure point.
