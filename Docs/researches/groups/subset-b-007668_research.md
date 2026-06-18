# subset-b-007668 research

This grouped report covers the requested Lustre PTLRPC errno, LNet event callback, and GSS security files. Each file section is wrapped with reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/errno.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/errno.c

Purpose: provides optional host-to-network and network-to-host errno translation for Lustre wire compatibility when `LUSTRE_TRANSLATE_ERRNOS` is enabled. It exists because Linux errno numeric values are not fully portable across architectures, while Lustre RPC replies need stable on-wire status values.

Important APIs/types/functions: `lustre_errno_hton()` maps a local positive errno value to a `LUSTRE_E*` value; `lustre_errno_ntoh()` maps back to the host errno namespace; both are exported symbols. The static `lustre_errno_hton_mapping[]` and `lustre_errno_ntoh_mapping[]` tables are designated-initializer arrays intended to be one-to-one. They include normal POSIX/Linux errors, Lustre-specific network errors such as `EBADHANDLE`, and LDLM-specific `ELDLM_*` values that intentionally preserve their numeric range.

Control flow: callers pass unsigned errno magnitudes, not negative return codes. Zero maps to zero. If an index is in range and populated, the table value is returned. If the value is out of range or maps to zero, control falls to a generic path that returns `LUSTRE_EIO` or `EIO` to avoid interpreting an unknown numeric errno as a different meaning on another host.

State/persistence: no mutable runtime state and no persistence. The ABI-relevant state is the compiled mapping table. Changing table values changes wire semantics.

Dependencies/integration: depends on `lustre_errno.h`; under translation it also includes `lustre_dlm.h` for `ELDLM_*` values. Integrated with PTLRPC packing/unpacking paths that put status codes on the wire.

Risks/test signals: table gaps silently degrade to I/O error, which is safe but loses specificity. Architecture-specific aliases are explicitly called out: `EDEADLOCK` is avoided in favor of `EDEADLK`. Tests should verify round trips for representative POSIX errors, Lustre private errors, LDLM errors, zero, unknown high values, and table entries that are unavailable on a given architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/errno.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/events.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/events.c

Purpose: implements PTLRPC's LNet event callbacks and portal initialization/shutdown glue. It converts LNet send, receive, unlink, ACK, GET, PUT, and REPLY events into request, reply, bulk, history, wakeup, and teardown state transitions.

Important APIs/types/functions: client callbacks are `request_out_callback()`, `reply_in_callback()`, and `client_bulk_callback()`. Server callbacks are `request_in_callback()`, `reply_out_callback()`, and, under `CONFIG_LUSTRE_FS_SERVER`, `server_bulk_callback()`. `ptlrpc_master_callback()` dispatches through `ptlrpc_cb_id`. `ptlrpc_uuid_to_peer()` resolves an OBD UUID to the best peer/self NID pair. `ptlrpc_init_portals()` and `ptlrpc_exit_portals()` initialize LNet, PTLRPC daemon refs, handler callbacks, and `ptlrpc_pending` draining.

Control flow: outgoing request completion records send time, marks the request MD unlinked, handles send failures as network errors, wakes waiters when both request and reply paths are unlinked or failed, then drops a request ref. Incoming replies distinguish early adaptive-timeout replies from real replies, handle truncation, set reply offsets/lengths, clear resend, update import reply timestamps and highest replied XID, and wake the waiting client. Bulk callbacks decrement descriptor refs, accumulate transferred bytes on success, mark failures, and wake the owning request or wait queue when refs reach zero. Incoming server requests allocate or reuse request descriptors, fill peer/source/self/rqbd metadata, add ordered history sequence IDs, queue to the service partition, and wake service threads. Difficult replies are scheduled only after send/unlink/commit conditions require high-priority reply processing.

State/persistence: manages in-memory request flags (`rq_req_unlinked`, `rq_reply_unlinked`, `rq_replied`, `rq_net_err`, `rq_early`), bulk descriptor refs/failure counts, service request history lists, request-buffer refcounts, import timestamps, and global `ptlrpc_pending` percpu ref shutdown state. No disk persistence.

Dependencies/integration: tightly coupled to LNet event delivery, `ptlrpc_request`, `ptlrpc_bulk_desc`, `ptlrpc_service_part`, adaptive timeouts, import pinger state, `sptlrpc_request_out_callback()`, PTLRPC daemon lifecycle, and service wait queues.

Risks/test signals: callback ordering is intentionally loose; replies may arrive before send completion and ACKs may arrive before SEND events. Races are controlled with request, descriptor, service, and reply-state locks. Tests should stress send failure, unlink-only events, early replies, truncated replies, bulk integrity failures via failpoints, zero posted receive buffers, difficult reply ACK loss, portal shutdown waiting for pending events, and UUID/NID distance selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/Makefile -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/Makefile

Purpose: builds the Lustre PTLRPC GSS security module object set.

Important APIs/types/functions: declares `obj-m += ptlrpc_gss.o` and composes `ptlrpc_gss-objs` from shared policy, bulk, client/server upcall, raw object, lproc, token, mechanism switch, Kerberos, null, and crypto objects. `gss_sk_mech.o` is included only under `CONFIG_LUSTRE_FS_GSS_SSK`; `gss_keyring.o` only under `CONFIG_LUSTRE_FS_GSS_KEYRING`; `GCOV_PROFILE := y` is enabled under `CONFIG_GCOV_PROFILE_LUSTRE`.

Control flow: no runtime control flow. Build-time conditionals decide which mechanisms and keyring policy are present in the module.

State/persistence: no runtime state. The build output determines which registration functions are linked and therefore which security mechanisms can initialize.

Dependencies/integration: integrates with the kernel module build system and the wider Lustre PTLRPC security policy registration path. It assumes objects such as `sec_gss.o` and `gss_svc_upcall.o` outside this work item provide common service-side support.

Risks/test signals: configuration mismatches can compile a module without expected mechanisms or keyring support. Build tests should cover default GSS, SSK enabled, keyring enabled, both enabled, and GCOV profile builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_api.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_api.h

Purpose: defines the simplified mechanism-independent GSS API used by Lustre PTLRPC security. It is the dispatch contract between common security code and concrete mechanisms such as Kerberos, shared-key, and null.

Important APIs/types/functions: `struct gss_ctx` stores the selected `gss_api_mech`, an opaque mechanism context, and a `digest_hash` callback. `struct gss_api_mech` describes a registered mechanism, module owner, OID, refcount, operations, and supported subflavors. `struct gss_api_ops` provides import/copy/inquire, MIC, wrap/unwrap, bulk prep/wrap/unwrap, delete, and display hooks. Public wrappers include `lgss_import_sec_context()`, `lgss_get_mic()`, `lgss_verify_mic()`, `lgss_wrap()`, `lgss_unwrap()`, `lgss_prep_bulk()`, `lgss_wrap_bulk()`, `lgss_unwrap_bulk()`, `lgss_delete_sec_context()`, and mechanism lookup/registration helpers.

Control flow: common code creates or receives a `gss_api_mech`, imports an opaque token into a `gss_ctx`, then invokes wrapper functions that assert the mechanism operations and dispatch to mechanism-specific implementations. Mechanism lookup can be by name or security subflavor.

State/persistence: only declares in-memory structures. The runtime registry and context ownership are implemented in `gss_mech_switch.c`; persistent credentials normally come from user-space upcalls or kernel keyrings.

Dependencies/integration: includes `uapi/linux/lustre/lgss.h` for `rawobj_t` and interoperates with `bio_vec` bulk buffers and `ptlrpc_bulk_desc`. It is consumed by `sec_gss.c`, `gss_bulk.c`, keyring/upcall code, and all mechanisms.

Risks/test signals: every mechanism must implement all operation slots expected by the wrappers. Tests should register fake mechanisms, validate module ref get/put behavior, verify subflavor dispatch, exercise MIC/wrap/bulk forwarding, and ensure failed imports clean up partially allocated contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_asn1.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_asn1.h

Purpose: declares minimal ASN.1/DER helpers for generic GSS token headers and defines generic GSS token parsing error constants adapted from upstream SunRPC/MIT Kerberos code.

Important APIs/types/functions: `g_OID_equal()` compares mechanism OIDs. `g_verify_token_header()` validates the application sequence tag, DER length, OID tag/length/value, and token body availability. `g_get_mech_oid()` extracts a copied mechanism OID from a token. `g_token_size()` calculates full token size for a mechanism OID and body length. `g_make_token_header()` writes the DER header and OID.

Control flow: mechanism code computes token size, writes headers before message-specific bytes, or verifies/extracts OIDs before processing received tokens. The implementation lives in `gss_generic_token.c`.

State/persistence: no state. Constants encode stable error values used internally by mechanism code.

Dependencies/integration: depends on `rawobj_t`, `memcmp()`, and the GSS generic token implementation. Kerberos and mechanism negotiation code use this layer for OID-tagged token handling.

Risks/test signals: the comments note an assumption that mechanism OIDs fit in one length byte. Tests should cover short tokens, bad sequence/OID tags, mismatched OIDs, malformed DER lengths, large body size calculations, and correct pointer advancement without modification on error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_asn1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_bulk.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_bulk.c

Purpose: applies GSS security services to PTLRPC bulk I/O descriptors. It signs, verifies, encrypts, decrypts, and prepares page vectors for bulk read/write paths on both client and server sides.

Important APIs/types/functions: client entry points are `gss_cli_ctx_wrap_bulk()`, `gss_cli_ctx_unwrap_bulk()`, and `gss_cli_prep_bulk()`. Server entry points are `gss_svc_prep_bulk()`, `gss_svc_unwrap_bulk()`, and `gss_svc_wrap_bulk()`. The helper `gss_prep_bulk()` allocates encryption pages with `obd_pool_get_desc_pages()` and calls `lgss_prep_bulk()`. Bulk security metadata is carried in `struct ptlrpc_bulk_sec_desc`.

Control flow: client wrap chooses the bulk security descriptor offset according to RPC service mode (`NULL`, `AUTH`, `INTG`, `PRIV`). For bulk reads with privacy it prepares receive pages; for bulk writes it either computes a MIC over `bd_vec` or allocates encrypted pages and calls `lgss_wrap_bulk()`. Client unwrap compares request and reply descriptors, handles server error flags, verifies bulk-read integrity, decrypts private bulk reads, and adjusts `bd_nob_transferred` to plaintext size. Server unwrap validates write data against the request descriptor, sets reply descriptor error flags on failures, verifies MICs or decrypts private writes. Server wrap signs or encrypts read replies and records ciphertext/plaintext sizes for the client.

State/persistence: mutates request buffers, clear buffers, reply buffers, bulk descriptor byte counts, vector lengths, encrypted vector allocation, and BSD error flags. No persistent storage.

Dependencies/integration: depends on PTLRPC flavor macros, Lustre message buffer layout, `gss_cli_ctx`, `gss_svc_reqctx`, `ptlrpc_bulk_desc`, OBD page pools, and mechanism dispatch functions in `gss_mech_switch.c`.

Risks/test signals: descriptor offsets vary by service mode, making layout regressions high risk. Integrity mode must trim final vector lengths before verification; privacy mode must preserve cleartext byte counts. Tests should cover client read/write and server read/write for null, integrity, and privacy bulk services; zero-vector bulk; server `BSD_FL_ERR`; mismatched descriptors; allocation failure; and mechanism MIC/encryption failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_bulk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_cli_upcall.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_cli_upcall.c

Purpose: bridges user-space GSS negotiation (`lgssd`/keyring upcall data) to kernel PTLRPC security-context initialization and destruction RPCs.

Important APIs/types/functions: `gss_do_ctx_init_rpc()` validates an `lgssd_ioctl_param`, finds a client OBD/import, builds a `SEC_CTX_INIT` request, sends it, parses the reply, and copies result fields back to user space. `gss_do_ctx_fini_rpc()` sends `SEC_CTX_FINI` for an uptodate context. Helpers `ctx_init_pack_request()` and `ctx_init_parse_reply()` serialize request and reply payloads.

Control flow: initialization validates ioctl size and interface version, copies the target OBD name from user space, rejects invalid/stopping/non-client devices, gets a live import, ensures the security id still matches, allocates `RQF_SEC_CTX`, packs the GSS header, optional user descriptor, target UUID, reverse handle, and user token, then waits synchronously. Queue failures other than `-EACCES` are reported to user space as `-ETIMEDOUT` so negotiation can retry. Reply parsing checks GSS version/bufcount, writes status, major/minor, sequence window, context handle, and output token to the supplied user buffer.

State/persistence: no durable storage. Mutates a transient request, user output buffer, context procedure field for destroy, and import/request refs.

Dependencies/integration: depends on PTLRPC request allocation/packing, `RQF_SEC_CTX`, `SEC_CTX_INIT`, `SEC_CTX_FINI`, OBD/import lookup, GSS raw object serialization, security flavor packing, and user-space `lgssd` ABI structures.

Risks/test signals: user pointer handling, output size checks, stale imports, changed `secid`, and request lifetime cleanup are primary risks. Tests should cover bad ioctl versions/sizes, invalid OBD names, unsupported device types, deactivated imports, oversized tokens, user copy failures, server denial, timeout remapping, swabbed replies, and destroy RPC suppression for non-uptodate/error contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_cli_upcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_crypto.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_crypto.c

Purpose: provides common crypto and parsing helpers for GSS mechanisms, including keyblock transform setup, serialized field extraction, scatterlist construction, hashing over mixed message/page data, padding, and raw-object encryption.

Important APIs/types/functions: `gss_keyblock_init/free/dup()` manage `rawobj_t` keys and `crypto_sync_skcipher` transforms. `gss_get_bytes()`, `gss_get_rawobj()`, and `gss_get_keyblock()` parse user-space serialized contexts. `gss_setup_sgtable()` maps kmalloc or vmalloc buffers into a scatter-gather table; `gss_teardown_sgtable()` frees multi-entry tables. `gss_crypt_generic()` encrypts/decrypts a contiguous buffer in place. `gss_digest_hash()` and `gss_digest_hash_compat()` update an ahash over raw objects, bio_vec pages, and optional headers. `gss_add_padding()` PKCS-style pads with byte value equal to padding length. `gss_crypt_rawobjs()` encrypts/decrypts a sequence of raw objects into one output object.

Control flow: mechanisms import keys, initialize transforms, build scatterlists for either direct buffers or pages, then drive synchronous kernel crypto requests. Hash helpers process message rawobjs first, then bulk vectors, then headers; the compat variant hashes only header length for the optional header.

State/persistence: keyblocks own allocated key bytes and optional crypto transforms. Parsing helpers allocate raw object buffers. No persistent state.

Dependencies/integration: uses Linux crypto skcipher/ahash APIs, Lustre OBD allocation macros, `bio_vec`, vmalloc/page helpers, and LNet crypto wrappers.

Risks/test signals: transform setkey failure leaves allocated transforms unless callers free; buffer length must match block size; sgtable setup must handle vmalloc buffers and zero lengths correctly. Tests should cover malformed serialized lengths and overflow checks, empty raw objects, vmalloc and kmalloc hashing, block-aligned and unaligned encryption inputs, padding bounds, multi-object encryption, and cleanup after crypto errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_crypto.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_crypto.h

Purpose: declares common GSS crypto helper types and functions used by Kerberos and shared-key mechanisms.

Important APIs/types/functions: `struct gss_keyblock` pairs a `rawobj_t` key with a synchronous skcipher transform. Prototypes cover keyblock lifecycle, serialized context parsing, sgtable setup/teardown, generic encryption, digest hashing, compatibility hashing, padding, and raw object encryption/decryption.

Control flow: no executable flow. Mechanisms include this header and call helper functions during context import, MIC generation, wrap/unwrap, and bulk encryption.

State/persistence: the header defines ownership expectations for keyblocks but stores no state itself.

Dependencies/integration: includes Linux scatterlist and skcipher headers plus `gss_internal.h`, so users inherit raw object definitions and Lustre security declarations.

Risks/test signals: this is an internal contract; signature changes must be reflected in every mechanism. Compile tests with Kerberos and SSK enabled are the main signal, plus unit coverage of helper behavior in `gss_crypto.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_err.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_err.h

Purpose: defines GSS-API status bit fields, flags, and standard major-status constants used by Lustre GSS mechanism code.

Important APIs/types/functions: `OM_uint32` is the status type. Context flags include delegation, mutual auth, replay, sequence, confidentiality, and integrity. Macros split status codes into calling, routine, and supplementary fields (`GSS_CALLING_ERROR`, `GSS_ROUTINE_ERROR`, `GSS_SUPPLEMENTARY_INFO`, `GSS_ERROR`). Routine errors include `GSS_S_BAD_MECH`, `GSS_S_BAD_SIG`, `GSS_S_NO_CONTEXT`, `GSS_S_DEFECTIVE_TOKEN`, `GSS_S_CONTEXT_EXPIRED`, and `GSS_S_FAILURE`; supplementary flags include duplicate, old, unsequenced, and gap tokens.

Control flow: no runtime code. Mechanisms return these constants through the `lgss_*` dispatch wrappers and higher PTLRPC security code maps failures to kernel errno values where needed.

State/persistence: none.

Dependencies/integration: consumed by all GSS implementation files in this set. Values are adapted from standard GSS bindings and should remain ABI-stable within the module's user/kernel negotiation contract.

Risks/test signals: accidental value changes would alter error classification. Tests should verify `GSS_ERROR()` behavior, supplementary bit extraction, and representative mechanism failure mapping to `-EACCES`, `-EPROTO`, or retry behavior in surrounding code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_generic_token.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_generic_token.c

Purpose: implements minimal DER/ASN.1 token header construction and verification for GSS tokens carrying mechanism OIDs.

Important APIs/types/functions: private helpers `der_length_size()`, `der_write_length()`, and `der_read_length()` handle definite-form DER lengths. `g_token_size()` computes sequence-tag plus length plus OID plus body size. `g_make_token_header()` writes application tag `0x60`, sequence length, OID tag `0x06`, OID length, and OID bytes. `g_verify_token_header()` validates the token header and leaves the caller's buffer pointer and body size advanced only on success. `g_get_mech_oid()` extracts and allocates a copy of the OID from an input token.

Control flow: token creation sizes the final buffer, writes the generic header, and leaves mechanism-specific code to append token type and body. Verification rejects short buffers, wrong tags, invalid DER lengths, sequence-length mismatches, wrong OIDs, and insufficient two-byte inner token type space.

State/persistence: allocates only the OID copy in `g_get_mech_oid()`; no persistent state.

Dependencies/integration: uses `gss_asn1.h`, `gss_err.h`, raw object allocation, and is used by GSS mechanism negotiation paths that need OID-tagged tokens.

Risks/test signals: integer overflow is noted but not fully guarded in token size calculation. OID length is assumed to fit one byte. Tests should cover all malformed-token branches, multi-byte DER lengths, OID mismatch versus structurally bad token precedence, correct output pointer/body size on success, and cleanup of allocated OID data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_generic_token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_internal.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_internal.h

Purpose: central internal header for PTLRPC GSS implementation. It defines raw object helpers, GSS wire constants, client/server context structures, keyring-specific state, inline conversions, and cross-file prototypes.

Important APIs/types/functions: raw object API includes allocation, duplication, serialization, extraction, and netobj conversion. `gss_round_ctx_expiry()` subtracts a timeout delta for forward contexts. GSS enums define interface versions, PTLRPC GSS procedures, target services, and packing flags. `struct gss_svc_reqctx`, `struct gss_cli_ctx`, `struct gss_cli_ctx_keyring`, `struct gss_sec`, and `struct gss_sec_keyring` carry service request state, client context handles, keyring bindings/timers, security mechanism pointers, reverse handles, cache lists, and root-context locks. Inline helpers convert base PTLRPC security/context pointers to GSS-specific structs.

Control flow: no primary flow, but prototypes expose the file-level integration map: common signing/sealing in `sec_gss.c`, keyring lifecycle, bulk wrapping, client/server upcalls, lproc stats, and mechanism init/cleanup. Conditional inline stubs make keyring and SSK support compile out cleanly.

State/persistence: defines in-memory security context and cache state. Persistence, if any, is through kernel keyrings and user-space tokens handled elsewhere.

Dependencies/integration: includes keyring, keyctl, crypto hash, LNet crypto, Lustre security, and upcall cache headers. It binds this work item to unlisted companions such as `sec_gss.c`, `gss_svc_upcall.c`, and `lproc_gss.c`.

Risks/test signals: structure layout and flag definitions are cross-file contracts. Tests should build all configuration combinations, validate context expiry rounding, handle conversion helpers, bulk descriptor pointer storage, reverse-context sequence updates, and upcall cache interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_keyring.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_keyring.c

Purpose: implements the `gss.keyring` PTLRPC security policy and kernel key type used to cache, refresh, revoke, and downcall GSS client contexts. It is the main persistence and lifecycle manager for GSS credentials in the kernel.

Important APIs/types/functions: context helpers include `ctx_create_kr()`, `ctx_destroy_kr()`, `ctx_enlist_kr()`, `ctx_unlist_kr()`, `bind_key_ctx()`, `unbind_key_ctx()`, `kill_ctx_kr()`, `dispose_ctx_list_kr()`, and timeout handlers. Security-policy hooks include `gss_sec_create_kr()`, `gss_sec_lookup_ctx_kr()`, `gss_sec_flush_ctx_cache_kr()`, `gss_sec_gc_ctx_kr()`, and `gss_sec_display_kr()`. Client context hooks include refresh, validate, and die implementations. Key-type hooks include `gss_kt_instantiate()`, `gss_kt_update()`, match, describe, destroy, and revoke. Exported SSK helpers `gss_rename_sk_key()` and `gss_cleanup_sk_key()` manage client-specific shared-key user keys.

Control flow: lookup first optimizes root/reverse contexts, then constructs a key description `<uid>@<secid>` and callout info containing sec id, mechanism, uid/gid, security flags, service flag/type, peer/self NIDs, target UUID, caller namespace PID, and client UUID. `request_key()` triggers user-space negotiation. If the returned key has no payload, a new context is created, listed, bound to the key, and protected by an upcall timeout. Downcall enters through key update: it extracts sequence window, failure codes or handle/mechanism token, imports the mechanism context, marks the context uptodate on success, or expires/errors and unbinds on failure. Flush and GC move contexts to a freelist, wake waiters, update reverse service sequence state, unbind keys, and release refs.

State/persistence: persistent kernel state is the `lgssc` key type and its key payload pointer to `ptlrpc_cli_ctx`. Security state includes cached context hlist, root context pointer, root/upcall mutexes, timers, key refs, context refs, expiry, flags, handles, sequence windows, and reverse handles.

Dependencies/integration: depends on Linux keyrings, credential override APIs, request-key authorization, Lustre security policy registration, imports, NID helpers, common GSS context operations, service upcall reverse-context helpers, OBD allocation, and optional kernel compatibility macros.

Risks/test signals: races around key payload, context cache membership, timer expiry, revoke, and user-space downcall are high risk; comments document lock ordering. Namespace switching and credential override affect security boundaries. Tests should cover parallel `request_key()` for the same uid, root versus non-root key placement, timeout invalidation, too-early key update returning `-EAGAIN`, negotiation failure, successful import, root unbinding after success, user key retention, forced flush of busy contexts, reverse root replacement, key revoke/destroy ordering, SSK rename/cleanup, and policy register/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_keyring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_krb5.h -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_krb5.h

Purpose: defines Kerberos mechanism constants, token header layout, context state, checksum/signature algorithms, and supported encryption type identifiers for Lustre's GSS Kerberos implementation.

Important APIs/types/functions: RFC 4121 usage constants identify acceptor/initiator seal/sign keys. `struct krb5_header` is the 16-byte MIC/wrap header with token id, flags, filler, EC/RRC, sequence, and checksum tail. `struct krb5_ctx` tracks initiator/CFX/subkey flags, expiry, seed, send/receive sequences, enctype, encryption/integrity/checksum keyblocks, and mechanism OID. Constants define token ids, flags, checksum types, Kerberos error values, and supported AES enctypes.

Control flow: no executable code. `gss_krb5_mech.c` fills and verifies these headers while importing user-space contexts and performing MIC/wrap/bulk crypto.

State/persistence: declares per-context in-memory state. Imported keys and sequence numbers are held in `struct krb5_ctx`.

Dependencies/integration: includes `gss_crypto.h` for keyblocks. Interfaces with user-space Kerberos context serialization and Linux crypto algorithm selection.

Risks/test signals: header endianness and sequence semantics are wire-visible. Tests should verify supported enctype mapping, header size assumptions, initiator/acceptor direction flag behavior, token id constants, and context import compatibility with both older RFC1964-style and newer RFC4121-style serialized contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_krb5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_krb5_mech.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_krb5_mech.c

Purpose: implements the Kerberos GSS mechanism for Lustre, including context import/copy, MIC generation/verification, message wrap/unwrap, encrypted bulk I/O, display, and mechanism registration.

Important APIs/types/functions: `krb5_init_keys()` maps Kerberos enctypes to kernel crypto transforms. `import_context_rfc1964()` and `import_context_rfc4121()` parse user-space context formats. `gss_import_sec_context_kerberos()` selects parser and initializes keys. `gss_copy_reverse_context_kerberos()` flips initiator role and send/receive sequences for reverse contexts. `krb5_make_checksum()` builds keyed hashes over headers, raw messages, and page vectors. `fill_krb5_header()` and `verify_krb5_header()` manage token metadata and sequence numbers. `gss_get_mic_kerberos()`, `gss_verify_mic_kerberos()`, `gss_wrap_kerberos()`, and `gss_unwrap_kerberos()` implement per-message services. Bulk helpers encrypt/decrypt confounders, page vectors, and trailing headers. `init_kerberos_module()` registers subflavors `krb5n`, `krb5a`, `krb5i`, and `krb5p`.

Control flow: context import reads version, expiry, flags, sequences, enctypes, key sizes, and keys, then initializes skcipher transforms. MIC fills a header, hashes message/page data plus header, and stores the truncated checksum. Verify recomputes and compares. Wrap pads plaintext, generates a confounder, hashes confounder/GSS header/message/Kerberos header, encrypts confounder/message/header into the token, and appends checksum. Unwrap verifies header and checksum after decrypting. Bulk privacy encrypts page vectors into `bd_enc_vec`, optionally adjusts ciphertext byte counts, and verifies checksums during unwrap.

State/persistence: per-context keys, crypto transforms, expiry, sequence counters, and mechanism OID are in memory. Sequence send increments under `krb5_seq_lock`; no persistent replay database is present in this file.

Dependencies/integration: depends on `gss_crypto.c`, Linux crypto, random confounder generation, `ptlrpc_bulk_desc`, GSS dispatch, and user-space Kerberos serialization. It intentionally uses CBC with padding for AES CTS enctypes because kernel CTS support is absent.

Risks/test signals: security risks include sequence handling, checksum truncation, AES CTS-vs-CBC compatibility, padding, and exact page-length adjustment. There is a suspicious decrypt-bulk path using `sg_src.sgl`/`sg_dst.sgl` after local `src`/`dst` setup, worth targeted regression testing. Tests should cover all supported enctypes, old/new context import, malformed key counts/sizes, MIC mismatch, direction flag mismatch, short tokens, wrap padding, bulk short final pages, adjusted byte counts, and crypto transform failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_krb5_mech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_mech_switch.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_mech_switch.c

Purpose: implements the mechanism registry and mechanism-independent GSS operation dispatch layer.

Important APIs/types/functions: `lgss_mech_register()` and `lgss_mech_unregister()` maintain the global `registered_mechs` list under `registered_mechs_lock`. `lgss_name_to_mech()` and `lgss_subflavor_to_mech()` find mechanisms and take module refs. `lgss_mech_get()`/`lgss_mech_put()` manage module ownership. Wrapper functions allocate or validate `gss_ctx` objects and dispatch every operation in `struct gss_api_ops`, including context import/copy/delete, inquire, MIC, wrap/unwrap, bulk prep/wrap/unwrap, and display.

Control flow: mechanisms register at module initialization. Lookup scans the list under spinlock and uses `try_module_get()` to pin a found mechanism. Import allocates a generic `gss_ctx`, pins the mechanism, installs the default hash function, and calls mechanism import. Copy allocates a new generic context, pins the same mechanism, copies hash behavior, and asks the mechanism to duplicate reverse state. Delete calls the mechanism destructor for opaque state, drops the module ref, frees the generic context, and nulls the caller's pointer.

State/persistence: global in-memory registered mechanism list and module refcounts. Contexts are heap objects owned by PTLRPC security contexts.

Dependencies/integration: used by keyring downcall import, service upcall context creation, bulk code, and concrete mechanisms. Depends on module ownership, list/spinlock APIs, `gss_crypto` hash defaults, and `gss_api.h`.

Risks/test signals: duplicate registration is not rejected, unregister assumes the list entry is present, and failed mechanism import after generic allocation depends on caller cleanup via delete. Tests should cover register/unregister ordering, lookup by name/subflavor, module get failures, failed copy cleanup, delete of null/no-context, and wrapper assertions with incomplete ops in debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_mech_switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_null_mech.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_null_mech.c

Purpose: implements a minimal `gssnull` mechanism for null-service GSS contexts, primarily for testing and protocol plumbing without cryptographic protection.

Important APIs/types/functions: `struct null_ctx` stores a 64-bit token. `gss_import_sec_context_null()` validates and copies the token from the input buffer. `gss_copy_reverse_context_null()` duplicates the token for reverse contexts. `gss_inquire_context_null()` returns a short expiry. All MIC, wrap, unwrap, prep bulk, wrap bulk, and unwrap bulk functions return success without modifying data. `gss_display_null()` reports `null`. `init_null_module()` registers the `SPTLRPC_SUBFLVR_GSSNULL` subflavor.

Control flow: import requires exactly one `struct null_ctx` worth of input. Once imported, every security operation is a no-op success, allowing common PTLRPC GSS paths to execute with `SPTLRPC_SVC_NULL`.

State/persistence: stores only the copied 64-bit token and a synthetic expiry of current time plus 60 seconds. No persistent credentials.

Dependencies/integration: registers through `gss_mech_switch.c`, uses OBD allocation macros, and integrates with the subflavor table consumed by security flavor lookup.

Risks/test signals: this mechanism provides no authentication, integrity, or privacy and must only be selected where `gssnull` is intended. Tests should verify invalid input rejection, reverse-copy independence, short expiry behavior, no-op operations, display string, and register/unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_null_mech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_rawobj.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_rawobj.c

Purpose: implements raw object allocation, duplication, serialization, extraction, netobj conversion, and fixed byte extraction for GSS token/context parsing.

Important APIs/types/functions: `rawobj_empty()`, `rawobj_alloc()`, `rawobj_free()`, `rawobj_equal()`, and `rawobj_dup()` manage `rawobj_t` ownership. `rawobj_serialize()` writes a little-endian length followed by 4-byte-rounded data. `rawobj_extract()`, `_alloc()`, `_local()`, and `_local_alloc()` parse serialized objects either by pointing into the caller buffer or allocating a copy, with network little-endian or local-endian length handling. `rawobj_from_netobj()` and `_alloc()` bridge `netobj_t`. `buffer_extract_bytes()` copies fixed-size fields and advances a pointer.

Control flow: serializers and extractors validate remaining buffer length before consuming bytes. Extractors set empty objects to `{0,NULL}` and either point into the serialized stream or allocate independent storage. Local extraction uses exact length rather than network 4-byte rounding.

State/persistence: allocated raw object data is caller-owned until `rawobj_free()`. Non-alloc extractors borrow the backing buffer.

Dependencies/integration: heavily used by GSS keyring downcalls, context import parsers, client upcall packing, and service upcall handling.

Risks/test signals: caller confusion between borrowed and allocated raw objects can cause lifetime bugs. `rawobj_serialize()` copies `obj->data` even for nonzero len and assumes valid data. Tests should cover empty objects, short buffers, rounded network lengths, local unrounded lengths, allocation failure, duplicate/free idempotence expectations, endianness, and pointer/buflen advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_rawobj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_sk_mech.c -->
# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_sk_mech.c

Purpose: implements Lustre's shared-key (`sk`) GSS mechanism, supporting null/auth/integrity/privacy subflavors with HMACs and optional encrypted message/bulk payloads.

Important APIs/types/functions: `struct sk_ctx` stores selected crypt/hash algorithms, expiry, host/peer random nonces, IV counter, HMAC key, and session keyblock. `struct sk_hdr` carries message version and IV. `sk_fill_context()` parses user-space serialized shared-key context data. `sk_fill_header()`, `sk_verify_header()`, and `sk_construct_rfc3686_iv()` manage IV/nonce construction. MIC operations use `sk_make_hmac()` and `sk_verify_hmac()`. Message privacy uses `gss_wrap_sk()`/`gss_unwrap_sk()`. Bulk privacy uses `gss_prep_bulk_sk()`, `sk_encrypt_bulk()`, `sk_decrypt_bulk()`, `gss_wrap_bulk_sk()`, and `gss_unwrap_bulk_sk()`. `init_sk_module()` registers `skn`, `ska`, `ski`, and `skpi`.

Control flow: import validates interface version, HMAC algorithm, encryption algorithm, expiry delta, random nonces, HMAC key length, and optional session key; privacy initializes a skcipher transform. Reverse copy duplicates keys but starts IVs at `SK_IV_REV_START` so forward and reverse contexts do not reuse counter ranges with the same key. Wrap pads plaintext, fills a header, encrypts with an RFC3686-style IV, and HMACs header/GSS header/ciphertext. Unwrap validates the header and HMAC before decryption. Bulk HMAC verification hashes only the sender's declared byte count rather than all allocated encrypted pages.

State/persistence: per-context keys, algorithm ids, expiry, random nonces, and atomic IV counter are in memory. No disk persistence. IV monotonicity is critical security state.

Dependencies/integration: compiled only when SSK support is enabled. Uses Lustre crypto algorithm name mapping, `gss_crypto.c`, Linux skcipher/ahash, PTLRPC bulk descriptors, and GSS mechanism dispatch.

Risks/test signals: IV reuse is explicitly fatal; counter wrap returns failure. Header stores use `be64_to_cpu()` when filling and `cpu_to_be64()` when verifying, which should be tested for endian correctness. Tests should cover malformed serialized contexts, unsupported algorithms, short HMAC keys, privacy absent/present, reverse IV range, MIC mismatch, token shortness, block padding, bulk byte-count HMAC, adjusted vectors, and counter wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_sk_mech.c -->
