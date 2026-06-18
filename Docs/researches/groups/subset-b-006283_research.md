# Group Research: subset-b-006283

This grouped report covers the SUNRPC generic auth layer, RPCSEC_GSS client/server upcall plumbing, and Kerberos 5 mechanism files under `sources/distributed-fs/ceph-client/net/sunrpc`. Each section preserves the source path and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth.c

## Purpose
`auth.c` is the generic RPC client authentication dispatcher. It owns registration of auth flavors, creation and replacement of per-client `rpc_auth` instances, generic credential-cache management, credential binding to RPC tasks, and the dispatch points for marshalling, refresh, verifier validation, request wrapping, and response unwrapping. RPCSEC_GSS plugs into this file through `rpcauth_register(&authgss_ops)` as flavor `RPC_AUTH_GSS`.

## Important APIs, Types, and Functions
The private `struct rpc_cred_cache` stores an RCU-visible hash table plus a spinlock and hash width. `auth_flavors[]` is an RCU-protected flavor-to-`rpc_authops` registry preloaded with NULL, UNIX, and TLS auth ops. `rpcauth_register()` and `rpcauth_unregister()` install or remove authops with `cmpxchg`; `rpcauth_get_authops()` handles module autoload via `request_module("rpc-auth-%u")` and module refcounting. Public helpers include `rpcauth_create()`, `rpcauth_release()`, `rpcauth_init_credcache()`, `rpcauth_destroy_credcache()`, `rpcauth_lookup_credcache()`, `rpcauth_lookupcred()`, `rpcauth_init_cred()`, `put_rpccred()`, `rpcauth_marshcred()`, `rpcauth_refreshcred()`, and wrap/unwrap/verifier dispatcher functions. `rpc_machine_cred()` exposes a static machine credential marker used by credential binding.

## Control Flow
Client setup calls `rpcauth_create()`, which maps GSS pseudoflavors to `RPC_AUTH_GSS`, gets the authops, calls `ops->create()`, and swaps `clnt->cl_auth`. Task execution calls `rpcauth_refreshcred()`: if no request credential is bound, `rpcauth_bindcred()` chooses an operation-specific cred, a process cred, a machine principal cred, a root fallback, null creds, or a newly looked-up current cred. Encoding then enters the per-credential ops: marshal credentials, wrap procedure args, validate the reply verifier, and unwrap/decode the response.

## State and Persistence
Credential cache entries are hash-linked with `RPCAUTH_CRED_HASHED` and carry one extra reference for hash-table residency. Unused up-to-date cached creds are placed on the global `cred_unused` LRU, counted by `number_cred_unused`, and reclaimed by a shrinker or by `auth_max_cred_cachesize` enforcement. Expired creds observe a 60-second GC moratorium based on `cr_expire`. Authops registration persists until module unregister; auth instances persist by `au_count`.

## Dependencies and Integration Points
The file depends on Linux credentials, RCU, refcounts, spinlocks, shrinkers, XDR streams, SUNRPC client/task/request types, auth modules, tracepoints, and module autoloading. It integrates with auth-specific ops from `auth_null`, `auth_unix`, TLS, and RPCSEC_GSS. It also integrates with transport request sequence tracking via `xprt_rqst_add_seqno()` indirectly through auth-specific marshalers.

## Risks and Edge Cases
Concurrency hinges on lock ordering between `rpc_credcache_lock` and per-cache locks. `put_rpccred()` has race-breaking checks when moving creds to the LRU or unhashed state. A malformed `auth_hashtable_size` module parameter is rejected unless it maps to 4..16384 buckets. `pseudoflavor_to_flavor()` treats values greater than `RPC_AUTH_MAXFLAVOR` as GSS, which is intentional for pseudoflavors but makes GSS module availability critical. Shrinker scanning avoids sleeping in the loop and refuses non-`GFP_KERNEL` reclaim.

## Test Signals
There are no direct unit tests in this file. Behavior is exercised by SUNRPC auth users, RPCSEC_GSS KUnit tests for mechanism pieces, and integration tests that perform authenticated RPC calls. Useful probes are SUNRPC tracepoints and cache-pressure tests that verify credential reuse, expiry, invalidation, and request re-encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/Makefile -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/Makefile

## Purpose
This Makefile defines how the kernel builds the RPCSEC_GSS core module, the Kerberos 5 mechanism module, and optional Kerberos KUnit tests. It is the build-time integration point that decides which implementation files participate under `CONFIG_SUNRPC_GSS`, `CONFIG_RPCSEC_GSS_KRB5`, and `CONFIG_RPCSEC_GSS_KRB5_KUNIT_TEST`.

## Important APIs, Types, and Functions
There are no runtime APIs. The important build targets are `auth_rpcgss.o`, `rpcsec_gss_krb5.o`, and `gss_krb5_test.o`. `auth_rpcgss-y` combines client auth (`auth_gss.o`), the GSS mechanism switch (`gss_mech_switch.o`), server auth (`svcauth_gss.o`), gssproxy upcall and XDR support (`gss_rpc_upcall.o`, `gss_rpc_xdr.o`), and trace support. `rpcsec_gss_krb5-y` combines the Kerberos mechanism adapter, MIC seal/unseal code, wrap/unwrap buffer handling, crypto helpers, and key derivation.

## Control Flow
Build control is entirely Kconfig driven. Enabling `CONFIG_SUNRPC_GSS` builds the generic RPCSEC_GSS module. Enabling `CONFIG_RPCSEC_GSS_KRB5` builds the Kerberos mechanism and makes it available for autoload aliases such as `rpc-auth-gss-krb5`. Enabling `CONFIG_RPCSEC_GSS_KRB5_KUNIT_TEST` builds the standalone KUnit module with RFC test vectors.

## State and Persistence
No runtime state is stored here. The object composition determines which module init/exit functions will exist and which KUnit-only symbols may be imported under `EXPORTED_FOR_KUNIT_TESTING`.

## Dependencies and Integration Points
The file integrates with kernel Kbuild and Kconfig. It binds user-visible configuration options to object files that register authops, GSS mechanisms, server-side domains, and test suites.

## Risks and Edge Cases
Misconfigured options can build generic RPCSEC_GSS without Kerberos, making GSS auth present but Kerberos pseudoflavors unsupported. Test coverage is also configuration-sensitive: unavailable crypto algorithms or disabled enctype configs cause relevant KUnit parameter cases to skip.

## Test Signals
The explicit `gss_krb5_test.o` target is the main test signal. Successful builds under each feature combination validate object dependencies and exported KUnit symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/auth_gss.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/auth_gss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/auth_gss_internal.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/auth_gss_internal.h

## Purpose
This internal header provides small parsing helpers used by RPCSEC_GSS client code to decode gssd downcall byte streams safely. It keeps low-level length and bounds checks shared and local to the auth_gss implementation.

## Important APIs, Types, and Functions
`simple_get_bytes()` copies a fixed-size value from a cursor to a destination and returns the advanced cursor or `ERR_PTR(-EFAULT)` on overflow or pointer wrap. `simple_get_netobj_noprof()` reads an unsigned length, validates the following variable-length data, duplicates it with `kmemdup_noprof()`, and fills an `xdr_netobj`. `simple_get_netobj` is an `alloc_hooks()` wrapper around the noprof implementation.

## Control Flow
Callers pass a current pointer and an end pointer. Fixed fields are consumed first; variable fields read a length then allocate and copy the payload. `auth_gss.c` uses these helpers in `gss_fill_context()` and downcall parsing to decode timeout, window, opaque wire context, imported security context length, and optional acceptor name.

## State and Persistence
The header owns no persistent state. It allocates copied netobject data that callers must free, typically as part of `gss_cl_ctx` cleanup.

## Dependencies and Integration Points
It depends on Linux error pointers, string/memory helpers, XDR netobject definitions, allocation hooks, and `GFP_KERNEL`. It integrates with gssd downcall import, but is not a public kernel API.

## Risks and Edge Cases
The helpers defend against buffer overrun and pointer wrap, which is important because downcalls originate from user space. `simple_get_netobj_noprof()` can leave prior allocations to caller cleanup if a later field fails. The length type is an unsigned int in host byte order, matching the local pipe protocol rather than external XDR.

## Test Signals
There are no direct tests. Malformed gssd downcalls, zero-length netobjects, and oversized length fields are the practical coverage targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/auth_gss_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_crypto.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_crypto.c

## Purpose
`gss_krb5_crypto.c` implements Kerberos 5 cryptographic helpers used by RPCSEC_GSS wrap/MIC paths. It handles confounder generation, checksum/HMAC calculation over `xdr_buf`, CBC plus ciphertext stealing encryption/decryption, RFC 3962/6803 checksum-then-encrypt payloads, and RFC 8009 encrypt-then-MAC payloads.

## Important APIs, Types, and Functions
Public/internal exports include `krb5_make_confounder()`, `krb5_encrypt()`, `gss_krb5_checksum()`, `xdr_extend_head()`, `krb5_cbc_cts_encrypt()`, `krb5_cbc_cts_decrypt()`, `gss_krb5_aes_encrypt()`, `gss_krb5_aes_decrypt()`, `krb5_etm_checksum()`, `krb5_etm_encrypt()`, and `krb5_etm_decrypt()`. Descriptor types `encryptor_desc` and `decryptor_desc` accumulate up to four scatterlist fragments while processing an XDR buffer.

## Control Flow
MIC calculation initializes a keyed ahash, processes the XDR body first, optionally appends the token header, finalizes the digest, and truncates to the enctype checksum length. CBC-CTS encryption processes all but the last two blocks with CBC across scatter/gather fragments, then handles the remainder in a temporary contiguous buffer through the CTS transform. Decryption mirrors this. AES-SHA1/Camellia wrap inserts a confounder after the token header, copies the plaintext header into the trailer, computes HMAC over plaintext, encrypts, and appends the HMAC. RFC 8009 wrap inserts the confounder, encrypts first, then computes HMAC over zero IV plus ciphertext before appending it. Decrypt paths select initiator or acceptor keys based on direction, verify HMAC, decrypt as appropriate, and return head/tail skip sizes for unwrap trimming.

## State and Persistence
The file does not persist state outside caller-provided `krb5_ctx`, crypto transforms, and `xdr_buf` mutation. Sensitive temporary key or digest material is freed with `kfree_sensitive()` where applicable. `xdr_extend_head()` mutates head iovec length and total buffer length in place.

## Dependencies and Integration Points
It depends on the kernel crypto API (`skcipher`, `ahash`, `shash` indirectly through callers), XDR buffer iteration, scatterlists, pages, highmem/pagemap helpers, random bytes, and Kerberos enctype metadata from `gss_krb5_internal.h`. It is called from `gss_krb5_wrap_v2()`/`unwrap_v2()` and MIC seal/unseal code.

## Risks and Edge Cases
Buffer layout is the main risk: page-cache plaintext pages must not be encrypted in place, so send paths swap in scratch pages for output while reading real pages for HMAC. The scatterlist fragment limit is enforced with `BUG_ON(desc->fragno > 3)`. `xdr_extend_head()` assumes sufficient RPC auth slack and uses `BUG_ON` if a shift exceeds `RPC_MAX_AUTH_SIZE`. HMAC comparisons use `crypto_memneq()` to avoid timing leaks. RFC 8009 validates integrity before decrypting, reducing exposure to malformed ciphertext compared with older enctypes.

## Test Signals
KUnit exports cover `gss_krb5_checksum()`, CBC-CTS encrypt/decrypt, and `krb5_etm_checksum()`. `gss_krb5_test.c` validates RFC 3962 encryption vectors, RFC 6803 checksum/encryption vectors, RFC 8009 checksum/encryption vectors, and encrypt/decrypt round trips across all compiled enctypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_internal.h -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_internal.h

## Purpose
This header defines Kerberos 5 RPCSEC_GSS internal data structures, enctype descriptors, context fields, and cross-file function prototypes. It is the contract between the Kerberos mechanism adapter, key derivation, crypto, seal/unseal, and wrap/unwrap files.

## Important APIs, Types, and Functions
`struct gss_krb5_enctype` describes an encryption type: numeric enctype/checksum type, crypto transform names, checksum and key lengths, key-derivation callback, and per-message callbacks. `struct krb5_ctx` stores direction, flags, selected enctype, crypto transforms, derived session and subkeys, sequence counters, end time, and mechanism OID. Important prototypes include MIC functions, wrap/unwrap functions, KDFs (`krb5_derive_key_v2()`, `krb5_kdf_hmac_sha2()`, `krb5_kdf_feedback_cmac()`), `krb5_derive_key()` inline label construction, crypto helpers, AES/EtM encrypt/decrypt, `krb5_nfold()`, and `gss_krb5_lookup_enctype()`.

## Control Flow
The import path fills a `krb5_ctx`, locates an enctype descriptor, derives keys through the descriptor's `derive_key`, allocates transforms, and then uses the descriptor's per-message callbacks for MIC and wrap operations. The inline `krb5_derive_key()` builds the 5-byte key usage label from a 32-bit usage and one-byte seed, then delegates to the enctype KDF.

## State and Persistence
`krb5_ctx` is the persistent security context used after gssd imports a context. It holds crypto transform pointers that must be freed on context deletion, sequence counters that advance per message, and `endtime` for expiration checks. `Ksess` and derived key buffers are sensitive and should be cleared or freed carefully by implementation files.

## Dependencies and Integration Points
The header depends on public Kerberos/SUNRPC definitions, XDR netobjects, crypto transform types, GSS token constants, and page-backed XDR buffers. It integrates the `gss_api_ops` mechanism adapter with lower-level crypto and KUnit-visible test hooks.

## Risks and Edge Cases
Because the descriptor table controls algorithms, key lengths, and function pointers, mismatched lengths or wrong transform names can break interoperability or weaken security. The 32-bit `seq_send` compatibility field must not overflow when importing a 64-bit sequence value for older enctypes. `krb5_derive_key()` assumes `GSS_KRB5_K5CLENGTH` is at least 5 bytes.

## Test Signals
Many prototypes are marked visible/exported under KUnit. `gss_krb5_test.c` exercises descriptor lookup, n-fold, KDFs, checksums, CBC-CTS, EtM checksum, and encryption round trips, with skips when a compiled enctype is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_keys.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_keys.c

## Purpose
`gss_krb5_keys.c` implements Kerberos key derivation primitives for supported RPCSEC_GSS Kerberos enctypes. It covers RFC 3961 n-fold and DK, RFC 3962 AES random-to-key behavior, RFC 6803 Camellia CMAC feedback KDF, and RFC 8009 AES-SHA2 HMAC KDF.

## Important APIs, Types, and Functions
KUnit-visible/exported `krb5_nfold()` implements RFC 3961 n-fold. `krb5_DK()` derives raw key material by repeated encryption of a folded constant. `krb5_random_to_key_v2()` validates and copies AES random bits to a protocol key. `krb5_derive_key_v2()` composes DK plus random-to-key for RFC 3962. `krb5_cmac_Ki()` and `krb5_kdf_feedback_cmac()` implement SP800-108 feedback mode for Camellia. `krb5_hmac_K1()` and `krb5_kdf_hmac_sha2()` implement the single-block HMAC-SHA2 KDF used by RFC 8009.

## Control Flow
Kerberos context import calls `krb5_derive_key()` for each usage and seed. For AES-SHA1, derivation folds the usage constant to the cipher block size, encrypts blocks until enough bytes are available, then copies into the output key. For Camellia, the code allocates a keyed shash, iteratively computes `K(i)` from previous output, counter, constant, separator, and output bit length, concatenates blocks, and truncates. For AES-SHA2, it computes `K1 = HMAC(key, 1 | label | 0 | k)` and truncates to the requested key length.

## State and Persistence
The file owns only temporary derivation buffers and crypto transforms. Temporary raw key material, step values, and K1 buffers are released with `kfree_sensitive()`. Output keys are caller-owned `xdr_netobj`s whose length is preselected by the enctype descriptor.

## Dependencies and Integration Points
It depends on the kernel crypto API (`sync_skcipher`, `shash`), `linux/lcm.h`, Kerberos constants and enctype descriptors, and `krb5_encrypt()` from the crypto file. It feeds key material into `gss_krb5_mech.c`, which allocates per-direction encryption and checksum transforms.

## Risks and Edge Cases
Incorrect length handling would break protocol compatibility. `krb5_random_to_key_v2()` permits only 16- or 32-byte AES-style keys and rejects mismatches. The Camellia implementation notes it does not handle partial-block key sizes, acceptable for current supported enctypes but a risk if new profiles are added. Allocation failures return negative errno and must abort context import.

## Test Signals
`gss_krb5_test.c` validates n-fold against RFC 3961, Camellia Kc/Ke/Ki against RFC 6803, and AES-SHA2 Kc/Ke/Ki against RFC 8009. Tests skip unavailable enctypes via `gss_krb5_lookup_enctype()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_mech.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_mech.c

## Purpose
`gss_krb5_mech.c` registers the Kerberos 5 GSS mechanism with SUNRPC, defines supported enctypes, imports Kerberos contexts from gssd, derives per-direction keys, dispatches MIC/wrap/unwrap operations to enctype implementations, and advertises krb5/krb5i/krb5p pseudoflavors.

## Important APIs, Types, and Functions
The central data is `supported_gss_krb5_enctypes[]`, conditionally compiled for AES-SHA1, Camellia-CMAC, and AES-SHA2. `gss_krb5_prepare_enctype_priority_list()` builds the comma-separated enctype list sent in gssd upcalls. `gss_krb5_lookup_enctype()` returns descriptor metadata. Crypto allocation helpers create keyed skcipher and ahash transforms. `gss_krb5_import_ctx_v2()` derives initiator/acceptor encryption, signing, and integrity keys. `gss_import_v2_context()` parses flags, expiration, sequence, enctype, and session key from the imported context. `gss_krb5_get_mic()`, `gss_krb5_verify_mic()`, `gss_krb5_wrap()`, and `gss_krb5_unwrap()` are `gss_api_ops` dispatchers.

## Control Flow
Module init prepares the enctype priority string and calls `gss_mech_register()`. During context import, the GSS switch allocates a `gss_ctx` and calls `gss_krb5_import_sec_context()`. This parses the v2 context token, rejects unsupported enctypes, stores the Kerberos OID in `mech_used`, derives six transforms for initiator/acceptor seal, sign, and integrity use, and publishes the `krb5_ctx` into the generic GSS context. Per-message operations then select the descriptor function pointers.

## State and Persistence
Persistent mechanism state includes `gss_kerberos_mech`, its pseudoflavor descriptors, and the enctype priority string. Per-context state lives in `krb5_ctx` with transform pointers, sequence counters, and end time. Delete frees all transforms, mechanism OID storage, and the context.

## Dependencies and Integration Points
This file depends on Kconfig-selected crypto algorithms, public SUNRPC GSS definitions, `gss_mech_switch.c`, key derivation and crypto helpers, KUnit visibility exports, and module autoload aliases for names, pseudoflavors, and OID. It maps `RPC_AUTH_GSS_KRB5`, `RPC_AUTH_GSS_KRB5I`, and `RPC_AUTH_GSS_KRB5P` to none, integrity, and privacy services.

## Risks and Edge Cases
Context import rejects trailing bytes, unsupported enctypes, sequence overflow into the 32-bit compatibility field, allocation failures, and crypto transform setup failures. The enctype priority string is fixed at 64 bytes; new enctypes could be silently omitted if the string grows too large. Direction-specific key selection is security-sensitive: initiator and acceptor transforms are deliberately separate.

## Test Signals
KUnit exercises `gss_krb5_lookup_enctype()` and all KDF/crypto behavior behind the descriptors. Runtime tests should verify module autoload aliases, gssd enctype negotiation, and each pseudoflavor service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_mech.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_seal.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_seal.c

## Purpose
`gss_krb5_seal.c` implements Kerberos v2 MIC token generation for RPCSEC_GSS. It constructs RFC 4121-style MIC headers, attaches a 64-bit sequence number, computes the keyed checksum, and reports context expiration.

## Important APIs, Types, and Functions
`setup_token_v2()` writes the MIC token header into a caller-provided `xdr_netobj`, setting flags for acceptor-sent direction and acceptor subkey use and reserving checksum space. `gss_krb5_get_mic_v2()` chooses `initiator_sign` or `acceptor_sign` based on `ctx->initiate`, writes the sequence number with `atomic64_fetch_inc(&ctx->seq_send64)`, computes `gss_krb5_checksum()`, and returns a GSS major status.

## Control Flow
The generic GSS switch calls `gss_get_mic()`, the Kerberos mechanism dispatches to the descriptor's `get_mic`, and this file fills the token. The checksum covers the message body and token header according to the crypto helper's RFC 4121 order. After checksum calculation, current wall-clock time is compared with `ctx->endtime`.

## State and Persistence
The only persistent mutation is incrementing the Kerberos 64-bit send sequence counter. The token buffer is caller-owned and updated in place. The context's flags and end time are read but not changed.

## Dependencies and Integration Points
It depends on Kerberos token constants, `gss_krb5_checksum()`, kernel time, atomics, and the per-context sign transforms created in `gss_krb5_mech.c`. It is used by RPCSEC_GSS verifier and integrity MIC generation.

## Risks and Edge Cases
Direction flags must match the receiver's expectations or unseal will reject the token. The checksum buffer must have enough room for `GSS_KRB5_TOK_HDR_LEN + cksumlength`; this is arranged by higher-level auth slack. Context expiration is reported after checksum generation, so callers may still have a valid token while needing credential renewal.

## Test Signals
There is no direct KUnit test for the token wrapper here, but checksum primitives and key derivation are covered. Integration tests should validate verifier generation and acceptance for initiator and acceptor roles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_seal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_test.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_test.c

## Purpose
`gss_krb5_test.c` is a KUnit test module for the RPCSEC_GSS Kerberos 5 implementation. It validates key derivation, checksum, CBC-CTS encryption, encrypt-then-MAC checksums, and encrypt/decrypt round trips against RFC test vectors and internal self-tests.

## Important APIs, Types, and Functions
`struct gss_krb5_test_param` carries parameterized test data: descriptor, enctype, fold length, constants, keys, usage labels, plaintext, confounder, expected ciphertext/HMAC, and next IV. Shared test helpers are `kdf_case()`, `checksum_case()`, `rfc3961_nfold_case()`, `rfc3962_encrypt_case()`, `rfc6803_encrypt_case()`, `rfc8009_encrypt_case()`, and `encrypt_selftest_case()`. Macros `DEFINE_HEX_XDR_NETOBJ` and `DEFINE_STR_XDR_NETOBJ` create static XDR netobjects for vectors. KUnit suites are registered for RFC 3961, RFC 3962, RFC 6803, RFC 8009, and generic encryption self-tests.

## Control Flow
Each parameterized case looks up the enctype with `gss_krb5_lookup_enctype()` and skips when the algorithm is unavailable under the current config. KDF and checksum tests derive keys through the descriptor and compare exact bytes. Encryption tests allocate crypto transforms, build an `xdr_buf` over KUnit memory, call CBC-CTS helpers and checksum helpers, and compare ciphertext, HMAC, IV, or plaintext after decrypt.

## State and Persistence
The module owns static immutable test vectors. Runtime allocations are KUnit-scoped where possible; crypto transforms are manually freed. It imports symbols from the `EXPORTED_FOR_KUNIT_TESTING` namespace.

## Dependencies and Integration Points
It depends on KUnit, the kernel crypto API, XDR buffers, Kerberos internal headers, and Kconfig-selected enctypes. It integrates with the Makefile through `CONFIG_RPCSEC_GSS_KRB5_KUNIT_TEST`.

## Risks and Edge Cases
Because tests skip unavailable enctypes, a green run does not imply every possible enctype was compiled. The vectors mainly test primitive behavior and do not fully exercise RPCSEC_GSS token framing, rpc_pipefs upcalls, credential cache behavior, or request retransmission. Some string vectors note possible platform encoding assumptions, though the kernel normally uses ASCII-compatible bytes.

## Test Signals
This file is itself the primary test signal. It covers RFC 3961 n-fold, RFC 3962 AES CBC-CTS encryption and IV behavior, RFC 6803 Camellia KDF/checksum/encryption, RFC 8009 AES-SHA2 KDF/checksum/encryption, and encrypt/decrypt round trips for each compiled enctype.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_unseal.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_unseal.c

## Purpose
`gss_krb5_unseal.c` verifies Kerberos v2 MIC tokens. It validates token structure, direction flags, checksum bytes, and context expiration for messages protected by RPCSEC_GSS integrity/verifier operations.

## Important APIs, Types, and Functions
The only function is `gss_krb5_verify_mic_v2()`. It selects the opposite-direction signing transform (`acceptor_sign` for initiators verifying server tokens, `initiator_sign` for acceptors), constructs a temporary checksum buffer, validates the `KG2_TOK_MIC` token ID, verifies flags and filler bytes, computes `gss_krb5_checksum()`, compares the expected checksum with the token checksum, and returns GSS major status.

## Control Flow
Generic RPC verifier validation calls into the GSS switch, then the Kerberos mechanism dispatches to this descriptor callback. The function checks token syntax before doing crypto. It intentionally does not validate the sequence number in the token; RPCSEC_GSS handles sequence validation outside the Kerberos MIC token per comments referencing RFC 2203.

## State and Persistence
No persistent state is mutated. The context's role and end time are read. A stack checksum buffer of `GSS_KRB5_MAX_CKSUM_LEN` is used.

## Dependencies and Integration Points
It depends on Kerberos token constants, `gss_krb5_checksum()`, kernel time, and sign transforms derived by context import. It is the counterpart to `gss_krb5_get_mic_v2()` in `gss_krb5_seal.c`.

## Risks and Edge Cases
Malformed token IDs, unexpected sealed flag, wrong direction bit, non-0xff filler bytes, checksum mismatch, and expired contexts return distinct GSS major statuses. The checksum comparison uses `memcmp()` on local and received checksum bytes; higher-level code maps failures to access errors. The sequence number is deliberately skipped, so sequence validation must remain correct in callers.

## Test Signals
No direct KUnit suite covers full MIC token verification. Indirect signals are checksum tests and integration tests that validate reply verifiers and integrity service responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_unseal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_wrap.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_wrap.c

## Purpose
`gss_krb5_wrap.c` implements Kerberos v2 wrap and unwrap token framing for privacy service. It inserts/removes RFC 4121 wrap headers, handles right-rotation count, delegates encryption/decryption to enctype callbacks, and reshapes `xdr_buf` contents so SUNRPC sees plaintext payloads.

## Important APIs, Types, and Functions
Buffer rotation helpers are `rotate_buf_a_little()`, `_rotate_left()`, and `rotate_left()`. `gss_krb5_wrap_v2()` creates a `KG2_TOK_WRAP` header with direction, acceptor-subkey, sealed flag, EC/RRC fields, and 64-bit sequence number, then calls the enctype encrypt callback. `gss_krb5_unwrap_v2()` validates header fields and direction, rotates ciphertext left if RRC is nonzero, calls the enctype decrypt callback, verifies the decrypted copy of the token header, removes header/confounder/trailer bytes, updates slack/alignment estimates, and returns a GSS status.

## Control Flow
Higher-level `auth_gss.c` privacy wrapping reserves RPCSEC_GSS framing, then calls generic `gss_wrap()`, which dispatches to `gss_krb5_wrap_v2()`. The unwrap path parses the opaque privacy blob, calls `gss_unwrap()`, and then reinitializes the XDR stream over the modified receive buffer. Encryption and decryption details are provided by `gss_krb5_crypto.c` via the selected enctype descriptor.

## State and Persistence
Wrap increments `seq_send64`. Unwrap mutates the `xdr_buf`: it can rotate data, memmove plaintext over the removed header area, shrink head length and total length, trim EC/checksum/trailer bytes, and set per-context slack/alignment outputs. No separate persistent state is stored in this file.

## Dependencies and Integration Points
It depends on XDR buffer subsegments, read/write helpers, Kerberos token constants, kernel time, and enctype-specific crypto callbacks. It is central to krb5p privacy service integration with RPC request/response buffers.

## Risks and Edge Cases
Unwrap must handle RRC rotation correctly or plaintext will be misaligned. Header verification compares the decrypted trailer header to the clear header, but ignores EC/RRC fields as expected. Buffer arithmetic uses `BUG_ON` to catch impossible memmove ranges. Sequence-number validation is left to RPCSEC_GSS callers, so that division of responsibility must remain intact.

## Test Signals
Primitive encryption and checksum behavior are covered by KUnit, but full wrap/unwrap token framing should be validated by krb5p integration tests over RPC calls, including nonzero RRC inputs and varied head/page/tail buffer layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_krb5_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_mech_switch.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_mech_switch.c

## Purpose
`gss_mech_switch.c` is the mechanism registry and dispatcher for SUNRPC GSS. It lets mechanism modules register supported OIDs and pseudoflavors, maps GSS tuples to pseudoflavors, registers server auth domains, imports security contexts, and dispatches generic GSS operations to mechanism-specific ops.

## Important APIs, Types, and Functions
Global state is `registered_mechs`, protected by `registered_mechs_lock` and traversed under RCU. Registration APIs are `gss_mech_register()` and `gss_mech_unregister()`. Lookup APIs include `gss_mech_get_by_name()`, `gss_mech_get_by_OID()`, and `gss_mech_get_by_pseudoflavor()`, with module autoload where needed. Mapping helpers include `gss_svc_to_pseudoflavor()`, `gss_mech_info2flavor()`, `gss_mech_flavor2info()`, `gss_pseudoflavor_to_service()`, `gss_pseudoflavor_to_datatouch()`, and `gss_service_to_auth_domain_name()`. Dispatch functions are `gss_import_sec_context()`, `gss_get_mic()`, `gss_verify_mic()`, `gss_wrap()`, `gss_unwrap()`, and `gss_delete_sec_context()`.

## Control Flow
Mechanism registration first calls `gss_mech_svc_setup()`, which creates `gss/<name>` auth domain names and registers each pseudoflavor with server-side GSS auth. The mechanism is then added to the RCU list. Client or server users look up by name, OID, or pseudoflavor, holding a module reference. Imported contexts allocate a generic `gss_ctx`, get the mechanism reference, and call the mechanism import op. Per-message functions then dispatch through `ctx->mech_type->gm_ops`.

## State and Persistence
Registered mechanisms persist on the global list until unregister. Each pseudoflavor descriptor may own an auth domain and allocated auth domain name. Generic `gss_ctx` objects persist per imported security context and hold a mechanism reference until `gss_delete_sec_context()`.

## Dependencies and Integration Points
It depends on module loading, OID formatting, SUNRPC server auth domain registration, GSS API structs, RPC auth pseudoflavors, tracepoints, RCU, and mechanism modules such as Kerberos. It connects client auth, server auth, and mechanism implementations.

## Risks and Edge Cases
Registration failure must unwind any auth domains already created. Lookups rely on module refs to keep mechanisms alive after RCU traversal. `gss_import_sec_context()` allocates `gss_ctx` before calling the mechanism; if a mechanism import fails after partial allocation, cleanup responsibility must be observed by callers and mechanism code. OID-to-module autoload uses a stringified OID, so alias correctness matters.

## Test Signals
Autoload and mapping can be tested by converting Kerberos OID/qop/service to krb5/krb5i/krb5p pseudoflavors and back. Runtime GSS calls validate dispatch. KUnit for Kerberos indirectly exercises lookup by enctype, while integration tests exercise mechanism registration and deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_mech_switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_upcall.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_upcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_upcall.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/auth_gss/gss_rpc_upcall.h -->
