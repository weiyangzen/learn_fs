# subset-b-000931 Research

Grouped research report for the requested Ceph-client Linux crypto subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/anubis.c -->
# sources/distributed-fs/ceph-client/crypto/anubis.c

Purpose: implements the generic Linux Crypto API provider for the Anubis 128-bit block cipher. It registers `anubis-generic` as a `CRYPTO_ALG_TYPE_CIPHER` algorithm with 16-byte blocks and 16, 20, 24, 28, 32, 36, or 40 byte keys.

Important APIs/types/functions: `struct anubis_ctx` stores key length, round count, and encryption/decryption round key arrays. The large `T0` through `T5` tables and `rc` constants drive the tweaked Anubis key schedule and round function. `anubis_setkey()` validates key length, derives encryption round keys, and builds the inverse schedule. `anubis_crypt()` performs common block transformation, while `anubis_encrypt()` and `anubis_decrypt()` select `ctx->E` or `ctx->D`. `anubis_alg`, `anubis_mod_init()`, and `anubis_mod_fini()` provide module registration.

Control flow: module load calls `crypto_register_alg()`. Consumers allocate a cipher transform, call the setkey hook, then call single-block encrypt/decrypt hooks. Key expansion maps big-endian key words into `kappa`, iterates `R = 8 + key_words` rounds, and computes decryption keys by reversing and transforming encryption keys. Crypting reads four big-endian words, applies the initial key, executes `R - 1` table rounds, executes a masked final round, and writes big-endian output.

State and persistence: all runtime state is per-transform memory in `struct anubis_ctx`; the lookup tables are read-only module data. There is no disk persistence. Sensitive key schedule material is stored until the transform is freed by the crypto core.

Dependencies and integration points: depends on `crypto/algapi.h`, module init/exit, unaligned big-endian helpers, and the classic cipher `cra_u.cipher` interface. It integrates with any kernel code that requests `"anubis"` or `"anubis-generic"`.

Risks: table-based cipher code is not constant-time with respect to lookup indices, so side-channel suitability depends on deployment context. Key-size validation is strict but unusual because Anubis accepts seven key lengths. Round-table or inverse-schedule corruption would break interoperability. The old single-block cipher interface is lower-level than modern skcipher/lskcipher users normally want.

Test signals: crypto selftests should include known-answer vectors for all accepted key lengths, encrypt/decrypt round trips, invalid key length rejection, module load/unload, and algorithm lookup aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/anubis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/api.c -->
# sources/distributed-fs/ceph-client/crypto/api.c

Purpose: provides the core Linux Crypto API transform allocation, algorithm lookup, module autoload, larval placeholder, selftest, notifier, and transform destruction machinery. It is the central registry-facing runtime for crypto algorithm consumers and providers.

Important APIs/types/functions: global exported objects include `crypto_alg_list`, `crypto_alg_sem`, and `crypto_chain`. `crypto_mod_get()` and `crypto_mod_put()` manage algorithm and module references. `crypto_larval_alloc()`, `crypto_larval_add()`, `crypto_larval_wait()`, and `crypto_larval_kill()` represent algorithms being probed, tested, or instantiated by cryptomgr. `crypto_alg_mod_lookup()`, `crypto_find_alg()`, `crypto_alloc_base()`, and `crypto_alloc_tfm_node()` locate and allocate transforms. `crypto_create_tfm_node()`, `crypto_clone_tfm()`, and `crypto_destroy_tfm()` manage transform memory and lifecycle hooks. `crypto_req_done()` is the common completion helper.

Control flow: lookup first scans registered algorithms under `crypto_alg_sem`, prefers exact driver-name matches or highest-priority generic-name matches, and filters type/mask/FIPS/internal/tested flags. If no usable algorithm exists, it can `request_module("crypto-%s")`, ask cryptomgr through `crypto_chain`, insert a larval, wait up to 60 seconds, and retry on `-EAGAIN` unless interrupted. Allocation wraps lookup, algorithm reference acquisition, frontend type initialization, optional provider `cra_init`, and rollback on failure. Destruction runs frontend/provider exit hooks and drops algorithm/module references.

State and persistence: algorithm registration state is process-global kernel memory protected by `crypto_alg_sem`. Larvals carry completions, probe state, and adult algorithm pointers until killed. Transforms store their algorithm pointer, refcount, NUMA node, frontend backing, and provider context until freed. No filesystem persistence exists.

Dependencies and integration points: depends on `internal.h`, module loading, completions, blocking notifier chains, static keys for boot selftests, crypto type frontends, and cryptomgr. Nearly every higher-level crypto allocation path ultimately depends on this file.

Risks: lookup and larval state are concurrency-sensitive; missed completions, refcount mistakes, or lock-order issues can hang callers or unload live modules. FIPS/internal/tested mask rules are subtle and easy to bypass accidentally. `crypto_request_clone()` falls back to the original request when allocation fails, so callers must understand ownership. Timeout and signal handling must not leave dead larvals in the registry.

Test signals: module autoload success/failure, cryptomgr fallback, larval timeout, interrupted allocation, tested/FIPS-internal filtering, provider `cra_init` returning `-EAGAIN`, NUMA allocation paths, clone fallback, and repeated concurrent allocation of the same algorithm are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/arc4.c -->
# sources/distributed-fs/ceph-client/crypto/arc4.c

Purpose: registers the generic ARC4 stream cipher through the lightweight skcipher API. The implementation is intentionally compatibility-focused and warns callers that `ecb(arc4)` use is obsolete.

Important APIs/types/functions: `crypto_arc4_setkey()` delegates to `arc4_setkey()` for `struct arc4_ctx`. `crypto_arc4_crypt()` copies the transform context into the state IV buffer unless `CRYPTO_LSKCIPHER_FLAG_CONT` is set, then calls `arc4_crypt()`. `crypto_arc4_init()` emits a rate-limited obsolete-use warning. `arc4_alg` declares algorithm metadata, key bounds, state size, and symmetric encrypt/decrypt callbacks.

Control flow: module initialization registers `arc4_alg` with `crypto_register_lskcipher()`. Each operation either starts from the transform's base RC4 state or continues from the supplied state buffer, then mutates that working state as bytes are generated. Encrypt and decrypt are identical stream-XOR operations.

State and persistence: persistent state is per-transform `struct arc4_ctx`; per-request continuation state is passed through `siv`. There is no external persistence. Callers must preserve `siv` when using continuation mode.

Dependencies and integration points: depends on `crypto/arc4.h`, `crypto/internal/skcipher.h`, scheduler task names for warnings, and the lskcipher registration API. Exposes `"arc4"` / `"arc4-generic"` with alias `"ecb(arc4)"`.

Risks: ARC4 is cryptographically obsolete, and the warning confirms new users should avoid it. Continuation state misuse can restart keystreams or corrupt stream position. The implementation assumes the state buffer is large and aligned enough for `struct arc4_ctx`.

Test signals: key length bounds, encrypt/decrypt known-answer vectors, continuation versus fresh-state behavior, alias lookup, obsolete warning rate limiting, and module unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/arc4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aria_generic.c -->
# sources/distributed-fs/ceph-client/crypto/aria_generic.c

Purpose: implements the generic ARIA block cipher provider for the Linux Crypto API, including key schedule generation, encryption, decryption, and exported helper functions used by architecture-specific or mode wrappers.

Important APIs/types/functions: `key_rc` contains ARIA round constants. `aria_set_encrypt_key()` derives encryption round keys from 128, 192, or 256 bit keys using ARIA substitution/diffusion helpers from `crypto/aria.h`. `aria_set_decrypt_key()` derives inverse round keys. `aria_set_key()` validates key length, initializes `struct aria_ctx`, and exports the setkey helper. `__aria_crypt()` is the common round function. `aria_encrypt()` and `aria_decrypt()` are exported raw helpers; `__aria_encrypt()` and `__aria_decrypt()` are Crypto API callbacks.

Control flow: module load registers `aria_alg`. Setkey computes rounds as `(key_len + 32) / 4`, fills `enc_key`, then builds `dec_key`. Encryption/decryption load four big-endian words, apply alternating odd/even subst-diff rounds, perform the final S-box/key transformation, and store big-endian output.

State and persistence: state is per-transform `struct aria_ctx`, including key length, round count, and round-key arrays. Constants and S-boxes are read-only. No persistence exists outside transform lifetime.

Dependencies and integration points: depends on `crypto/aria.h` for ARIA primitive helpers, S-boxes, context layout, and constants. Registers `"aria"` and `"aria-generic"` as a classic cipher algorithm.

Risks: key schedule layout is guarded by `BUILD_BUG_ON()` size checks, but any context-layout change must remain synchronized with callers and assembly alternatives. Table lookups may have side-channel implications. Wrong accepted key sizes or round counts would silently break standards compliance.

Test signals: RFC 5794 known-answer vectors for 128/192/256 bit keys, exported helper use from accelerated implementations, invalid key length rejection, module alias lookup, and encrypt/decrypt inverse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/aria_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/Kconfig -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/Kconfig

Purpose: defines build-time configuration for Linux asymmetric key support, public-key subtype support, X.509/PKCS#8/PKCS#7 parsers, PE signature verification, and optional FIPS signature selftests.

Important APIs/types/functions: `ASYMMETRIC_KEY_TYPE` enables the key type and depends on `KEYS`. `ASYMMETRIC_PUBLIC_KEY_SUBTYPE` selects MPI, hash info, akcipher, sig, and hash support. Parser options include `X509_CERTIFICATE_PARSER`, `PKCS8_PRIVATE_KEY_PARSER`, and `PKCS7_MESSAGE_PARSER`. `PKCS7_WAIVE_AUTHATTRS_REJECTION_FOR_MLDSA` provides a compatibility waiver. `PKCS7_TEST_KEY`, `SIGNED_PE_FILE_VERIFICATION`, and `FIPS_SIGNATURE_SELFTEST*` enable test and verification modules.

Control flow: Kconfig selection controls which objects the Makefile builds and which verification features can be reached by module signing, firmware, kexec, and keyring code. Parser options layer on the public key subtype, and PKCS#7 depends on X.509 parsing.

State and persistence: no runtime state is stored here; it persists only as kernel configuration. Selected options change available key types, parsers, and verification behavior.

Dependencies and integration points: integrates with `crypto/asymmetric_keys/Makefile`, keyrings, ASN.1 decoder generation, OID registry, hash and signature algorithms, module/firmware verification, and FIPS boot requirements.

Risks: missing `select` dependencies can produce runtime `-ENOPKG` failures or build failures. The ML-DSA authattrs waiver is a policy-sensitive compatibility exception and should remain narrowly scoped.

Test signals: build matrices for built-in and modular parsers, configs with only X.509 or PKCS#7 enabled, PE verification configs, and FIPS selftest configs with RSA/ECDSA individually selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/Makefile -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/Makefile

Purpose: maps asymmetric key Kconfig options to kernel objects and generated ASN.1 parser artifacts. It assembles compound modules such as `asymmetric_keys.o`, `x509_key_parser.o`, `pkcs7_message.o`, and PE verification support.

Important APIs/types/functions: `asymmetric_keys-y` combines `asymmetric_type.o`, `restrict.o`, and `signature.o`. X.509 support builds generated `x509.asn1.o` and `x509_akid.asn1.o` with parser/loader/public-key code. PKCS#8, PKCS#7, PKCS#7 test key, PE verification, and selftest objects are conditionally assembled from their sources.

Control flow: kbuild uses `obj-$(CONFIG_...)` to include objects, and explicit dependencies ensure generated ASN.1 headers exist before C parser objects compile. `clean-files` removes generated parser products.

State and persistence: no runtime state. Build products and generated ASN.1 C/header files are filesystem artifacts controlled by kbuild.

Dependencies and integration points: integrates with the kernel ASN.1 compiler, `crypto/asymmetric_keys/Kconfig`, generated parser definitions, key type registration, PKCS#7/X.509 verification, and selftest object inclusion.

Risks: dependency typos can race generated headers or leave stale generated files. Object grouping determines module boundaries and owner references used by parsers. The duplicated `mscode.asn1.h` prerequisite looks harmless but should be checked if dependency maintenance changes.

Test signals: clean builds after `make clean`, modular and built-in configurations for each parser, generated ASN.1 dependency ordering under parallel builds, and selftest object inclusion by config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/asymmetric_keys.h -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/asymmetric_keys.h

Purpose: provides private declarations shared by asymmetric key implementation files.

Important APIs/types/functions: declares `asymmetric_key_hex_to_key_id()`, `__asymmetric_key_hex_to_key_id()`, and `asymmetric_key_eds_op()`. The first two convert hexadecimal key-id strings into `struct asymmetric_key_id` values, while `asymmetric_key_eds_op()` is the encryption/decryption/signing operation dispatch for asymmetric keys.

Control flow: implementation files include this header to avoid exposing private helper declarations in public keyring headers. Restriction parsing uses the hex helpers, and the key type operation table points at `asymmetric_key_eds_op()`.

State and persistence: no state is stored here. The types referenced are owned by keyring and public key payload code.

Dependencies and integration points: depends on `<keys/asymmetric-type.h>` and the kernel pkey parameter definitions reachable through it. Integrated by `asymmetric_type.c`, `restrict.c`, `x509_public_key.c`, and related parser code.

Risks: declarations must match exported definitions exactly; signature drift breaks builds or keyctl operation dispatch. Keeping this header private limits accidental ABI expansion.

Test signals: compile coverage of asymmetric key type, restriction, X.509, and pkey operation configs validates the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/asymmetric_keys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/asymmetric_type.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/asymmetric_type.c

Purpose: implements the `"asymmetric"` key type, parser registry, key-id matching, key descriptions, key cleanup, keyring restriction lookup, and pkey operation dispatch.

Important APIs/types/functions: `find_asymmetric_key()` searches keyrings by issuer/serial, subject key ID, or subject name ID. `asymmetric_key_generate_id()`, `asymmetric_key_id_same()`, `asymmetric_key_id_partial()`, and `asymmetric_key_hex_to_key_id()` build and compare identifiers. Match-preparse helpers support `id:`, `ex:`, and `dn:` search prefixes. `asymmetric_key_preparse()` iterates registered parsers. `register_asymmetric_key_parser()` and `unregister_asymmetric_key_parser()` manage the parser list. `key_type_asymmetric` wires all operations into the keyring core.

Control flow: key instantiation calls `asymmetric_key_preparse()`, which scans parser modules under `asymmetric_key_parsers_sem` until one returns something other than `-EBADMSG`. Searches can use direct description matching or iterative key-id matching. Restriction strings such as `builtin_trusted`, `builtin_and_secondary_trusted`, and `key_or_keyring:<serial>[:chain]` are parsed into `struct key_restriction` callbacks. Pkey encryption/decryption/sign/verify operations dispatch through the key subtype stored in the payload.

State and persistence: global parser list state is protected by an rwsem. Each key persists subtype, key IDs, crypto payload, and auth signature data in `key->payload` until destroyed. Restriction objects can hold referenced trust keys.

Dependencies and integration points: depends on Linux keyrings, public-key subtype interfaces, system keyring restriction functions, user-type helpers, module references, and parser modules such as X.509 and PKCS#8.

Risks: key-id search prefixes are security-sensitive because partial versus exact matching changes trust decisions. Parser lifetime depends on module owner references and correct free-preparse behavior. Restriction parsing must not leak referenced keys on allocation failure. Payload slot indexes must match public asymmetric key conventions.

Test signals: key add/search by description, `id:` partial, `ex:` exact, and `dn:` exact searches; parser registration conflicts; restriction string variants; unsupported subtype pkey operations; key destroy/free-preparse leak checks; and concurrent parser registration with key instantiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/asymmetric_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/mscode_parser.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/mscode_parser.c

Purpose: parses Microsoft Individual Code Signing authenticated content embedded in Authenticode PKCS#7 signatures and extracts the PE image digest algorithm and digest.

Important APIs/types/functions: `mscode_parse()` adjusts the content pointer to include the ASN.1 header and invokes `asn1_ber_decoder()` with `mscode_decoder`. `mscode_note_content_type()` validates that the content type is a PE image data OID, with a compatibility allowance for a historical `pesign` bug. `mscode_note_digest_algo()` maps supported OIDs to crypto hash names. `mscode_note_digest()` duplicates the signed digest into `struct pefile_context`.

Control flow: `verify_pefile_signature()` passes `mscode_parse()` as the PKCS#7 content callback. During ASN.1 decode, OID callbacks validate content and choose the hash algorithm, then the digest callback stores the expected PE digest for later comparison against a locally computed digest.

State and persistence: state is stored only in the caller-provided `struct pefile_context`: `digest_algo`, `digest`, and `digest_len`. The digest allocation is freed by PE verification cleanup.

Dependencies and integration points: depends on generated `mscode.asn1.h`, OID registry helpers, PKCS#7 callback conventions, and `verify_pefile.h`.

Risks: accepting the historical alternate OID is intentional but broadens accepted input. Digest OID support must match available crypto hash algorithms. The pointer adjustment by `asn1hdrlen` assumes the PKCS#7 callback contract remains stable.

Test signals: Authenticode signatures with sha1/sha2/sha3 digests, unknown OID rejection, alternate `OID_msIndividualSPKeyPurpose` acceptance, malformed ASN.1, and digest allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/mscode_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_key_type.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_key_type.c

Purpose: defines a testing key type that accepts a PKCS#7-wrapped user payload only after the PKCS#7 signature validates against trusted system keys, then exposes the unwrapped user payload.

Important APIs/types/functions: module parameter `usage` selects the `enum key_being_used_for` verification usage. `pkcs7_view_content()` temporarily substitutes PKCS#7 content data into the preparse payload and delegates to `user_preparse()`. `pkcs7_preparse()` invokes `verify_pkcs7_signature()` with `VERIFY_USE_SECONDARY_KEYRING`. `key_type_pkcs7` reuses user key instantiate, revoke, destroy, describe, and read operations.

Control flow: adding a `pkcs7_test` key runs `pkcs7_preparse()`, validates the configured usage, verifies the wrapper, and calls back into `pkcs7_view_content()` to parse the inner payload as a user key. Module init registers the test key type.

State and persistence: persistent key payload is the unwrapped user payload in the keyring. The module parameter controls runtime verification policy. No file persistence exists.

Dependencies and integration points: depends on keyrings, user key type helpers, `linux/verification.h`, and the PKCS#7 verification stack.

Risks: this is explicitly test infrastructure; the writable module parameter changes verification semantics. Temporarily mutating `prep->data` and `prep->datalen` must restore them on all paths.

Test signals: adding valid and invalid wrapped keys, each allowed `usage` value, invalid usage rejection, secondary keyring trust failures, and successful readback of only the inner payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_key_type.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_parser.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_parser.c

Purpose: parses PKCS#7/CMS signed-data blobs into in-memory `struct pkcs7_message` objects containing content metadata, embedded X.509 certificates, CRLs, and signer information.

Important APIs/types/functions: `struct pkcs7_parse_context` tracks the message under construction, current `SignedInfo`, certificate lists, raw issuer/serial/SKID fields, OIDs, and indexes. `pkcs7_parse_message()` drives `asn1_ber_decoder()`. `pkcs7_free_message()` frees certificates and signed infos. OID, version, content, certificate, signer, authenticated-attribute, serial, issuer, SKID, and signature callbacks fill `struct pkcs7_message` and `struct pkcs7_signed_info`.

Control flow: parsing allocates a message and first `SignedInfo`, decodes ASN.1, appends certificates through `x509_cert_parse()`, records encapsulated data or detached-data metadata, maps digest/signature OIDs to crypto algorithm strings, enforces authenticated attribute consistency, and appends completed signed-info records. Authenticated attributes must contain content type and message digest and cannot repeat supported attributes.

State and persistence: parsed state is heap memory owned by the returned `pkcs7_message`; embedded certificates link into `certs` and `crl`, signers link through `signed_infos`, and signature buffers/auth IDs are owned by each signed info. No state persists after `pkcs7_free_message()`.

Dependencies and integration points: depends on generated `pkcs7.asn1.h`, OID registry, public-key signature structures, X.509 parser, and later verification/trust code in `pkcs7_verify.c` and `pkcs7_trust.c`.

Risks: ASN.1 pointer/length bookkeeping is high risk because many fields point into the original blob while signatures are duplicated. Authattrs policy differs by usage and ML-DSA compatibility config. Signer ID construction must choose issuer+serial versus SKID correctly. Missing cleanup after late allocation failures can leak partially built structures.

Test signals: DER/BER PKCS#7 messages with attached and detached data, multiple signers, CMS version 3 SKID signers, Authenticode authenticated attributes, duplicate/missing authattrs rejection, unsupported OIDs, and malformed certificate lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_parser.h -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_parser.h

Purpose: defines internal PKCS#7 parser and verifier structures shared by parsing, signature verification, and trust validation.

Important APIs/types/functions: `struct pkcs7_signed_info` stores signer certificate pointer, index, unsupported/blacklisted flags, authenticated attribute state, signing time, message digest attribute, authattrs byte range, and `struct public_key_signature`. `struct pkcs7_message` stores certificate/CRL lists, signed-info list, version, authattrs flags, content type, content length/header length, and content pointer. Debug macros `kenter` and `kleave` wrap `pr_devel()`.

Control flow: parser code fills these structures, verifier code resolves `signer`, computes digests, and trust code walks signer chains using `seen` and `verified` fields in linked X.509 certificates.

State and persistence: all state is per parsed message and freed by `pkcs7_free_message()`. Pointers to content and authenticated attributes often reference the original PKCS#7 buffer, so caller lifetime matters.

Dependencies and integration points: includes OID registry, public PKCS#7 API declarations, and `x509_parser.h`. Used by `pkcs7_parser.c`, `pkcs7_verify.c`, and `pkcs7_trust.c`.

Risks: structure field semantics are shared across files; changing ownership of `sig->m`, `authattrs`, or `data` can cause use-after-free or double-free. Bit indexes for `aa_set` must remain synchronized with parser checks.

Test signals: compile coverage of all PKCS#7 files, multi-signer verification, detached data lifetime tests, and authattrs parsing/verification tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_trust.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_trust.c

Purpose: validates that a verified PKCS#7 signature chain intersects a trusted keyring, returning policy-aware trust results after cryptographic verification has linked internal chains.

Important APIs/types/functions: `pkcs7_validate_trust_one()` walks a signed info's signer chain, searches the trust keyring with `find_asymmetric_key()`, verifies the relevant signature with the trusted key, and caches verified certificates. `pkcs7_validate_trust()` iterates signed infos and prioritizes return codes across `-ENOKEY`, `-ENOPKG`, success, and hard failures.

Control flow: for each signer, the code walks from leaf signer to root, checking whether any certificate is already trusted. If no embedded certificate matches, it tries the root's authority IDs against trusted keys, then tries direct signed-info signer IDs. A matched key must verify either an embedded certificate signature or the signed-info signature. Success marks certificates from leaf to the trusted intersection as verified.

State and persistence: trust validation mutates in-memory `seen` and `verified` flags in embedded X.509 certificates and reads signed-info `unsupported_crypto`. No keyring state is modified.

Dependencies and integration points: depends on asymmetric key search, public-key signature verification, PKCS#7 internal structures, and caller-supplied trust keyrings such as builtin, secondary, or platform keyrings.

Risks: trust depends on correct key-id matching and verifying the trusted variant can validate the descendant signature. Cached `seen`/`verified` state must be reset appropriately before validation. Direct signed-info fallback is useful but security-sensitive.

Test signals: chains trusted at leaf, intermediate, and root; unknown self-signed roots; direct signer keys; unsupported crypto; signature failure with matched trusted key; multi-signer messages where one chain succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_trust.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_verify.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_verify.c

Purpose: verifies PKCS#7 message integrity and embedded certificate chains before external trust validation. It computes content/authattr digests, checks signatures, links embedded certificates, and enforces usage-specific PKCS#7 policy.

Important APIs/types/functions: `pkcs7_digest()` computes or selects the signature message buffer, handling authenticated attributes and algorithms that take raw data. `pkcs7_get_digest()` exposes a single-signer digest. `pkcs7_find_key()` matches signed-info issuer IDs to embedded certs. `pkcs7_verify_sig_chain()` verifies embedded certificate chains and detects loops/blacklisting. `pkcs7_verify_one()` verifies one signer. `pkcs7_verify()` enforces usage policy and iterates signers. `pkcs7_supply_detached_data()` attaches caller-owned data to a parsed detached signature.

Control flow: verification first validates the requested usage's expected content type/authattrs policy. For each signer, it digests content, verifies messageDigest authattr when present, re-digests authattrs as a SET for signature verification, locates the signer certificate, checks signing time against certificate validity if available, verifies the signed info signature, and verifies embedded chain signatures as far as possible.

State and persistence: verification mutates `sig->m`, `sig->m_size`, `sig->m_free`, signer pointers, certificate `seen`, `signer`, `blacklisted`, and signed-info flags. Detached data is only borrowed; callers must keep it alive.

Dependencies and integration points: depends on shash algorithms, hash-name mapping, public-key verification, X.509 certificate structures, ASN.1 tag constants, and higher-level module/firmware/kexec/BPF verification callers.

Risks: authenticated attribute canonicalization is subtle; the code mutates the first tag byte from context-specific to SET before hashing. Usage policy differences can reject valid-looking messages for the wrong context. Missing hash/signature algorithms produce `-ENOPKG`, which must not be confused with trust failure. Detached data lifetime is external.

Test signals: attached/detached signatures, authattrs digest mismatch, signing time outside certificate validity, blacklisted certificates, unsupported hash algorithms, ML-DSA raw-data behavior, module versus firmware versus kexec usage policy, and certificate-chain loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs7_verify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs8_parser.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs8_parser.c

Purpose: parses unencrypted PKCS#8 private key blobs, currently accepting RSA, and instantiates them as asymmetric public-key subtype keys with private-key material.

Important APIs/types/functions: `struct pkcs8_parse_context` tracks the public key object, source base, last OID, algorithm OID, and key bytes. ASN.1 callbacks `pkcs8_note_OID()`, `pkcs8_note_version()`, `pkcs8_note_algo()`, and `pkcs8_note_key()` validate and collect fields. `pkcs8_parse()` decodes the blob and duplicates the private key bytes. `pkcs8_key_preparse()` fills asymmetric key payload slots and parser metadata. `pkcs8_key_parser` registers with the asymmetric parser list.

Control flow: key preparse calls `pkcs8_parse()`, which allocates `struct public_key`, decodes ASN.1 with `pkcs8_decoder`, rejects non-version-0 and non-RSA algorithms, copies the private key, marks it private, then returns it for payload installation. Module init registers the parser as `"pkcs8"`.

State and persistence: private key bytes are stored in `public_key->key` and freed by public-key subtype destruction. No key IDs or auth signature are generated. Key persistence follows kernel keyring lifetime and permissions.

Dependencies and integration points: depends on generated `pkcs8.asn1.h`, asymmetric parser registration, public-key subtype, OID registry, and keyring preparse conventions.

Risks: only unencrypted RSA PKCS#8 is supported; unsupported algorithms return `-ENOPKG`. Private key material must stay within sensitive-free paths. Lack of key IDs means lookup by ID does not work for these keys unless descriptions are supplied externally.

Test signals: valid RSA PKCS#8 import, non-zero version rejection, unsupported algorithm OID, malformed ASN.1, private signing/decryption operations through keyctl, and sensitive cleanup on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/pkcs8_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/public_key.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/public_key.c

Purpose: implements the in-software public-key asymmetric subtype, translating kernel key payloads into akcipher or sig algorithm instances for query, encryption, decryption, signing, and verification.

Important APIs/types/functions: `public_key_free()` releases key material and parameters. `software_key_determine_akcipher()` maps key algorithm, encoding, hash, and operation to Crypto API algorithm names such as `pkcs1(rsa,sha256)`, `pkcs1pad(rsa)`, `x962(ecdsa-...)`, or raw ML-DSA/ECRDSA names. `software_key_query()` reports key sizes and supported operations. `software_key_eds_op()` performs encrypt/decrypt/sign. `public_key_verify_signature()` verifies signatures and checks key/signature algorithm compatibility. `public_key_subtype` exports subtype callbacks.

Control flow: subtype callbacks pack public/private key bytes with algorithm id and parameters, allocate either `crypto_sig` or `crypto_akcipher`, set public/private keys, run the requested operation, and free all temporary material. Verification rejects mismatched pkey algorithms except the accepted ECDSA key/algorithm naming difference.

State and persistence: persistent state is `struct public_key` in an asymmetric key payload, including key bytes, parameters, key length, algorithm names, flags, and private/public bit. Temporary packed key buffers are freed with `kfree_sensitive()`.

Dependencies and integration points: depends on `crypto_sig`, `crypto_akcipher`, public-key structures, keyctl pkey params, and parser-produced payloads from X.509 and PKCS#8.

Risks: algorithm-name construction is policy-critical because it controls padding and hash semantics. Supported hash lists for ECDSA/ECRDSA/ML-DSA must track available algorithms and standards. Positive returns from verify are warned and normalized. Private-key paths must avoid leaking temporary packed keys.

Test signals: RSA pkcs1 verify/sign and pkcs1pad encrypt/decrypt, raw RSA restrictions, ECDSA x962/p1363 with allowed and disallowed hashes, ECRDSA Streebog hashes, ML-DSA raw/sha512 handling, query supported-op bits, and mismatched pkey algorithm rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/public_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/restrict.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/restrict.c

Purpose: implements asymmetric keyring restriction callbacks that decide whether a new asymmetric key may be linked into a destination keyring based on signatures, CA attributes, digital signature usage, builtin trust, and specified trusted keys/keyrings.

Important APIs/types/functions: boot parameter parsing for `ca_keys=` can restrict acceptable signer IDs or builtin keys. `restrict_link_by_signature()` verifies a new key against a trust keyring. `restrict_link_by_ca()` accepts only CA certificates with keyCertSign. `restrict_link_by_digsig()` accepts non-CA digital-signature certificates and then verifies trust. `key_or_keyring_common()` backs `restrict_link_by_key_or_keyring()` and `restrict_link_by_key_or_keyring_chain()`. Builtin/secondary/system restriction wrappers are referenced by `asymmetric_type.c`.

Control flow: restriction callbacks receive the candidate key payload and destination keyring. They validate key type, inspect public key extension flags and auth signature IDs, find a signer key in trusted material, optionally enforce builtin-key-only policy, and call `verify_signature()`. Chain mode can accept a candidate if signed by a trusted key or a key already in the destination keyring.

State and persistence: `use_builtin_keys` and `ca_keyid` are boot-time static policy state for built-in kernels. Restriction allocations can hold referenced trusted keys. Candidate key payload data is read but not owned.

Dependencies and integration points: depends on asymmetric key IDs, public-key extension flags, system keyrings, keyring restriction hooks, boot parameter parsing, and signature verification.

Risks: trust decisions hinge on exact/partial ID matching and key usage bits. Builtin/secondary trusted keyring policy is configuration-sensitive. Chain mode allowing `serial 0` must be limited to the intended restriction syntax. Missing auth IDs must reject rather than accidentally trust.

Test signals: adding CA and non-CA certificates to restricted keyrings, builtin-only restrictions, `ca_keys=id:` and `ca_keys=builtin`, chain restrictions with destination signer, rejected key usage combinations, and signature failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/restrict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest.c

Purpose: runs late-init FIPS-oriented certificate/PKCS#7 signature verification selftests for configured RSA and ECDSA vectors.

Important APIs/types/functions: `fips_signature_selftest()` creates a temporary keyring, loads DER X.509 certificates with `x509_load_certificate_list()`, parses a PKCS#7 detached signature, supplies test data, verifies it as a module signature, validates trust against the temporary keyring, frees the message, and releases the keyring. `fips_signature_selftest_init()` calls RSA and ECDSA variant hooks.

Control flow: `late_initcall()` runs after core initialization. Failures use `panic()`, making this a hard boot gate when enabled. Variant functions are compiled as real calls or inline no-ops through `selftest.h`.

State and persistence: state is temporary keyring and parsed PKCS#7 memory. No test result is persisted; success is absence of panic.

Dependencies and integration points: depends on X.509 loader, PKCS#7 parser/verifier/trust, current credentials, keyring allocation, and configured selftest vector files.

Risks: enabled selftests can prevent boot if required crypto algorithms are missing. The error message after parse failure prints `ret`, which may not contain the parse error pointer value. The temporary keyring must be released on success; panic paths intentionally stop.

Test signals: boot with RSA-only, ECDSA-only, both, and neither; deliberate malformed vector failure; missing crypto algorithm configs; and successful late-init logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest.h -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest.h

Purpose: declares shared FIPS signature selftest helpers and provides configuration-dependent stubs for RSA and ECDSA vector tests.

Important APIs/types/functions: `fips_signature_selftest()` is the shared runner. `fips_signature_selftest_rsa()` and `fips_signature_selftest_ecdsa()` are declared when their configs are enabled, otherwise defined as empty `__init` inline functions.

Control flow: `selftest.c` can call both variant hooks unconditionally; the preprocessor selects real test functions or no-ops.

State and persistence: no runtime state. The header only controls linkage.

Dependencies and integration points: included by `selftest.c`, `selftest_rsa.c`, and `selftest_ecdsa.c`; depends on config symbols from asymmetric Kconfig.

Risks: prototypes must match variant definitions. Stubs prevent link failures but can also make an expected test silently absent if config is wrong.

Test signals: build with every combination of `CONFIG_FIPS_SIGNATURE_SELFTEST_RSA` and `CONFIG_FIPS_SIGNATURE_SELFTEST_ECDSA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest_ecdsa.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest_ecdsa.c

Purpose: provides static DER/PKCS#7 test vectors and the ECDSA-specific entry point for the FIPS certificate verification selftest.

Important APIs/types/functions: `certs_selftest_ecdsa_keys` contains a P-256 ECDSA certificate. `certs_selftest_ecdsa_data` contains detached test data. `certs_selftest_ecdsa_sig` contains a PKCS#7 ECDSA/SHA-256 signature. `fips_signature_selftest_ecdsa()` passes these buffers to `fips_signature_selftest()`.

Control flow: when compiled, late init in `selftest.c` calls this function. The shared runner loads the certificate, parses the PKCS#7 signature, supplies data, verifies, and validates trust.

State and persistence: test vectors are `__initconst`, so they can be discarded after init. No persistent state remains after successful selftest.

Dependencies and integration points: depends on ECDSA P-256 public-key verification, SHA-256 hashing, PKCS#7 parser/verifier, and X.509 parser support.

Risks: DER byte arrays are opaque and easy to corrupt. Algorithm availability must match vector choices. The certificate validity dates are intentionally far future; changes to time validation policy could affect selftest assumptions.

Test signals: boot success with ECDSA selftest enabled, failure when ECDSA or SHA-256 support is absent, and vector corruption causing panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest_ecdsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest_rsa.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest_rsa.c

Purpose: provides static DER/PKCS#7 test vectors and the RSA-specific entry point for the FIPS certificate verification selftest.

Important APIs/types/functions: `certs_selftest_rsa_keys` contains a 4096-bit RSA X.509 certificate. `certs_selftest_rsa_data` contains detached test data. `certs_selftest_rsa_sig` contains a PKCS#7 signature using RSA PKCS#1 v1.5 with SHA-256. `fips_signature_selftest_rsa()` invokes the shared runner.

Control flow: when enabled, late init calls this function before returning from `fips_signature_selftest_init()`. The generic selftest path exercises X.509 loading, PKCS#7 detached verification, and trust validation.

State and persistence: vectors are `__initconst` and discarded after init. Temporary keyring and parsed message state are owned by the shared runner.

Dependencies and integration points: depends on RSA, PKCS#1 signature encoding, SHA-256, PKCS#7, and X.509 parser support.

Risks: large byte arrays are maintenance-heavy and not self-describing. Missing RSA/PKCS#1/SHA-256 crypto support causes boot panic when selftest is enabled. Any parser policy change may require vector regeneration.

Test signals: boot with RSA selftest enabled, intentional vector mutation, missing crypto algorithm configs, and successful notice logs for the RSA selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest_rsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/signature.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/signature.c

Purpose: provides shared signature object cleanup and exported asymmetric key query/verify dispatch wrappers.

Important APIs/types/functions: `public_key_signature_free()` frees all auth key IDs, signature bytes, optionally owned digest/message bytes, and the signature object. `query_asymmetric_key()` validates key type and subtype and calls subtype `query`. `verify_signature()` validates key type and subtype and calls subtype `verify_signature`.

Control flow: parsers allocate `struct public_key_signature` objects and verifier/trust code eventually frees them through this file. Keyctl query and verifier callers enter the generic asymmetric key surface, then dispatch to the concrete subtype such as `public_key_subtype`.

State and persistence: no global state. It frees per-signature heap state and reads key payload subtype pointers.

Dependencies and integration points: depends on asymmetric subtype definitions, keyctl pkey query structures, public key structures, and user-type headers. Used by X.509, PKCS#7, trust restriction, and public-key operations.

Risks: `sig->m_free` controls ownership of `sig->m`; incorrect parser setup can leak or free borrowed data. Dispatch rejects missing subtype/payload but assumes payload slot conventions are stable.

Test signals: signature objects with and without owned message buffers, multiple auth IDs, unsupported subtype operations, non-asymmetric key rejection, and normal public-key verification calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/signature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/verify_pefile.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/verify_pefile.c

Purpose: verifies Authenticode-style signatures on PE binaries by parsing the PE headers, extracting the embedded PKCS#7 signature, validating the PKCS#7 trust chain, and comparing the signed Microsoft code-signing digest with a locally computed PE digest.

Important APIs/types/functions: `pefile_parse_binary()` validates DOS/PE/optional headers, records checksum and certificate-directory offsets, and locates sections. `pefile_strip_sig_wrapper()` validates the `WIN_CERTIFICATE` wrapper and trims padding. `pefile_compare_shdrs()` canonicalizes section order. `pefile_digest_pe_contents()` hashes the PE image while excluding checksum and certificate directory. `pefile_digest_pe()` allocates the selected hash and compares digests. `verify_pefile_signature()` is the exported top-level verifier.

Control flow: verification parses PE metadata, strips the certificate wrapper, calls `verify_pkcs7_signature()` over the PKCS#7 signature with `mscode_parse()` as content callback, then computes the PE digest named by the signed content and compares it to the digest extracted from the PKCS#7 authenticated content.

State and persistence: all state is in stack `struct pefile_context`, plus a heap-duplicated expected digest freed before return. Section pointers borrow from the PE buffer. No persistent state is written.

Dependencies and integration points: depends on `linux/pe.h`, shash algorithms, PKCS#7 verification, Microsoft code-signing ASN.1 parser, and trusted keyrings supplied by callers such as kexec PE verification.

Risks: PE bounds checking is security-critical for untrusted binaries. Digest canonicalization must exactly match Authenticode, including omitted checksum/cert data and section sorting. The tail hashing path must avoid underflow around certificate table padding. Indefinite-length PKCS#7 acceptance leaves length validation to the ASN.1 layer.

Test signals: signed and unsigned PE images, PE32 and PE32+ headers, malformed header offsets, wrapper length/padding variants, unsupported cert types, section ordering edge cases, digest mismatch, unsupported hash algorithm, and trust keyring failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/verify_pefile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/verify_pefile.h -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/verify_pefile.h

Purpose: defines PE verification shared context and the Microsoft code-signing parser entry declaration.

Important APIs/types/functions: `struct pefile_context` stores parsed PE metadata such as header size, checksum offset, certificate directory offset, data directory and section counts, signature offset/length, section table pointer, and signed digest details. `kenter` and `kleave` provide local debug tracing. `mscode_parse()` is declared for use by PE verification.

Control flow: `verify_pefile.c` fills the context during PE parsing, `mscode_parser.c` fills digest fields during PKCS#7 content parsing, and PE digest comparison consumes the combined state.

State and persistence: context state is per-verification and stack-owned by the top-level verifier. The digest pointer is heap-owned until freed by the verifier.

Dependencies and integration points: includes public PKCS#7 API and hash info. Shared only by PE verification and Microsoft code-signing parser.

Risks: ownership of `digest` and borrowed section pointers must remain clear. Field width is `unsigned`, so bounds checks in the C file must guard arithmetic and offsets.

Test signals: compile coverage of PE verification, digest allocation/free paths, and debug builds that exercise kenter/kleave macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/verify_pefile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_cert_parser.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_cert_parser.c

Purpose: parses X.509 certificates into internal certificate, public-key, signature, identity, validity, and extension state for asymmetric key instantiation and PKCS#7 chain verification.

Important APIs/types/functions: `struct x509_parse_context` tracks current certificate, OIDs, raw data base, public-key parameters, key bytes, AKID fields, and name fragments. `x509_cert_parse()` drives generated ASN.1 decoders and finalizes IDs/signature params/self-signed checks. `x509_free_certificate()` frees parsed certificates. Callback functions record OIDs, algorithms, signature bits, serial, issuer/subject names, public key parameters/data, extensions, validity times, and authority key IDs. `x509_decode_time()` validates UTCTime/GeneralizedTime and converts to `time64_t`.

Control flow: decode callbacks collect raw TBS bytes, issuer/subject, serial, public key algorithm and key bytes, signature algorithm/hash, extension flags, SKID and AKID. Finalization duplicates public key material, generates issuer+serial ID, computes signature digest parameters via `x509_get_sig_params()`, and checks self-signedness when applicable.

State and persistence: parsed certificate state is heap-owned and linked by callers. Many raw fields point into the original certificate blob, so lifetime is tied to the blob held by key preparse or PKCS#7 message. Public key bytes and generated IDs are allocated and freed by `x509_free_certificate()` or transferred to key payloads.

Dependencies and integration points: depends on generated X.509 ASN.1 decoders, OID registry, public key structures, asymmetric key ID helpers, extension flag definitions, and `x509_public_key.c`.

Risks: ASN.1 bounds and ownership are security-critical. Time parsing deliberately rejects some encodings and dates before 1970. Extension parsing must correctly interpret keyUsage/basicConstraints for keyring restrictions. Unsupported algorithms return `-ENOPKG` and can prune verification chains.

Test signals: RSA/ECDSA/ECRDSA/ML-DSA certs, SKID/AKID variants, issuer+serial IDs, self-signed certs, malformed BIT STRING metadata, invalid time encodings, keyUsage/basicConstraints extension combinations, and unsupported curve/OID handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_cert_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_loader.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_loader.c

Purpose: loads a concatenated list of in-kernel DER X.509 certificates into a supplied keyring as asymmetric keys.

Important APIs/types/functions: `x509_load_certificate_list()` walks a byte array, validates that each certificate begins with a DER SEQUENCE using two-byte length form, computes each certificate length, and calls `key_create_or_update()` with type `"asymmetric"` and built-in/bypass flags.

Control flow: the function advances from certificate to certificate until the end of the list. Successful imports log the created key description; failures log the error and continue to the next parsed certificate. Dodgy list structure logs an error and returns 0.

State and persistence: imported keys persist in the target keyring. The input certificate list is borrowed and not retained directly. Created keys are marked built-in and not charged to quota.

Dependencies and integration points: depends on keyrings, asymmetric key type parsing, and callers that provide built-in certificate blobs for system, platform, or selftest keyrings.

Risks: structural parsing is intentionally simple and expects long-form DER lengths; unusual but valid DER encodings may be rejected. Parse errors return 0 after logging, so callers must rely on logs or resulting keyring contents rather than a hard error for malformed trailing data.

Test signals: concatenated multiple DER certs, short or malformed blobs, parser failure for one cert while continuing, built-in key flags, and selftest keyring loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_parser.h -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_parser.h

Purpose: defines the internal X.509 certificate representation and parser/public-key helper declarations shared by X.509 parser, public-key instantiation, PKCS#7 verification, and selftests.

Important APIs/types/functions: `struct x509_certificate` stores links, signer pointer, public key, signature, SHA-256 TBS hash, issuer/subject strings, issuer+serial ID, SKID, validity times, raw TBS/signature/serial/issuer/subject/SKID pointers and sizes, index, and verification flags. Declarations include `x509_free_certificate()`, `x509_cert_parse()`, `x509_decode_time()`, `x509_get_sig_params()`, and `x509_check_for_self_signed()`.

Control flow: parser code fills this structure, public-key preparse transfers selected fields into key payloads, and PKCS#7 verification/trust code uses signer, seen, verified, self-signed, unsupported, and blacklisted flags.

State and persistence: state is per parsed certificate. Ownership transfers are explicit in `x509_public_key.c`; otherwise `x509_free_certificate()` frees allocated members.

Dependencies and integration points: includes cleanup helpers, time types, public-key structures, asymmetric key IDs, and SHA-256 size constants.

Risks: mixed borrowed raw pointers and owned allocations require disciplined lifetime handling. Verification flags are reused across chain verification passes and must be reset where needed.

Test signals: parser/preparse ownership transfer, PKCS#7 embedded cert chain verification, blacklist hashing, and cleanup leak tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_public_key.c -->
# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_public_key.c

Purpose: converts parsed X.509 certificates into asymmetric public-key payloads and prepares certificate signatures for verification.

Important APIs/types/functions: `x509_get_sig_params()` duplicates the raw signature, computes the certificate TBS digest or assigns raw TBS data for algorithms that take data, and checks the TBS SHA-256 against the blacklist. `x509_check_for_self_signed()` compares subject/issuer and AKID/SKID/issuer IDs, then verifies self-signatures when crypto is available. `x509_key_preparse()` parses a certificate, rejects blacklisted certs, creates a key description, builds key IDs, and transfers public key/signature state into the asymmetric key payload. `x509_key_parser` registers the parser.

Control flow: asymmetric key preparse invokes this parser for X.509 blobs. Parsed certificates become `public_key_subtype` keys with `X509` id type, generated description, three possible key IDs, crypto payload, and auth signature payload. Unsupported certificate signatures can still allow key instantiation with no auth payload unless blacklisted.

State and persistence: key payloads take ownership of `cert->pub`, `cert->sig`, `cert->id`, and `cert->skid`; parser cleanup owns anything not transferred. Descriptions persist with keys. The computed SHA-256 TBS hash is only used for blacklist checks.

Dependencies and integration points: depends on shash allocation, blacklist APIs, public-key subtype, asymmetric parser registry, and X.509 parser internals.

Risks: blacklist handling intentionally sets `cert->blacklisted` but continues enough cleanup to avoid leaks. Algorithms without available hash support mark `unsupported_sig`, affecting trust restrictions. Description generation uses subject plus SKID or serial and must allocate enough hex space.

Test signals: valid X.509 key add, blacklisted TBS rejection, unsupported hash algorithm, self-signed verification success/failure, SKID versus serial description generation, and key ID lookup after import.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/asymmetric_keys/x509_public_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/Kconfig -->
# sources/distributed-fs/ceph-client/crypto/async_tx/Kconfig

Purpose: defines async_tx feature configuration for asynchronous memory copy, XOR, RAID6 P/Q syndrome generation, RAID6 recovery, and optional DMA validation-disable switches.

Important APIs/types/functions: `ASYNC_CORE` provides core async transaction support. `ASYNC_MEMCPY`, `ASYNC_XOR`, `ASYNC_PQ`, and `ASYNC_RAID6_RECOV` select the core and related primitives. `ASYNC_TX_DISABLE_PQ_VAL_DMA` and `ASYNC_TX_DISABLE_XOR_VAL_DMA` disable validation DMA paths.

Control flow: selected configs determine which async_tx objects are built and which RAID paths can use DMA offload versus synchronous fallback.

State and persistence: no runtime state; configuration persists in the built kernel.

Dependencies and integration points: integrated by async_tx Makefile, DMA engine support, RAID5/6 code, XOR blocks, and PQ helpers.

Risks: selecting high-level recovery without required lower-level primitives would break builds, so dependencies are expressed through `select`. Disabling DMA validation changes performance and exercised code paths.

Test signals: build configs for each async primitive alone and combined, DMA engine enabled/disabled, and RAID6 recovery with validation DMA switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/Makefile -->
# sources/distributed-fs/ceph-client/crypto/async_tx/Makefile

Purpose: maps async_tx Kconfig symbols to the corresponding kernel objects.

Important APIs/types/functions: builds `async_tx.o`, `async_memcpy.o`, `async_xor.o`, `async_pq.o`, `async_raid6_recov.o`, and optionally `raid6test.o` based on config symbols.

Control flow: kbuild includes each object only when its config is enabled, allowing minimal kernels to omit unused async transaction helpers.

State and persistence: no runtime state. Build outputs are controlled by kbuild.

Dependencies and integration points: tied to `crypto/async_tx/Kconfig` and RAID/DMA consumers that call exported async_tx APIs.

Risks: object selection must track exported API dependencies; missing objects cause unresolved symbols for RAID code.

Test signals: parallel builds across all config combinations and module/built-in variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_memcpy.c -->
# sources/distributed-fs/ceph-client/crypto/async_tx/async_memcpy.c

Purpose: implements `async_memcpy()`, an async_tx memory copy helper that uses DMA engine offload when possible and falls back to synchronous CPU copy.

Important APIs/types/functions: `async_memcpy()` finds a `DMA_MEMCPY` channel with `async_tx_find_channel()`, allocates `dmaengine_unmap_data`, maps source and destination pages, prepares `device_prep_dma_memcpy()`, submits with `async_tx_submit()`, or performs a `kmap_atomic()`/`memcpy()` fallback. It exports the symbol for RAID and other async_tx users.

Control flow: if a DMA channel exists, unmap data allocates, and offsets/length are DMA-aligned, it prepares and submits an async descriptor with interrupt/fence flags as requested. Otherwise it waits for `submit->depend_tx`, maps pages atomically, copies bytes, unmaps, and runs `async_tx_sync_epilog()`.

State and persistence: DMA descriptors and unmap data live until descriptor completion; synchronous state is temporary. Page contents are modified at the destination.

Dependencies and integration points: depends on DMA engine, page mapping, highmem helpers, and async_tx core dependency/callback handling.

Risks: DMA mappings must use the correct directions and be paired with descriptor unmap ownership. Atomic mappings require short, non-sleeping copy sections. Fallback must honor dependencies and callbacks to preserve async_tx semantics.

Test signals: aligned DMA path, unaligned fallback, missing channel fallback, dependency ordering, callback execution, highmem pages, and DMA mapping error instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_pq.c -->
# sources/distributed-fs/ceph-client/crypto/async_tx/async_pq.c

Purpose: implements asynchronous RAID6 P/Q syndrome generation and validation with DMA PQ offload and synchronous software fallback.

Important APIs/types/functions: global `pq_scribble_page` provides temporary P/Q storage for sync generation when one destination is omitted. `do_async_gen_syndrome()` chunks source lists according to DMA engine `dma_maxpq()` and chains descriptors. `do_sync_gen_syndrome()` calls RAID6 software syndrome routines. `async_gen_syndrome()` generates P and/or Q. `async_syndrome_val()` validates existing P/Q against recomputed values. `pq_val_chan()` optionally disables validation DMA.

Control flow: generation collapses NULL data sources, maps sources and P/Q destinations, sets `DMA_PREP_PQ_DISABLE_P/Q` when one destination is absent, and chains PQ operations if the engine cannot handle all sources at once. Sync fallback waits dependencies, substitutes zero pages and scribble destinations, then calls RAID6 software. Validation either submits `device_prep_dma_pq_val()` or recomputes P and Q into a spare page and compares.

State and persistence: `pq_scribble_page` is allocated at module init and freed at exit. Operations modify P/Q destination pages and `pqres` validation flags. DMA descriptor state is transient.

Dependencies and integration points: depends on DMA engine PQ/PQ_VAL capabilities, RAID6 tables and calls, async_tx core, async_xor helpers, and page-addressable buffers.

Risks: NULL P/Q handling is subtle; callers may omit either but not both. DMA engines differ in max source and continue support, so descriptor chaining must preserve flags and callbacks. Sync validation requires caller-provided spare and scribble buffers. `BUG_ON()` input checks can panic on invalid RAID callers.

Test signals: generation with P only, Q only, both, NULL data sources, engines with limited `dma_maxpq`, sync fallback, validation success/failure flags, disabled PQ_VAL DMA, and module init failure to allocate scribble page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_pq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_raid6_recov.c -->
# sources/distributed-fs/ceph-client/crypto/async_tx/async_raid6_recov.c

Purpose: implements async_tx RAID6 recovery for two missing data blocks or one data block plus P parity, using DMA PQ/XOR/memcpy helpers when available and software RAID6 recovery otherwise.

Important APIs/types/functions: `async_sum_product()` computes `A*x ^ B*y`; `async_mult()` multiplies a page by a GF coefficient. `__2data_recov_4()`, `__2data_recov_5()`, and `__2data_recov_n()` handle two-data recovery special cases. `async_raid6_2data_recov()` is the exported two-data recovery entry. `async_raid6_datap_recov()` is the exported data-plus-P recovery entry.

Control flow: public functions first choose sync fallback if no DMA PQ channel or no scribble buffer is available. The fallback waits dependencies, builds a pointer table with zero pages, and calls `raid6_2data_recov()` or `raid6_datap_recov()`. Async paths construct operation chains using syndrome generation, XOR, multiplication, and sum-product helpers, preserving original callback/flags for the final operation. The code temporarily rewrites `blocks` and `offs` to compute deltas, then restores them.

State and persistence: operations modify failed data/parity pages in place. Descriptor chains and scribble buffers are transient. The caller-owned `blocks` and `offs` arrays are temporarily mutated and restored.

Dependencies and integration points: depends on RAID6 Galois-field tables, async_memcpy, async_xor, async_pq, DMA engine PQ, and async_tx core.

Risks: recovery math and temporary pointer rewrites are fragile. Missing scribble buffers force sync path or reuse caller arrays. Special-case paths for 4- and 5-disk arrays exist because DMA engines may not handle zero/single-source PQ uniformly. Invalid fail indexes hit `BUG_ON()`.

Test signals: two-data recovery across 4, 5, and larger disk counts; data+P recovery; DMA and sync paths; all faila/failb orderings; NULL source pages; callback/dependency ordering; and recovered data validation against software RAID6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_raid6_recov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_tx.c -->
# sources/distributed-fs/ceph-client/crypto/async_tx/async_tx.c

Purpose: provides core async_tx descriptor submission, dependency chaining, channel switching, callback triggering, quiescing, and DMA-engine channel selection support.

Important APIs/types/functions: under `CONFIG_DMA_ENGINE`, `async_tx_init()` and `async_tx_exit()` manage global DMA engine references, and `__async_tx_find_channel()` prefers a dependent descriptor's channel when capable. `async_tx_channel_switch()` inserts an interrupt descriptor or waits when a dependency chain must move channels. `async_tx_submit()` submits or chains descriptors while respecting dependency locks. `async_trigger_callback()` schedules a callback after dependencies. `async_tx_quiesce()` waits for completion and acks descriptors.

Control flow: a new descriptor with a dependency is examined under the dependency descriptor lock. It is appended directly, submitted directly, or routed through channel switch. Channel switch uses DMA interrupt capability when available, otherwise waits synchronously. Submission acks descriptors according to `ASYNC_TX_ACK` and always acks consumed dependencies. Synchronous fallback users call `async_tx_quiesce()` before CPU work and `async_tx_sync_epilog()` after.

State and persistence: descriptor parent/next/ack state persists until DMA completion and ack. No filesystem state. Module init holds DMA engine availability while loaded.

Dependencies and integration points: depends on DMA engine descriptor conventions, async_tx flags/macros from `<linux/async_tx.h>`, RCU list headers, and exported users in async_memcpy/xor/pq/raid recovery.

Risks: dependency chaining is lock-order sensitive; submitting while holding descriptor locks can deadlock drivers, hence the disposition logic. Acking the wrong descriptor can hide live operations. Fallback waits panic on DMA error. Channel switching relies on interrupt descriptor support or safe polling.

Test signals: same-channel chaining, cross-channel switching, no-interrupt fallback, dependency ack misuse detection, callback after dependency, `ASYNC_TX_ACK` behavior, DMA errors, and configs without DMA engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/async_tx/async_tx.c -->
