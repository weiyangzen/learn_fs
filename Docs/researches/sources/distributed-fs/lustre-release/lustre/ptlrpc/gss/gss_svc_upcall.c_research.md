# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_svc_upcall.c

## Purpose
`gss_svc_upcall.c` implements the server-side RPCSEC_GSS upcall bridge for Lustre PTLRPC. It owns two upcall-backed caches: the RPCSEC init cache (`rsicache`) that sends context-init tokens to userspace, and the RPCSEC context cache (`rsccache`) that stores accepted service contexts imported from userspace. The file also manages reverse service contexts used for callbacks, initializes cache state at module load, and checks whether the `lsvcgssd` init socket is available.

## Important APIs, types, and functions
- Global state: `rsicache`, `rsccache`, `krb5_allow_old_client_csum`, and the randomized `__ctx_index` counter protected by `__ctx_index_lock`.
- Hash helpers: `hash_mem()` and 64-bit `hash_mem_64()` compute cache bucket keys from raw handles and tokens.
- RSI cache functions: `rsi_entry_init()`, `rsi_entry_free()`, `rsi_do_upcall()`, `rsi_parse_downcall()`, `rsi_entry_get()`, `rsi_entry_put()`, and `rsi_upcall_cache_ops`.
- RSC cache functions: `rsc_entry_init()`, `__rsc_free()`, `rsc_do_upcall()`, `rsc_parse_downcall()`, `rsc_accept_expired()`, `rsc_entry_get()`, `rsc_entry_put()`, and `rsc_upcall_cache_ops`.
- Context-facing exports: `gss_svc_upcall_handle_init()`, `gss_svc_upcall_get_ctx()`, `gss_svc_upcall_put_ctx()`, `gss_svc_upcall_destroy_ctx()`, `gss_svc_upcall_install_rvs_ctx()`, `gss_svc_upcall_expire_rvs_ctx()`, `gss_svc_upcall_dup_handle()`, and `gss_svc_upcall_update_sequence()`.
- Lifecycle: `gss_init_svc_upcall()` creates both caches; `gss_exit_svc_upcall()` tears them down.

## Control flow
For `PTLRPC_GSS_PROC_INIT`, `sec_gss.c` calls `gss_svc_upcall_handle_init()`. This builds a temporary `gss_rsi` key from the incoming GSS handle, incoming token, Lustre service type, primary peer NID, and nodemap name. `rsi_entry_get()` may trigger `rsi_do_upcall()`, which formats a single argument containing the cache key, service, NID, suggested context index, nodemap, input handle, and token, then invokes the configured userspace helper with `call_usermodehelper()`. Userspace later writes a downcall. `rsi_parse_downcall()` records major/minor status plus output handle and token.

After the RSI result is available, `gss_svc_upcall_handle_init()` looks up the output handle in `rsccache`. RSC entries are populated by userspace downcalls through `rsc_parse_downcall()`, which imports the mechanism context via `lgss_import_sec_context()`, queries its expiry, and fills service identity fields including remote/root/MDS/OSS flags, mapped uid, uid, gid, mechanism, and nodemap. On success, the request context gets an extra cache reference to `gsc_ctx`, the reverse handle is copied, the target is recorded, and an INIT reply containing the output handle/token and status is packed.

For normal data requests, `gss_svc_upcall_get_ctx()` searches `rsccache` by wire handle and returns the embedded `gss_svc_ctx`; the caller later drops it with `gss_svc_upcall_put_ctx()`. Destroy requests mark the cache entry invalid and force early expiry. Reverse-context helpers install a copied mechanism context into `rsccache`, update expiry from `lgss_inquire_context()`, assign server role bits from the import target type, and preserve sequence state for callbacks.

## State and persistence behavior
All state is in memory. RSI entries are short-lived and invalidated after an init request is handled regardless of success. RSC entries live until their GSS mechanism expiry, explicit destroy, invalidation, or cache cleanup. Context expiry is converted from real-time GSS expiry to monotonic cache expiry using current real seconds. Reverse contexts can be made to expire soon, and their last reverse sequence number can be stored through `gss_svc_upcall_update_sequence()`. Cache initialization seeds `__ctx_index` from kernel randomness to reduce handle collisions after reboot.

## Dependencies and integration points
This file depends on Lustre upcall cache infrastructure, raw object helpers, nodemap lookup, LNet NID conversion, GSS mechanism APIs, PTLRPC reply packing, and kernel userspace-helper/socket APIs. It integrates tightly with `sec_gss.c` for server request admission, error notify packing, reverse context creation, and context lifetime. It also integrates with `lproc_gss.c`, which exposes cache tunables and downcall debugfs files.

## Risks
- `rsi_do_upcall()` must calculate its helper argument length correctly; wrong sizing risks truncation or `-E2BIG`.
- Userspace downcall parsing trusts length fields after magic checks; malformed buffers must be rejected without leaking partially allocated raw objects.
- `gss_svc_upcall_handle_init()` invalidates RSI entries after use, so retry behavior depends on callers and clients reissuing init tokens.
- Reverse-context expiry and accepted-expired logic are delicate: too strict can break callbacks, too permissive can allow use of stale contexts.
- Hash functions are not cryptographic; correctness depends on full match comparisons after bucket selection.
- The old Kerberos checksum compatibility gate is security-sensitive and controlled by the `krb5_allow_old_client_csum` tunable.

## Test signals
Useful tests include GSS mount/authentication with `lsvcgssd` running and absent, malformed RSI/RSC downcalls, INIT with missing/oversized handles or tokens, old-client checksum compatibility toggling, context expiry and destroy behavior, reverse callback context install/expire/update paths, nodemap identity propagation, and reboot/failover cases where randomized context indexes avoid stale-handle confusion.
