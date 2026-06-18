# subset-b-007777

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/config_file.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/config_file.c

Purpose: implements Heimdal krb5 configuration parsing, tree storage, typed lookup helpers, and cleanup for text configuration files, string-backed deprecated parsing, and Apple plist configuration.

Important APIs/types/functions: `struct fileptr` abstracts `FILE *` versus string input. `_krb5_config_get_entry()` creates or finds `krb5_config_binding` nodes. Parser internals are `config_fgets()`, `parse_section()`, `parse_binding()`, `parse_list()`, and `krb5_config_parse_debug()`. Public entry points include `krb5_config_parse_file_multi()`, `krb5_config_parse_file()`, `krb5_config_file_free()`, `_krb5_config_get_next()`, `_krb5_config_vget_next()`, `krb5_config_get_list()`, `krb5_config_get_string()`, `krb5_config_get_strings()`, bool/time/int getters, and deprecated `krb5_config_parse_string_multi()`.

Control flow: text parsing reads lines, strips CR/LF, skips comments and blank lines, opens top-level `[section]` nodes, and parses `name = value` or `name = { ... }` bindings recursively until a matching `}`. Lookup walks variadic path components through list nodes and can continue from a previous binding pointer to return repeated values.

State and persistence behavior: parsing allocates a linked tree of config bindings and strings that persists until `krb5_config_file_free()`. Multi-parse appends into an existing tree. Returned strings are borrowed from that tree. Apple plist parsing converts CoreFoundation dictionaries into the same tree.

Dependencies and integration points: uses `krb5_locl.h`, krb5 error-message APIs, `issuid()`, passwd/home expansion, optional `_krb5_expand_path_tokens()`, and optional CoreFoundation. It feeds `context->cf` lookup callers throughout the Kerberos library.

Risks: malformed braces and missing `=` produce parser errors with line numbers, but duplicate names are appended and lookup order matters. Home directory expansion is security-sensitive and gated by `_krb5_homedir_access()` and `issuid()`. `_krb5_config_copy()` does not fully unwind partial allocation failures. `next_component_string()` mutates copies in place and has quote parsing edge cases.

Test signals: useful coverage includes config files with repeated keys, nested lists, comments, unmatched braces, bindings before sections, `~/` expansion under setuid-like conditions, plist parsing on Apple builds, and typed getter defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/config_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-aes.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-aes.c

Purpose: defines Heimdal AES Kerberos encryption and checksum descriptors for AES128/AES256 CTS with HMAC-SHA1-96.

Important APIs/types/functions: static `_krb5_key_type` records `keytype_aes128` and `keytype_aes256` specify key sizes, EVP CBC ciphers, AES salts, and schedule cleanup. Exported checksum descriptors `_krb5_checksum_hmac_sha1_aes128` and `_krb5_checksum_hmac_sha1_aes256` use `_krb5_SP_HMAC_SHA1_checksum`. Exported encryption descriptors `_krb5_enctype_aes128_cts_hmac_sha1` and `_krb5_enctype_aes256_cts_hmac_sha1` use `_krb5_evp_encrypt_cts`. `AES_PRF()` implements the RFC3961-style AES PRF.

Control flow: generic crypto code selects these descriptors from `_krb5_etypes`, schedules the key with `_krb5_evp_schedule()`, derives usage-specific keys, computes HMAC-SHA1 checksums, and encrypts with CTS. `AES_PRF()` hashes input with the enctype checksum, derives a `"prf"` key, encrypts the first block of the digest with an all-zero IV, and returns one block.

State and persistence behavior: no module-global mutable state beyond exported descriptor records. Per-context state lives in `krb5_crypto` key schedules and derived-key cache managed by `crypto.c`.

Dependencies and integration points: depends on OpenSSL/hcrypto EVP AES CBC functions, `krb5_derive_key()`, `krb5_data_alloc/free()`, and the generic descriptor tables in `crypto-algs.c`.

Risks: `AES_PRF()` aborts on internal failures after allocation or derivation instead of returning all errors. Correctness depends on `_krb5_evp_encrypt_cts()` handling CTS framing and on checksum truncation to 12 bytes. AES descriptors set padsize 1, so length validation is mostly in CTS code.

Test signals: round-trip AES128/AES256 encryption for one block, partial final block, multi-block CTS, keyed checksum verification, PRF known-answer tests, and derived key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-aes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-algs.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-algs.c

Purpose: central registry for compiled-in Heimdal checksum and encryption algorithms.

Important APIs/types/functions: exports `_krb5_checksum_types[]`, `_krb5_num_checksums`, `_krb5_etypes[]`, and `_krb5_num_etypes`. The arrays reference descriptors defined in the AES, DES, DES3, RC4, null, and common crypto files. Conditional entries are controlled by `HEIM_WEAK_CRYPTO`, `HEIMDAL_SMALLER`, and `DES3_OLD_ENCTYPE`.

Control flow: lookup functions in `crypto.c` linearly scan these arrays for enctype or checksum identifiers. Preference-sensitive APIs such as deprecated keytype-to-enctype mapping iterate over `_krb5_etypes`; comments note the encryption list is in reverse preference order for non-pseudo enctypes.

State and persistence behavior: exposes global mutable descriptor pointers and counts. Enabling/disabling algorithms mutates flags inside descriptor records, not these arrays.

Dependencies and integration points: included by the krb5 crypto library build; it connects all algorithm-specific files to generic APIs such as `krb5_enctype_valid()`, `krb5_create_checksum()`, `krb5_crypto_init()`, and weak-crypto toggles.

Risks: compile-time macros materially change supported algorithms. Weak DES algorithms are absent unless `HEIM_WEAK_CRYPTO` is set, while some legacy DES3 entries are included unless smaller builds suppress them. Table order affects compatibility and negotiation behavior.

Test signals: enumerate supported enctypes/checksums under each build profile, validate string-to-enctype aliases, weak-crypto enable/disable behavior, and absence/presence of legacy entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-algs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-arcfour.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-arcfour.c

Purpose: implements the Kerberos RC4-HMAC/ARCFOUR enctype and HMAC-MD5 checksum variant used for Windows compatibility.

Important APIs/types/functions: `keytype_arcfour` declares the RC4 key type with EVP RC4 scheduling. `_krb5_HMAC_MD5_checksum()` computes the draft RC4-HMAC checksum. `_krb5_checksum_hmac_md5` exports the checksum descriptor. `ARCFOUR_subencrypt()` and `ARCFOUR_subdecrypt()` implement checksum, confounder/data encryption, and integrity verification. `_krb5_usage2arcfour()` remaps selected Kerberos key usages. `ARCFOUR_encrypt()` dispatches encrypt/decrypt, `ARCFOUR_prf()` implements a SHA1-HMAC based PRF, and `_krb5_enctype_arcfour_hmac_md5` exports the enctype.

Control flow: encryption derives K1 from usage, copies it to K2, computes HMAC over confounder plus plaintext into the first 16 bytes, derives K3 from that checksum, and RC4-encrypts the remaining bytes. Decryption derives K3 from the received checksum, decrypts, recomputes the HMAC, and uses `ct_memcmp()` for integrity.

State and persistence behavior: no module-global mutable state beyond descriptors. Temporary HMAC keys are stack buffers and are zeroed before return in the subencrypt/subdecrypt paths.

Dependencies and integration points: uses generic `_krb5_internal_hmac()`, `_krb5_find_checksum()`, EVP MD5/SHA1/RC4, `ct_memcmp()`, and special-mode dispatch in `crypto.c` through the `F_SPECIAL` flag.

Risks: RC4 and MD5 are legacy algorithms. The code assumes ciphertext length includes a 16-byte checksum and does not independently guard every underflow at the algorithm boundary, relying on `crypto.c` size checks. Several internal HMAC failures call `krb5_abortx()`. Usage remapping is compatibility-critical.

Test signals: RC4-HMAC known-answer vectors, bad checksum rejection, usage remap cases for AS-REP, seal/sign/seq, and encryption/decryption with minimum legal lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-arcfour.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des-common.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des-common.c

Purpose: provides helper routines shared by single-DES and triple-DES checksum/encryption implementations.

Important APIs/types/functions: `_krb5_xor()` XORs an 8-byte DES block in place. `_krb5_des_checksum()` builds DES-encrypted keyed MD4/MD5-style checksums when DES3 old enctypes or weak crypto are enabled. `_krb5_des_verify()` decrypts and verifies those checksums. `_krb5_checksum_rsa_md5` exports the unkeyed RSA-MD5 checksum descriptor.

Control flow: keyed checksum generation writes an 8-byte random confounder, hashes confounder plus data, then CBC-encrypts the 24-byte checksum field with zero IV. Verification decrypts the 24-byte field, recomputes the digest over the recovered confounder and input data, and constant-time compares the digest portion.

State and persistence behavior: stateless except for use of the caller's scheduled EVP contexts. Temporary decrypted checksum and digest buffers are zeroed before return.

Dependencies and integration points: depends on DES block types, EVP digest/cipher contexts, `krb5_generate_random_block()`, and `ct_memcmp()`. Called by `crypto-des.c` and `crypto-des3.c`.

Risks: legacy DES checksum formats are only conditionally built and are cryptographically weak. EVP cipher contexts are reused from the key schedule, so correct IV reset is essential. Digest failure paths abort rather than returning recoverable errors.

Test signals: keyed checksum known-answer or round-trip verification tests for MD5-DES and MD5-DES3, bad checksum rejection, and weak-crypto build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des.c

Purpose: defines single-DES key handling, legacy checksum types, and DES enctypes when weak crypto support is compiled in.

Important APIs/types/functions: `krb5_DES_random_key()`, `krb5_DES_schedule_old()`, and `krb5_DES_random_to_key()` implement DES key generation, old schedule setup, parity, and weak-key avoidance. Checksum descriptors include `_krb5_checksum_crc32`, `_krb5_checksum_rsa_md4`, `_krb5_checksum_rsa_md4_des`, and `_krb5_checksum_rsa_md5_des`. Enctype descriptors include DES CBC CRC/MD4/MD5/NONE plus CFB64 and PCBC pseudo enctypes.

Control flow: random keys are generated until not weak and then parity-adjusted. Random-to-key copies input, sets odd parity, and XORs weak keys. DES CBC helpers reset IVs either to zero or the key bytes before in-place EVP encryption. CFB64 and PCBC use legacy DES APIs directly.

State and persistence behavior: descriptors are global; key schedules are per-crypto context. No durable state is written.

Dependencies and integration points: compiled under `HEIM_WEAK_CRYPTO`; references shared DES helpers, EVP DES CBC, CRC helpers, MD4/MD5, and generic crypto table registration.

Risks: all DES enctypes are marked `F_DISABLED|F_WEAK` and some are pseudo protocol helpers. Enabling them is security-sensitive. Old DES APIs and weak-key/parity behavior are compatibility-critical. Some checksum digest failures abort.

Test signals: weak-crypto enable/disable checks, DES parity and weak-key tests, CBC CRC/MD4/MD5 round trips under weak builds, and verification that disabled enctypes are rejected by default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des3.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des3.c

Purpose: defines triple-DES Kerberos key types, checksums, enctypes, and random-to-key conversion.

Important APIs/types/functions: `DES3_random_key()` generates three non-weak DES blocks with odd parity. `keytype_des3` is used for old DES3 when enabled, while `keytype_des3_derived` uses derived-key salts. `_krb5_checksum_rsa_md5_des3` and `_krb5_checksum_hmac_sha1_des3` provide keyed checksums. Enctype descriptors cover `des3-cbc-md5`, `des3-cbc-sha1`, `old-des3-cbc-sha1`, and pseudo `des3-cbc-none`. `_krb5_DES3_random_to_key()` maps 21 random bytes into 24 DES key bytes with parity and weak-key correction.

Control flow: generic crypto selects DES3 descriptors, schedules EVP `EVP_des_ede3_cbc`, applies either old or derived keying semantics, and encrypts through `_krb5_evp_encrypt()`. Random-to-key fills each 8-byte DES block from 7 bytes plus parity synthesis.

State and persistence behavior: descriptor state is global and immutable apart from flags. Key material and schedules are per-crypto context and wiped by generic cleanup.

Dependencies and integration points: depends on DES APIs, shared DES checksum helpers, EVP, salt arrays, and conditional `DES3_OLD_ENCTYPE` inclusion.

Risks: triple-DES is legacy but not marked weak in the same way as single DES. Old enctypes lack modern derived-key behavior. Random-to-key bit packing is subtle and must preserve parity and weak-key handling.

Test signals: DES3 random-to-key vectors, DES3 CBC round trips, HMAC-SHA1-DES3 checksum verification, and build variants with and without old DES3 enctypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-evp.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-evp.c

Purpose: implements the generic EVP scheduling and encryption helpers used by AES, DES, DES3, and RC4 key types.

Important APIs/types/functions: `_krb5_evp_schedule()` initializes encryption and decryption `EVP_CIPHER_CTX` objects from a key type's `evp()` cipher. `_krb5_evp_cleanup()` cleans those contexts. `_krb5_evp_encrypt()` performs normal in-place ciphering with caller IV or zero IV. `_krb5_evp_encrypt_cts()` implements CBC ciphertext stealing for AES CTS and related enctypes.

Control flow: scheduling creates separate encrypt/decrypt contexts. Normal encryption resets the IV on the selected context, then calls `EVP_Cipher()`. CTS validates length, handles exactly one block as normal CBC, and otherwise performs the final two-block CTS transformation differently for encryption and decryption while updating the caller IV when supplied.

State and persistence behavior: EVP contexts are stored in the per-key schedule allocated by `crypto.c`. The static `zero_ivec` is read-only. No file or process state is persisted.

Dependencies and integration points: depends on EVP cipher APIs and `_krb5_evp_schedule` storage defined in `crypto.h`. Called through enctype descriptor function pointers.

Risks: EVP contexts are reused, so IV reinitialization must happen before every operation. CTS boundary cases are fragile, especially one-block, two-block, and non-block-multiple lengths. Allocation failure in zero-IV setup is returned, while some EVP failures are not explicitly checked.

Test signals: CBC round trips with explicit and null IV, AES CTS known-answer tests for exact one block, partial final block, and long multi-block messages, plus IV update checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-evp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-null.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-null.c

Purpose: defines disabled null encryption and checksum descriptors used as sentinel or compatibility entries.

Important APIs/types/functions: `keytype_null` declares a zero-length key type. `NONE_checksum()` is a no-op checksum function. `_krb5_checksum_none` exports `CKSUMTYPE_NONE`. `NULL_encrypt()` is a no-op encryption function. `_krb5_enctype_null` exports `ETYPE_NULL` with `F_DISABLED`.

Control flow: generic lookup can find the null descriptors, but validation and crypto initialization reject the disabled enctype unless flags are changed. If invoked directly through descriptors, checksum and encryption return success without mutating data.

State and persistence behavior: no mutable state except the descriptor flags that can be changed by generic enable/disable functions.

Dependencies and integration points: participates in `_krb5_checksum_types[]` and `_krb5_etypes[]` as a marker. Used by APIs that default missing mappings to `ETYPE_NULL`.

Risks: accidentally enabling null encryption would remove confidentiality and integrity. The checksum size is zero, so callers must handle empty trailers correctly.

Test signals: validation should reject `ETYPE_NULL` by default, lookup should still resolve the descriptor, and null checksum size should remain zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-rand.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-rand.c

Purpose: provides krb5 random block generation backed by OpenSSL/hcrypto RAND with one-time seeding.

Important APIs/types/functions: `seed_something()` loads an optional RAND seed file, probes `RAND_status()`, optionally reads an EGD socket path from krb5 config, writes the seed file back, and reports success/failure. `krb5_generate_random_block()` is the public generator.

Control flow: first generator call locks `crypto_mutex`, seeds once, sets `rng_initialized`, unlocks, and then calls `RAND_bytes()`. Subsequent calls skip seeding and directly request random bytes. Failure to seed or generate aborts the process with `krb5_abortx()`.

State and persistence behavior: `rng_initialized` is a static process-local flag protected during initialization. The RAND seed file may be read and rewritten, so host-level RNG persistence can be affected.

Dependencies and integration points: uses RAND APIs, file I/O with `O_CLOEXEC` and `rk_cloexec()`, krb5 config lookup for `libdefaults/egd_socket`, and the Heimdal mutex abstraction. All random key, confounder, and checksum confounder generation flows depend on this function.

Risks: fatal abort on RNG failure is deliberate but high impact. Seed-file entropy is explicitly added with zero entropy estimate. The EGD path is legacy and config-sensitive. Correct mutex use is important for threaded callers.

Test signals: single and concurrent first-call initialization, RAND failure injection, seed-file open/read/write behavior, and generation of requested byte lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-rand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto.c

Purpose: implements the generic Heimdal krb5 crypto API: enctype/checksum lookup, key scheduling, checksums, encryption/decryption, IOV crypto, key derivation, crypto context lifecycle, PRF, weak-crypto toggles, and length/overhead helpers.

Important APIs/types/functions: key lifecycle includes `krb5_generate_random_keyblock()`, `krb5_random_to_key()`, `krb5_crypto_init()`, `krb5_crypto_destroy()`, `_krb5_free_key_data()`, `_key_schedule()`, `_get_derived_key()`, and `krb5_derive_key()`. Checksum APIs include `_krb5_internal_hmac()`, `_krb5_SP_HMAC_SHA1_checksum()`, `krb5_create_checksum()`, `krb5_verify_checksum()`, and IOV checksum helpers. Encryption APIs include `krb5_encrypt_ivec()`, `krb5_decrypt_ivec()`, `krb5_encrypt_iov_ivec()`, `krb5_decrypt_iov_ivec()`, and `EncryptedData` wrappers.

Control flow: public APIs find descriptor records from `crypto-algs.c` and dispatch by flags. Derived enctypes build confounder plus plaintext, checksum with integrity usage, encrypt with encryption usage, and append trailer. Old enctypes put checksum inside encrypted data. Special RC4 delegates framing to the RC4 algorithm. Decryption reverses each format and verifies integrity before returning plaintext.

State and persistence behavior: `krb5_crypto` stores the selected enctype, copied base key, optional key schedule, and an expandable cache of derived keys by usage. Global descriptor flags can be mutated by enable/disable APIs, affecting later callers process-wide.

Dependencies and integration points: integrates all algorithm descriptors, ASN.1 `Checksum`/`EncryptedData` types, EVP helpers, n-fold, store-int, random generation, `ct_memcmp`, and krb5 error-message APIs.

Risks: this is security-critical code with many size and padding invariants. Some allocation paths use `ENOMEM` directly, some internal failures abort, and `_get_derived_key()` does not check every copy/derive return before publishing a cache entry. Descriptor flag mutation is global and not synchronized. IOV code copies buffers into temporary contiguous memory and must preserve data/sign-only ordering.

Test signals: known-answer vectors for each enctype, round-trip encrypt/decrypt with bad-integrity cases, IOV header/padding/trailer sizing, checksum type mismatch handling, derived-key cache reuse, weak-crypto toggles, PRF/CF2 tests, and malformed ciphertext size rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto.h -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto.h

Purpose: internal krb5 crypto interface header defining descriptor structures, flags, usage macros, external algorithm descriptors, and EVP schedule storage.

Important APIs/types/functions: defines `_krb5_key_data`, `krb5_crypto_data`, `F_KEYED`, `F_CPROOF`, `F_DERIVED`, `F_VARIANT`, `F_PSEUDO`, `F_SPECIAL`, `F_DISABLED`, and `F_WEAK`. Defines `salt_type`, `_krb5_key_type`, `_krb5_checksum_type`, `_krb5_encryption_type`, and `_krb5_evp_schedule`. Declares checksum and enctype descriptor symbols and the `_krb5_checksum_types`/`_krb5_etypes` registries.

Control flow: not executable, but it defines the function-pointer contract used by `crypto.c`: key randomization, scheduling, cleanup, checksum/verify, encrypt, EVP cipher lookup, string-to-key, and PRF. Usage macros map Kerberos key usages into encryption, integrity, and checksum constants.

State and persistence behavior: structures describe per-crypto key state and process-global descriptor records. `krb5_crypto_data` persists selected enctype, base key, and cached usage keys until destroy.

Dependencies and integration points: consumed by all `crypto-*.c` files and `crypto.c`; depends on krb5 and EVP types from `krb5_locl.h`.

Risks: any ABI or semantic change here affects all crypto descriptors. Flag combinations define security behavior, including disabled and weak algorithm handling. Function pointers must match descriptor sizes and key schedule layout.

Test signals: build coverage across algorithm macros, descriptor table integrity checks, and compile-time validation that every declared descriptor is provided in the selected build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/data.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/data.c

Purpose: implements allocation, copying, freeing, and comparison helpers for `krb5_data` buffers.

Important APIs/types/functions: `krb5_data_zero()`, `krb5_data_free()`, `krb5_free_data()`, `krb5_data_alloc()`, `krb5_data_realloc()`, `krb5_data_copy()`, `krb5_copy_data()`, `krb5_data_cmp()`, and `krb5_data_ct_cmp()`.

Control flow: allocation helpers set `data` and `length`, accepting zero-length allocations as successful even with null pointers. Copy helpers allocate then `memmove()` input. Free helpers free content and zero the structure. Compare helpers first compare lengths, then use `memcmp()` or `ct_memcmp()`.

State and persistence behavior: no global state. Ownership is caller-managed; allocated buffers persist until the matching free helper.

Dependencies and integration points: used across krb5 crypto, encoding, and ASN.1 copy paths. `krb5_copy_data()` delegates to `der_copy_octet_string()`. Constant-time compare integrates with roken `ct_memcmp()`.

Risks: length parameters are `int` for allocation/reallocation but `size_t` for copy, so oversized lengths need caller discipline. `krb5_data_cmp()` subtracts lengths and may truncate on unusual size ranges. Secrets freed through `krb5_data_free()` are not wiped unless caller does it first.

Test signals: zero-length allocation/copy, realloc growth/shrink, copy failure cleanup, constant-time compare equality/inequality, and ownership of `krb5_copy_data()` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/expand_path.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/expand_path.c

Purpose: expands `%{TOKEN}` path tokens for krb5 configuration paths across Unix and Windows.

Important APIs/types/functions: platform token expanders include `_expand_temp_folder()`, `_expand_bin_dir()`, `_expand_userid()`, `_expand_csidl()`, `_expand_path()`, `_expand_extra_token()`, and `_expand_null()`. The static `tokens[]` table maps names such as `LIBDIR`, `BINDIR`, `LIBEXEC`, `SBINDIR`, `TEMP`, `USERID`, `uid`, and `null`. Public internals are `_krb5_expand_path_tokens()` and `_krb5_expand_path_tokensv()`.

Control flow: `_krb5_expand_path_tokensv()` first copies variadic extra token pairs, then scans the input string for `%{`, appends literal spans or expanded token values, and reallocates the output buffer as it grows. `_expand_token()` checks syntax, searches caller-provided extra tokens first, then built-in tokens.

State and persistence behavior: no global mutable state. The returned path is heap-allocated and caller-owned. On Windows, output slashes are normalized to backslashes.

Dependencies and integration points: used by config file path handling when `KRB5_USE_PATH_TOKENS` is enabled. Unix paths use compile-time install directories and UID/TEMP helpers; Windows paths use CSIDL, token/SID APIs, module path lookup, and package directories.

Risks: token matching uses `strncmp()` against token length without checking exact built-in token length, so prefix ambiguities would matter if added. Varargs must be key/value pairs terminated by NULL. Setuid environment handling in Unix `_expand_temp_folder()` appears inverted and deserves scrutiny. Repeated reallocs are simple but potentially inefficient.

Test signals: literal-only paths, missing `}`, unknown token, extra token override, empty input, all built-in tokens, Windows slash conversion, and allocation-failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/expand_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/keyblock.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/keyblock.c

Purpose: manages `krb5_keyblock` initialization, copying, access, and secure-ish cleanup.

Important APIs/types/functions: `krb5_keyblock_zero()`, `krb5_free_keyblock_contents()`, `krb5_free_keyblock()`, `krb5_copy_keyblock_contents()`, `krb5_copy_keyblock()`, `krb5_keyblock_get_enctype()`, and `krb5_keyblock_init()`.

Control flow: initialization verifies requested key size with `krb5_enctype_keysize()`, copies caller bytes into a new `krb5_data`, and sets keytype. Freeing wipes key bytes with `memset()`, frees the data, and resets keytype to `KRB5_ENCTYPE_NULL`. Copying delegates content copying to generated ASN.1 copy helpers.

State and persistence behavior: no global state. Key bytes are heap-owned by the keyblock and remain until explicit free. Free content wipes current bytes before release.

Dependencies and integration points: used by crypto initialization, random key generation, derived-key caching, and external callers constructing keys. Depends on `krb5_data_*`, `copy_EncryptionKey()`, and enctype metadata from `crypto.c`.

Risks: wiping via `memset()` may be optimized out by some compilers unless the broader build guarantees secure memset behavior. `krb5_keyblock_init()` returns `KRB5_PROG_ETYPE_NOSUPP` for bad size, which conflates size and unsupported-type errors.

Test signals: correct size enforcement per enctype, copy independence, free zeroing behavior under instrumentation, and null-safe free calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/keyblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/n-fold.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/n-fold.c

Purpose: implements the Kerberos n-fold operation used by RFC3961 key derivation.

Important APIs/types/functions: internal `rr13()` rotates a bitstring right by 13 bits while duplicating into two buffers. `add1()` adds one's-complement byte arrays with carry handling optimized over aligned 32-bit chunks. `_krb5_n_fold()` folds an input byte string into an output key-sized byte string.

Control flow: `_krb5_n_fold()` allocates temporary storage sized to twice the larger of input and output plus rotation buffers, zeroes the output, copies the input, repeatedly adds output-sized chunks into the result, rotates the source by 13 bits, and continues until the cycle completes with no remainder.

State and persistence behavior: stateless. Temporary buffers are zeroed before free because they may contain key derivation material.

Dependencies and integration points: called by `_krb5_derive_key()` in `crypto.c`. Uses network-byte-order helpers for aligned arithmetic.

Risks: bit-level correctness is critical and hard to review. `add1()` assumes inputs are aligned to 4 bytes, which is true for malloc-backed buffers but important to preserve. Length zero inputs are not guarded here and should be rejected by callers.

Test signals: RFC3961 n-fold known-answer vectors for multiple input/output sizes, valgrind/ASan coverage for non-multiple-of-4 sizes, and derived-key known answers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/n-fold.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/store-int.c -->
# sources/distributed-fs/openafs/src/external/heimdal/krb5/store-int.c

Purpose: provides fixed-width big-endian integer serialization helpers for internal krb5 code.

Important APIs/types/functions: `_krb5_put_int()` stores the low `size` bytes of an unsigned long into a buffer in big-endian order. `_krb5_get_int()` reads `size` bytes from a buffer into an unsigned long in big-endian order.

Control flow: put walks from last output byte to first while shifting the value right. Get walks forward, left-shifting the accumulator and adding each input byte.

State and persistence behavior: stateless and purely buffer-local.

Dependencies and integration points: used by crypto key-usage derivation constants and other internal store/load code that needs network-order integer fields.

Risks: no buffer length validation and no overflow reporting if `size` exceeds the meaningful width of `unsigned long`; callers must pass valid sizes. Return type reports bytes processed, not an error channel.

Test signals: round trips for 1 to 5 byte values, truncation behavior for oversized values, and expected key-usage constant encoding in crypto derivation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/krb5/store-int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/base64.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/base64.c

Purpose: implements simple base64 encode/decode helpers for roken portability users.

Important APIs/types/functions: `base64_chars[]` is the alphabet. `pos()` returns the alphabet index. `base64_encode()` allocates and returns a NUL-terminated encoded string. `token_decode()` decodes a 4-character quantum and tracks padding. `base64_decode()` decodes into caller-provided storage.

Control flow: encoding groups up to three bytes into a 24-bit integer, emits four alphabet characters, and substitutes `=` padding when input runs short. Decoding advances in four-character chunks while input chars are alphabet or `=`, validates padding order, and writes one to three bytes per quantum.

State and persistence behavior: stateless. Encode allocates output that the caller owns; decode writes into caller-provided memory without allocating.

Dependencies and integration points: declared by `base64.h`; used by any roken/Heimdal code needing compact binary-to-text conversion.

Risks: `base64_decode()` does not take an output buffer length, so callers must preallocate enough space. `pos()` returns -1 for invalid chars, but the loop largely filters characters before decoding. Encoded allocation uses a compact formula and rejects negative or huge `int` sizes.

Test signals: RFC base64 vectors, zero-length input, one/two-byte padding, invalid padding position, invalid characters, and caller buffer sizing tests under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/base64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/base64.h -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/base64.h

Purpose: public roken header for base64 helpers.

Important APIs/types/functions: defines `ROKEN_LIB_FUNCTION` and `ROKEN_LIB_CALL` defaults when not already provided. Declares `base64_encode(const void *, int, char **)` and `base64_decode(const char *, void *)`.

Control flow: not executable. It establishes calling convention decoration, especially for Windows builds.

State and persistence behavior: no state. The function contract implies encode allocates a string through `char **`, while decode writes into caller-owned memory.

Dependencies and integration points: included by `base64.c` and consumers that need roken base64 without pulling a larger header.

Risks: decode declaration has no output buffer length, which makes safe use dependent on caller-side length calculation. The header exposes `int` sizes, limiting very large encodings.

Test signals: compile with and without pre-defined roken export macros, C and C++ inclusion compatibility if applicable, and ABI matching with `base64.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/base64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/cloexec.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/cloexec.c

Purpose: provides helpers to mark file descriptors, `FILE *`, and directory streams close-on-exec.

Important APIs/types/functions: `rk_cloexec(int fd)`, `rk_cloexec_file(FILE *f)`, and `rk_cloexec_dir(DIR *d)`.

Control flow: on platforms with `fcntl`, `rk_cloexec()` reads existing descriptor flags with `F_GETFD` and writes them back with `FD_CLOEXEC` set. File and directory helpers convert to descriptors with `fileno()` and `dirfd()` where available.

State and persistence behavior: mutates kernel descriptor flags for the current process. No heap or global state.

Dependencies and integration points: used by RNG seed-file code and other roken callers that open descriptors before possible exec. Depends on `roken.h`, `fcntl`, and non-Windows directory APIs.

Risks: failures are silently ignored, so callers cannot distinguish unsupported platforms or bad descriptors. On platforms lacking `fcntl`, helpers are no-ops. Race-free close-on-exec still requires using `O_CLOEXEC` at open when possible.

Test signals: descriptor flag inspection after calls, invalid descriptor no-crash behavior, and platform builds without `HAVE_FCNTL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/cloexec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/ct.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/ct.c

Purpose: implements a constant-time memory equality check.

Important APIs/types/functions: `ct_memcmp(const void *p1, const void *p2, size_t len)` returns 0 if equal and nonzero otherwise.

Control flow: iterates over all bytes, ORs every XOR difference into an accumulator, and returns `!!r`. It does not early-exit on the first difference.

State and persistence behavior: stateless and read-only over the input buffers.

Dependencies and integration points: used by krb5 checksum verification paths and `krb5_data_ct_cmp()` to avoid leaking the position of the first mismatching byte.

Risks: the return value is equality-oriented, not lexicographic like `memcmp()`, and the comments warn it must not be used for ordering. Constant-time behavior still depends on compiler code generation but the source avoids data-dependent branches.

Test signals: equal/unequal buffers, zero length, differing first and last byte, and consumers that expect only zero/nonzero semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/ct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/daemon.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/daemon.c

Purpose: supplies a BSD-style `daemon()` implementation when the platform lacks one.

Important APIs/types/functions: `daemon(int nochdir, int noclose)` is compiled only under `#ifndef HAVE_DAEMON`.

Control flow: forks and exits the parent, calls `setsid()` in the child, optionally changes directory to `/`, and optionally redirects stdin/stdout/stderr to `_PATH_DEVNULL`.

State and persistence behavior: changes process session, working directory, and standard descriptors. No heap state.

Dependencies and integration points: roken portability layer for daemons in Heimdal/OpenAFS components. Depends on fork, setsid, chdir, open, dup2, close, and path constants.

Risks: classic single-fork daemonization leaves some traditional double-fork edge cases unhandled. `chdir()` and `dup2()` failures are not propagated except for fork/setsid. Not compiled where the system daemon exists.

Test signals: child process behavior, parent exit, descriptor redirection, `nochdir`/`noclose` options, and build coverage for fallback-only platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/ecalloc.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/ecalloc.c

Purpose: provides an allocation wrapper like `calloc()` that terminates the process on allocation failure.

Important APIs/types/functions: `ecalloc(size_t number, size_t size)`.

Control flow: calls `calloc(number, size)`, and if it returns NULL for a nonzero product, calls `errx(1, ...)`; otherwise returns the pointer.

State and persistence behavior: returns heap memory owned by the caller. On failure, process state ends via `errx`.

Dependencies and integration points: uses roken export macros and BSD `errx()`. Intended for code paths that prefer fatal allocation failure over error plumbing.

Risks: `number * size` can overflow in the diagnostic and zero/nonzero check, so huge overflowed requests could be mishandled depending on `calloc()` behavior. Fatal exit is unsuitable for library paths that must report errors.

Test signals: successful zeroed allocation, zero-size behavior, and failure injection verifying fatal diagnostic paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/ecalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/emalloc.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/emalloc.c

Purpose: provides a `malloc()` wrapper that exits on nonzero allocation failure.

Important APIs/types/functions: `emalloc(size_t sz)`.

Control flow: calls `malloc(sz)`, calls `errx(1, ...)` if NULL and `sz != 0`, and otherwise returns the pointer.

State and persistence behavior: returns caller-owned heap memory or terminates the process.

Dependencies and integration points: roken helper for programs that use fatal allocation semantics; depends on BSD err compatibility.

Risks: fatal exit is problematic in reusable library code. Zero-size allocation may return NULL without error, mirroring C library behavior.

Test signals: normal allocation/free, zero-size allocation tolerance, and allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/emalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/erealloc.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/erealloc.c

Purpose: provides a `realloc()` wrapper that exits on nonzero allocation failure.

Important APIs/types/functions: `erealloc(void *ptr, size_t sz)`.

Control flow: calls `realloc(ptr, sz)`, calls `errx(1, ...)` if NULL and `sz != 0`, and returns the new pointer otherwise.

State and persistence behavior: mutates heap ownership exactly like `realloc()`: on success the old pointer is invalid, on zero-size behavior depends on the C library, and on failure this wrapper exits.

Dependencies and integration points: roken fatal allocation helper used by utilities that avoid explicit allocation error handling.

Risks: callers lose recoverability on memory pressure. As with any `realloc`, assigning directly to the original pointer is only safe because this wrapper exits on failure.

Test signals: grow/shrink behavior, NULL-as-malloc behavior, zero-size behavior, and failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/erealloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/err.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/err.c

Purpose: implements the BSD `err()` wrapper where the platform lacks one or roken supplies its own.

Important APIs/types/functions: `err(int eval, const char *fmt, ...)`.

Control flow: starts a varargs list, delegates to `verr(eval, fmt, ap)`, and ends the list. `verr()` is expected to print the message, include errno text, and exit with `eval`.

State and persistence behavior: no local persistent state; process exits through `verr()`.

Dependencies and integration points: part of roken err/warn portability family, used by fatal allocation helpers and command-line tools.

Risks: behavior depends on the linked `verr()` implementation. Because it exits, it must not be used in recoverable library flows.

Test signals: formatted output includes errno text, exit status is preserved, and varargs forwarding works with null and non-null formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/errx.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/errx.c

Purpose: implements the BSD `errx()` wrapper that exits with a formatted message but without errno text.

Important APIs/types/functions: `errx(int eval, const char *fmt, ...)`.

Control flow: starts varargs, delegates to `verrx(eval, fmt, ap)`, and ends varargs. `verrx()` handles output and exit.

State and persistence behavior: no local state; terminates process through `verrx()`.

Dependencies and integration points: roken err compatibility function used by `emalloc()`, `ecalloc()`, and `erealloc()`.

Risks: fatal semantics are unsuitable for library code that should return errors. Output behavior depends on `verrx()` and global program name state.

Test signals: formatted output without errno suffix, exit status, and varargs forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/errx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/flock.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/flock.c

Purpose: provides a portable `flock()`-style advisory locking fallback as `rk_flock()` when the system lacks native `flock`.

Important APIs/types/functions: `rk_flock(int fd, int operation)` supports `LOCK_SH`, `LOCK_EX`, `LOCK_UN`, and `LOCK_NB`.

Control flow: on POSIX with `fcntl`, builds a whole-file `struct flock`, chooses blocking or nonblocking command, maps lock operations to read/write/unlock locks, and calls `fcntl()`. On Windows, maps the fd to a HANDLE and uses `LockFileEx()`/`UnlockFileEx()` with whole-file ranges and errno translation. Otherwise returns -1.

State and persistence behavior: mutates OS advisory lock state for the file description or handle. No heap state.

Dependencies and integration points: roken compatibility for code expecting BSD-style file locking across Unix and Windows.

Risks: `fcntl` locks and BSD `flock` locks have different semantics around process ownership and descriptor inheritance. Windows error mapping is approximate. Unsupported fallback returns -1 without setting a specific errno in the final branch.

Test signals: shared/exclusive/unlock behavior, nonblocking conflict errors, invalid operation EINVAL, and Windows errno translation if applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/freeaddrinfo.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/freeaddrinfo.c

Purpose: fallback implementation of `freeaddrinfo()`.

Important APIs/types/functions: `freeaddrinfo(struct addrinfo *ai)`.

Control flow: iterates the linked list, frees `ai_canonname`, frees `ai_addr`, saves `ai_next`, frees the node, and advances.

State and persistence behavior: releases heap state produced by the fallback `getaddrinfo()` implementation or compatible allocations.

Dependencies and integration points: companion to roken `getaddrinfo()` fallback; included where the platform lacks native `freeaddrinfo`.

Risks: assumes `ai_canonname` and `ai_addr` are individually heap allocated. Safe for NULL input. Mixing with a system `getaddrinfo()` implementation that uses different allocation rules would be unsafe, so configure guards must be correct.

Test signals: freeing NULL, single-node and multi-node lists, canonname-only first entry, and ASan leak/double-free checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/freeaddrinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/gai_strerror.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/gai_strerror.c

Purpose: fallback `gai_strerror()` mapping getaddrinfo error codes to strings.

Important APIs/types/functions: static `errors[]` maps available `EAI_*` constants to messages. `gai_strerror(int ecode)` performs lookup.

Control flow: linear scan over the table until a matching code or terminating NULL string, returning a static string.

State and persistence behavior: read-only static table; returned pointers are static storage.

Dependencies and integration points: companion to fallback address-resolution APIs and callers that format `getaddrinfo()` failures.

Risks: exact available error codes are compile-time dependent. Unknown codes collapse to a generic message, so diagnostics may be less precise than native libc.

Test signals: mappings for all configured `EAI_*` constants and unknown-code fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/gai_strerror.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getaddinfo.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/getaddinfo.c

Purpose: fallback `getaddrinfo()` implementation for IPv4 and optional IPv6 platforms.

Important APIs/types/functions: `get_port_protocol_socktype()` resolves services and socket/protocol hints. `add_one()`, `const_v4()`, and `const_v6()` build `addrinfo` nodes. `get_null()` returns wildcard or loopback addresses. `get_number()` parses numeric hosts. `add_hostent()` and `get_nodes()` resolve names through hostent APIs. Public `getaddrinfo()` orchestrates validation and lookup.

Control flow: public entry validates node/service presence and supported families, resolves service to port/protocol/socktype, tries numeric node parsing, optionally refuses nonnumeric hosts under `AI_NUMERICHOST`, otherwise resolves hostnames, or returns passive/loopback entries for null node.

State and persistence behavior: allocates a linked `addrinfo` list with heap-owned address and optional canonical name. Caller releases it with `freeaddrinfo()`. No global state except resolver/library state used by hostent and service lookups.

Dependencies and integration points: uses `getservbyname()`, `getprotobynumber()`, `inet_pton()`, `getipnodebyname()`, `hostent_find_fqdn()`, and IPv6 feature macros. Provides portability for OpenAFS/Heimdal networking code.

Risks: fallback semantics are simpler than modern libc, especially `AI_ADDRCONFIG`, multiple protocols, canonical name handling, and thread safety of resolver APIs. Some error paths may leak a canonical name if later address additions fail. Numeric service parsing uses `strtol()` with limited validation.

Test signals: null node passive/non-passive, numeric IPv4/IPv6, hostname resolution, service names for tcp/udp, `AI_CANONNAME`, `AI_NUMERICHOST`, unsupported family, and cleanup on partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getaddinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getdtablesize.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/getdtablesize.c

Purpose: fallback implementation of `getdtablesize()` returning a process file-descriptor limit.

Important APIs/types/functions: `getdtablesize(void)`.

Control flow: tries `sysconf(_SC_OPEN_MAX)`, else `getrlimit(RLIMIT_NOFILE)`, else `sysctl(KERN_MAXFILES)`, then falls back to `OPEN_MAX` or `NOFILE` macros if available.

State and persistence behavior: read-only query of OS/resource state; no heap or global mutation.

Dependencies and integration points: portability shim for code that needs descriptor table bounds, often before closing descriptors in daemon setup.

Risks: may return -1 if no method or macro is available. Resource limits can change after the call. Some fallback paths use system-wide max rather than per-process soft limit.

Test signals: platform builds for each configured path, expected value under adjusted `RLIMIT_NOFILE`, and fallback macro behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getdtablesize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getnameinfo.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/getnameinfo.c

Purpose: fallback `getnameinfo()` implementation for formatting socket addresses into host and service names.

Important APIs/types/functions: internal `doit()` handles one address family. Public `getnameinfo()` dispatches `AF_INET` and optional `AF_INET6`.

Control flow: for host output, numeric mode uses `inet_ntop()`, otherwise attempts reverse lookup with `gethostbyaddr()`, applies `NI_NOFQDN`, and falls back to numeric unless `NI_NAMEREQD` is set. For service output, numeric mode prints the port, otherwise `getservbyport()` is tried with tcp or udp based on `NI_DGRAM`.

State and persistence behavior: writes into caller-provided host/service buffers. No heap state.

Dependencies and integration points: used by networking code on platforms missing native `getnameinfo`; depends on resolver functions, service database, `inet_ntop()`, and `hostent_find_fqdn()`.

Risks: does not verify `salen` against family-specific sockaddr sizes. Resolver APIs may be non-thread-safe. Buffer truncation is delegated to `strlcpy()`/`snprintf()` rather than reported as `EAI_OVERFLOW`.

Test signals: numeric and reverse host paths, `NI_NAMEREQD`, `NI_NOFQDN`, numeric and named services, `NI_DGRAM`, IPv6 build coverage, and unsupported family errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getnameinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getopt.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/getopt.c

Purpose: BSD-derived fallback implementation of `getopt()`.

Important APIs/types/functions: global variables `opterr`, `optind`, `optopt`, `optreset`, and `optarg`; public `getopt(int nargc, char * const *nargv, const char *ostr)`.

Control flow: maintains static scanning pointer `place`, starts a new argv element when needed, stops at non-option or `--`, validates option characters against `ostr`, handles options with required arguments, returns `?` or `:` according to leading-colon rules, and prints diagnostics when `opterr` permits.

State and persistence behavior: uses global and static parser state across calls; `optreset` resets scanning.

Dependencies and integration points: command-line portability layer for tools that cannot rely on libc `getopt`.

Risks: global state is not thread-safe. Only short options are supported. Error messages go to stderr and derive program name from argv[0]. Behavior should match BSD enough for callers but may differ from GNU extensions.

Test signals: grouped short options, options with adjacent and separate arguments, missing arguments with/without leading colon, illegal options, `--`, `optreset`, and non-option termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getprogname.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/getprogname.c

Purpose: fallback support for retrieving the process program name.

Important APIs/types/functions: optionally defines global `const char *__progname`; implements `getprogname(void)` when unavailable.

Control flow: returns the `__progname` pointer.

State and persistence behavior: uses process-global `__progname`, which must be set elsewhere by startup or roken support code.

Dependencies and integration points: used by err/warn style diagnostics and tools expecting BSD `getprogname()`.

Risks: may return NULL or stale data if `__progname` is not initialized. Global state is not owned by this file.

Test signals: program-name initialization path, fallback build without native `getprogname`, and diagnostic users that consume the returned pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/getprogname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/gettimeofday.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/gettimeofday.c

Purpose: fallback `gettimeofday()` implementation for platforms missing it.

Important APIs/types/functions: `gettimeofday(struct timeval *tp, void *ignore)` under `#ifndef HAVE_GETTIMEOFDAY`.

Control flow: on Windows, reads `FILETIME`, converts from Windows epoch 100ns units to Unix epoch microseconds, and fills `tv_sec`/`tv_usec`. On other fallback platforms, uses `time(NULL)` and sets microseconds to zero.

State and persistence behavior: read-only wall-clock query into caller-provided struct.

Dependencies and integration points: portability layer for code needing `struct timeval` timestamps.

Risks: non-Windows fallback has only one-second precision. No null pointer guard. Uses platform-specific integer suffixes in Windows code.

Test signals: Windows epoch conversion sanity, monotonic-ish wall-clock progression, microsecond range validation, and fallback non-Windows precision expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/gettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/hex.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/hex.c

Purpose: implements hexadecimal encoding and decoding helpers.

Important APIs/types/functions: `hexchar[]` is the uppercase alphabet. `pos()` maps a hex digit to a nibble after `toupper()`. `hex_encode()` allocates an uppercase hex string. `hex_decode()` decodes into caller-provided storage.

Control flow: encoding checks size overflow, allocates `size * 2 + 1`, emits two hex chars per byte, and NUL-terminates. Decoding checks output capacity using rounded-up input length, handles odd-length input by treating the first digit as a low byte, then decodes pairs.

State and persistence behavior: stateless. Encode output is caller-owned; decode writes into caller storage.

Dependencies and integration points: declared by `hex.h` and available as `rk_hex_encode`/`rk_hex_decode` through macros.

Risks: `hex_decode()` does not reject non-hex characters; `pos()` returns -1, which is then folded into output nibbles. Odd-length behavior may surprise callers expecting strict pair input.

Test signals: uppercase output, lowercase decode, odd-length decode, invalid-character behavior, output-length rejection, and zero-length input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/hex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/hex.h -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/hex.h

Purpose: public roken header for hex encode/decode helpers.

Important APIs/types/functions: defines export/calling macros if missing, maps `hex_encode` to `rk_hex_encode` and `hex_decode` to `rk_hex_decode`, and declares `hex_encode(const void *, size_t, char **)` plus `hex_decode(const char *, void *, size_t)`.

Control flow: not executable; it controls symbol naming and prototypes.

State and persistence behavior: no state. The API contract makes encode allocate caller-owned text and decode consume caller-provided storage with a length.

Dependencies and integration points: included by `hex.c` and consumers needing stable roken-prefixed symbols while using convenient names in source.

Risks: macro renaming can surprise code that needs the unprefixed names. Decode returns `ssize_t`, so callers must handle negative errors.

Test signals: compile/link with macro-renamed symbols, prototype compatibility on Windows and Unix, and inclusion alongside other roken headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/hex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/inet_ntop.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/inet_ntop.c

Purpose: fallback implementation of `inet_ntop()` for IPv4 and optional IPv6.

Important APIs/types/functions: `inet_ntop_v4()`, `inet_ntop_v6()` under `HAVE_IPV6`, and public `inet_ntop(int af, const void *src, char *dst, size_t size)`.

Control flow: IPv4 converts the network-order address to host order and writes dotted decimal. IPv6 prints eight 16-bit hex groups and compresses a run of zero groups using `::` with a simple first-run strategy. Public dispatch sets `EAFNOSUPPORT` for unsupported families.

State and persistence behavior: writes into caller-provided buffer only.

Dependencies and integration points: used by fallback `getnameinfo()` and address formatting callers on platforms without native support.

Risks: IPv6 zero-compression implementation is simpler than modern canonical formatting and may not choose the longest run in all cases. Buffer size checks require `INET_ADDRSTRLEN` or `INET6_ADDRSTRLEN`. No null pointer guards.

Test signals: IPv4 formatting, insufficient buffer ENOSPC, IPv6 normal and compressed addresses, all-zero IPv6, and unsupported family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/inet_ntop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/inet_pton.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/inet_pton.c

Purpose: fallback implementation of `inet_pton()`.

Important APIs/types/functions: `inet_pton(int af, const char *src, void *dst)`.

Control flow: on Winsock, duplicates the input string, dispatches to `WSAStringToAddress()` for IPv4 or IPv6, copies parsed address bytes, maps invalid input to 0 and other errors to -1 with errno. On non-Winsock fallback, only `AF_INET` is supported and delegated to `inet_aton()`.

State and persistence behavior: writes parsed address bytes to caller storage; temporary duplicated string is freed.

Dependencies and integration points: companion to fallback address-resolution code. Uses Winsock APIs on Windows and `inet_aton()` elsewhere.

Risks: non-Windows fallback lacks IPv6 parsing even if other code has IPv6 conditionals, so configure selection must avoid this fallback where IPv6 is needed. Windows path returns 0 for allocation failure after setting ENOMEM, which differs from usual -1 error semantics.

Test signals: valid/invalid IPv4, valid/invalid IPv6 on Winsock, unsupported family, null source, and errno mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/inet_pton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/issuid.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/issuid.c

Purpose: detects whether the process is running with set-user-ID or set-group-ID privilege transitions.

Important APIs/types/functions: `issuid(void)`.

Control flow: uses `issetugid()` where available. Otherwise compares real/effective UID and real/effective GID, returning 1 for UID mismatch, 2 for GID mismatch, or 0.

State and persistence behavior: read-only process credential query.

Dependencies and integration points: used by krb5 config and path logic to avoid trusting environment variables in privileged execution.

Risks: fallback detection is less comprehensive than `issetugid()` on platforms with saved IDs or other privilege mechanisms. Return values encode which mismatch was found, but most callers treat any nonzero as true.

Test signals: normal process returns 0, simulated/elevated UID and GID mismatch behavior where possible, and config code refusing HOME/env trust when nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/issuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/localtime_r.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/localtime_r.c

Purpose: fallback `localtime_r()` implementation.

Important APIs/types/functions: `localtime_r(const time_t *timer, struct tm *result)` under `#ifndef HAVE_LOCALTIME_R`.

Control flow: MSVC builds call `localtime_s(result, timer)` and return `result` on success. Other fallback builds call `localtime()`, copy the returned `struct tm` into caller storage, and return the caller buffer.

State and persistence behavior: writes into caller-provided `struct tm`. Non-MSVC path reads from libc static `localtime()` storage before copying.

Dependencies and integration points: portability shim for code requiring reentrant local time conversion.

Risks: non-MSVC fallback is not truly thread-safe because `localtime()` uses shared static storage. It only narrows the window by copying immediately. No null pointer checks.

Test signals: successful conversion, NULL/error propagation if libc returns NULL, and threaded stress on platforms using the fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/localtime_r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/mkdir.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/mkdir.c

Purpose: portable wrapper for directory creation with Unix-style signature.

Important APIs/types/functions: `rk_mkdir(const char *pathname, mode_t mode)`.

Control flow: on non-Windows, calls `mkdir(pathname, mode)`. On Windows, ignores `mode` and calls `_mkdir(pathname)`.

State and persistence behavior: creates a filesystem directory or returns an error from the platform call.

Dependencies and integration points: roken portability wrapper, with `mkdir` macro undefined before defining the wrapper to avoid replacement loops.

Risks: Windows cannot honor Unix permission mode, so callers needing specific ACLs must handle that elsewhere. Behavior and errno values otherwise follow the platform call.

Test signals: directory creation success, existing directory errors, permission-denied paths, and Windows mode-ignored behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/mkdir.c -->
