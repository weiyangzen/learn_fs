# subset-b-000935 Research

Grouped research report for the requested Ceph-client crypto subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/selftest.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/selftest.c

Purpose: implements in-kernel selftests for the Kerberos 5 crypto library. It validates PRF output, key derivation, encryption/decryption, and MIC generation/verification against static vectors supplied by `selftest_data.c`.

Important APIs, types, and functions: `krb5_selftest()` is the exported entry point. `prep_buf()`, `load_buf()`, and `clear_buf()` manage decoded test buffers. `krb5_test_one_prf()`, `krb5_test_one_key()`, `krb5_test_one_enc()`, and `krb5_test_one_mic()` drive each vector class. The code uses `struct krb5_buffer`, `struct krb5_enctype`, `struct crypto_aead`, `struct crypto_shash`, and single-entry `scatterlist` objects.

Control flow: `krb5_selftest()` allocates a 4096-byte scratch buffer, iterates null-terminated vector arrays, and skips unsupported enctypes via `-EOPNOTSUPP`. PRF tests decode key/octet/expected PRF and call `calc_PRF`. Key tests derive Kc, Ke, and Ki from a base key. Encryption tests build a confounder-plus-plaintext buffer, prepare either raw base-key or already-derived keys, encrypt, compare ciphertext, then decrypt and verify returned offsets and plaintext. MIC tests prepare checksum keys, generate a MIC at the front of the buffer, then verify it and check payload offsets.

State and persistence: all buffers and crypto transforms are per-test transient allocations. Test state persists only in stack/local heap objects and kernel logs; no filesystem state is written. `VALID()` marks malformed vectors, while `CHECK()` marks implementation mismatches.

Dependencies and integration points: depends on `crypto_krb5_find_enctype()`, Kerberos profile callbacks, `crypto_krb5_prepare_encryption()`, `crypto_krb5_encrypt()`, `crypto_krb5_decrypt()`, `crypto_krb5_get_mic()`, `crypto_krb5_verify_mic()`, `hex2bin()`, and the vector declarations in `internal.h`.

Risks: the 4096-byte scratch buffer assumes all current vectors fit; larger vectors would need sizing changes. The quote-prefixed literal path in `load_buf()` stores `len - 1` bytes including the trailing string content exactly as typed. Tests check deterministic confounder vectors rather than randomness. Error logging exposes vector bytes, which is acceptable for test data but not secret production data.

Test signals: module load/selftest logs should show all supported enctypes running and final success. Good regression cases include zero-length plaintext, sub-block/block/exceed-block CTS paths, both K0 and derived-key inputs, unsupported enctype skipping, checksum verify offset handling, and failure injection for malformed hex or mismatched expected data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/selftest_data.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/selftest_data.c

Purpose: provides the static Kerberos 5 test-vector tables consumed by `selftest.c`. The vectors cover RFC 8009 AES-SHA2, RFC 6803 Camellia, key derivation, encryption layouts, and MIC calculation.

Important APIs, types, and data: exports four null-terminated arrays: `krb5_prf_tests[]`, `krb5_key_tests[]`, `krb5_enc_tests[]`, and `krb5_mic_tests[]`. Entries use `struct krb5_prf_test`, `struct krb5_key_test`, `struct krb5_enc_test`, and `struct krb5_mic_test` fields from `internal.h`, including `.etype`, `.name`, `.key`, `.Kc`, `.Ke`, `.Ki`, `.K0`, `.usage`, `.plain`, `.conf`, `.ct`, and `.mic`.

Control flow: this file has no executable control flow. Runtime behavior is produced when `krb5_selftest()` walks each array until it sees an entry with no `.name`. Hex strings are decoded by `load_buf()`; strings whose first byte is a single quote are treated as literal byte data after the quote.

State and persistence: all vectors are read-only static kernel data. There is no mutable state or persistence. The sentinel `{/* END */}` entries are part of the API contract with the test runner.

Dependencies and integration points: depends on Kerberos enctype constants such as `KRB5_ENCTYPE_AES128_CTS_HMAC_SHA256_128`, `KRB5_ENCTYPE_AES256_CTS_HMAC_SHA384_192`, `KRB5_ENCTYPE_CAMELLIA128_CTS_CMAC`, and `KRB5_ENCTYPE_CAMELLIA256_CTS_CMAC`. The content is tied to expected behavior in `krb5_kdf.c`, RFC 3961 simplified profiles, AES2, and Camellia Kerberos implementations.

Risks: a typo in any vector can look like a crypto regression. Literal string entries are easy to misread because the leading quote is a marker, not data. The vectors exercise selected RFC examples, not exhaustive key usages, message sizes, or all Kerberos enctypes.

Test signals: selftest coverage should detect format drift in vector structs, missing sentinels, incorrect enctype registration, and changed output lengths. Adding new enctypes should include PRF, derivation, encryption, and MIC vectors here so `selftest.c` can validate the whole profile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/selftest_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5enc.c -->
# sources/distributed-fs/ceph-client/crypto/krb5enc.c

Purpose: defines the `krb5enc` AEAD template for Kerberos 5 RFC 3961 simplified profiles. It composes an ahash authentication algorithm and an skcipher encryption algorithm into a crypto API AEAD instance whose checksum is appended after the encrypted payload.

Important APIs, types, and functions: `crypto_krb5enc_extractkeys()` decodes the auth/encryption key blob and is exported. `krb5enc_setkey()`, `krb5enc_encrypt()`, `krb5enc_decrypt()`, `krb5enc_init_tfm()`, `krb5enc_exit_tfm()`, and `krb5enc_create()` implement the template. Key state lives in `struct krb5enc_ctx`; per-instance spawns and request offsets live in `struct krb5enc_instance_ctx`; request-local SG arrays and tail storage live in `struct krb5enc_request_ctx`.

Control flow: instance creation validates AEAD attributes, grabs ahash and skcipher children, names the instance as `krb5enc(auth,enc)`, and sizes request storage for either child request plus two digests. Setkey decodes an `rtattr` key blob with `CRYPTO_AUTHENC_KEYA_PARAM`, then sets the auth key and encryption key. Encryption hashes associated data plus plaintext, writes the digest after the encrypted region, and dispatches the skcipher over data after `assoclen`. Decryption decrypts the ciphertext portion first, hashes associated data plus decrypted plaintext, then compares the stored checksum with `crypto_memneq()`.

State and persistence: transform state contains child `crypto_ahash` and `crypto_skcipher` handles. Per-request state contains forwarded scatterlists, child requests, and digest scratch space. No state persists beyond crypto object lifetime.

Dependencies and integration points: integrates with the crypto template registry as `MODULE_ALIAS_CRYPTO("krb5enc")`. It uses `scatterwalk_ffwd()`, `scatterwalk_map_and_copy()`, `crypto_grab_ahash()`, `crypto_grab_skcipher()`, `aead_register_instance()`, and rtnetlink attribute encoding compatible with `authenc`.

Risks: key blob parsing is sensitive to `rtattr` alignment and CPU-endian versus big-endian fields. `reqoff = 2 * digestsize` must keep `ahreq->result` and copied message hash separate. Length arithmetic around `assoclen`, `cryptlen`, and `authsize` is security-sensitive. Asynchronous completions must complete only after chained hash/cipher work has reached a terminal state.

Test signals: testmgr and Kerberos selftests should cover setkey blob parsing, separate and in-place source/destination buffers, async child algorithms, wrong checksums returning `-EBADMSG`, truncated buffers, zero-length plaintext, and exact instance naming for algorithm lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lrw.c -->
# sources/distributed-fs/ceph-client/crypto/lrw.c

Purpose: implements the LRW block-cipher mode template for 128-bit block ciphers, mainly for disk-style tweakable encryption. It wraps an ECB child cipher and applies GF(2^128) tweak masks before and after the child operation.

Important APIs, types, and functions: `struct lrw_tfm_ctx` stores the child skcipher, a `gf128mul_64k` table for key2, and `mulinc[128]` tweak increments. `struct lrw_request_ctx` stores the starting tweak and child request. Key and data paths are `lrw_setkey()`, `lrw_xor_tweak()`, `lrw_init_crypt()`, `lrw_encrypt()`, and `lrw_decrypt()`. Template setup is in `lrw_create()`.

Control flow: `lrw_create()` grabs the requested child or automatically wraps a bare block cipher as `ecb(cipher)`, then requires a 16-byte block size and zero child IV. `lrw_setkey()` splits the supplied key into child key plus final 16-byte tweak key, builds the GF multiplication table, and precomputes increment masks. Encryption and decryption compute initial `T = IV * key2`, xor each block with the tweak, run the child over the destination buffer, then recompute and xor the same tweak stream after the child operation.

State and persistence: transform state persists the child handle and GF tables until `lrw_exit_tfm()`. Request state holds only the current initial tweak and child request. The IV is advanced on the second pass at completion so callers see the consumed counter.

Dependencies and integration points: depends on `crypto/internal/skcipher.h`, `crypto/b128ops.h`, `crypto/gf128mul.h`, `skcipher_walk_virt()`, and the crypto template registry. It soft-depends on `ecb`.

Risks: bit numbering in `lrw_setbit128_bbe()` is endian-sensitive. The key length contract requires at least child minimum plus 16 bytes. The two-pass tweak recomputation must remain identical, or encryption/decryption corrupts data. LRW is a legacy disk mode; new code usually prefers XTS where applicable.

Test signals: known LRW vectors from tcrypt, non-in-place and in-place SG tests, IV advancement checks, child lookup with both `cipher` and `ecb(cipher)` names, key-size boundary tests, and big-endian build coverage are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lrw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lskcipher.c -->
# sources/distributed-fs/ceph-client/crypto/lskcipher.c

Purpose: implements the crypto API type for linear symmetric key ciphers (`lskcipher`) and bridges that type to skcipher scatterlist requests. It centralizes allocation, registration, reporting, alignment fallback, and simple-instance helpers.

Important APIs, types, and functions: exported APIs include `crypto_lskcipher_setkey()`, `crypto_lskcipher_encrypt()`, `crypto_lskcipher_decrypt()`, `crypto_grab_lskcipher()`, `crypto_alloc_lskcipher()`, `crypto_register_lskcipher()`, `crypto_unregister_lskcipher()`, `crypto_register_lskciphers()`, `crypto_unregister_lskciphers()`, `lskcipher_register_instance()`, and `lskcipher_alloc_instance_simple()`. Internal paths include `crypto_lskcipher_crypt_unaligned()` and `crypto_lskcipher_crypt_sg()`.

Control flow: direct callers allocate an `lskcipher`, set a key after min/max validation, and call encrypt/decrypt on linear buffers. If key, src, dst, or IV alignment violates the algorithm alignmask, the code copies through temporary aligned pages and copies IV plus state back. The SG bridge walks a skcipher request, maps continuation/final flags into `CRYPTO_LSKCIPHER_FLAG_*`, and updates the IV after walking. Registration prepares common skcipher metadata, enforces power-of-two chunksize, installs the `crypto_lskcipher_type`, and registers algorithms or instances.

State and persistence: transform state is owned by individual algorithms and optional child ciphers. The bridge stores a child `crypto_lskcipher *` in the parent skcipher context and frees it on tfm exit. No state persists outside crypto object lifetimes, except exported/imported IV/state carried by callers.

Dependencies and integration points: depends on `skcipher.h`, common crypto algorithm registration, procfs/netlink reporting, and simple-mode templates such as CBC/ECB-style modes.

Risks: alignment fallback allocates with `GFP_ATOMIC` and processes page-sized chunks; failures return `-ENOMEM`. Lengths not divisible by blocksize fail after partial chunk handling. Continuation/final flag propagation is subtle for multi-walk requests. Simple instance naming prevents nested instances unless the child was auto-ECB-wrapped.

Test signals: test aligned and unaligned keys/data/IV, SG requests with continuation and not-final flags, chunksize validation, netlink/proc reporting, simple instance creation with bare and `ecb(...)` child names, and registration rollback for arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lskcipher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lz4.c -->
# sources/distributed-fs/ceph-client/crypto/lz4.c

Purpose: registers the LZ4 compression library as a synchronous compression (`scomp`) crypto algorithm named `lz4`.

Important APIs and functions: `lz4_alloc_ctx()` and `lz4_free_ctx()` manage the LZ4 work memory. `lz4_scompress()` calls `LZ4_compress_default()`, and `lz4_sdecompress()` calls `LZ4_decompress_safe()`. `lz4_mod_init()` and `lz4_mod_fini()` register and unregister the single `scomp_alg`.

Control flow: crypto users allocate an scomp stream, which receives a vmalloc-backed context sized by `LZ4_MEM_COMPRESS`. Compression returns `-EINVAL` if the library reports zero output, otherwise updates `*dlen`. Decompression returns `-EINVAL` on negative library status and updates `*dlen` with the actual output size.

State and persistence: the only state is per-stream work memory allocated with `vmalloc()` and freed with `vfree()`. The registered algorithm object persists while the module is loaded.

Dependencies and integration points: depends on `<linux/lz4.h>` and `crypto/internal/scompress.h`; consumed by crypto compression callers and the acomp wrapper in `scompress.c`.

Risks: callers must provide adequate destination space through `*dlen`. Compression context allocation can fail under memory pressure. This wrapper does not store frame headers or original length metadata, so users must manage those format details externally.

Test signals: scomp compression/decompression round trips, too-small destination buffers, malformed compressed input, zero-length input handling, and module alias lookup for `lz4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lz4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lz4hc.c -->
# sources/distributed-fs/ceph-client/crypto/lz4hc.c

Purpose: registers the high-compression LZ4HC library as an scomp crypto algorithm named `lz4hc`.

Important APIs and functions: `lz4hc_alloc_ctx()` allocates `LZ4HC_MEM_COMPRESS` workspace, `lz4hc_scompress()` calls `LZ4_compress_HC()` using `LZ4HC_DEFAULT_CLEVEL`, and `lz4hc_sdecompress()` uses `LZ4_decompress_safe()` because LZ4HC output is standard LZ4 format.

Control flow: module initialization registers one `scomp_alg`. Compression receives source, destination, length pointer, and stream context; a zero return from the library maps to `-EINVAL`. Decompression maps negative returns to `-EINVAL` and records the actual decompressed size.

State and persistence: per-stream workspace is vmalloc-backed and released at stream teardown. No compressed data or dictionaries are persisted by the wrapper.

Dependencies and integration points: depends on Linux LZ4HC library functions and the scomp framework. It integrates with users that select `lz4hc` when trading CPU time for better compression.

Risks: high-compression work memory is larger than regular LZ4 and allocation failure is possible. As with `lz4.c`, there is no container framing; consumers must know expected output limits. Decompression accepts ordinary LZ4 data, so tests should not assume an LZ4HC-only decompressor.

Test signals: round trips for compressible and incompressible data, small destination buffer failure, malformed input failure, allocation failure paths, and algorithm registration/alias lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lz4hc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lzo-rle.c -->
# sources/distributed-fs/ceph-client/crypto/lzo-rle.c

Purpose: wraps the LZO-RLE safe compressor as an scomp crypto algorithm named `lzo-rle`.

Important APIs and functions: `lzorle_alloc_ctx()`/`lzorle_free_ctx()` allocate `LZO1X_MEM_COMPRESS` workspace with `kvmalloc()`/`kvfree()`. `lzorle_scompress()` calls `lzorle1x_1_compress_safe()`. `lzorle_sdecompress()` calls `lzo1x_decompress_safe()`.

Control flow: crypto registration exposes a single `scomp_alg`. Compression converts `unsigned int *dlen` to a `size_t` temporary required by LZO, maps non-`LZO_E_OK` to `-EINVAL`, and writes the resulting size back. Decompression follows the same size conversion pattern.

State and persistence: only the compression workspace persists per stream. There is no global runtime state beyond the registered algorithm.

Dependencies and integration points: depends on `<linux/lzo.h>` and the scomp framework. It shares decompression with standard LZO because RLE is an encoding variant of the LZO1X stream.

Risks: size conversion comments highlight the `size_t` versus `unsigned int` boundary on 64-bit systems. Destination length must be supplied by callers. The wrapper returns only generic `-EINVAL` for library failures, so diagnostics depend on tests.

Test signals: round trips containing long repeated runs, ordinary small inputs, too-small output buffers, invalid compressed streams, and successful crypto lookup by `lzo-rle`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lzo-rle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lzo.c -->
# sources/distributed-fs/ceph-client/crypto/lzo.c

Purpose: wraps the standard LZO1X safe compressor/decompressor as an scomp crypto algorithm named `lzo`.

Important APIs and functions: `lzo_alloc_ctx()`/`lzo_free_ctx()` manage `LZO1X_MEM_COMPRESS` workspace. `lzo_scompress()` calls `lzo1x_1_compress_safe()`, while `lzo_sdecompress()` calls `lzo1x_decompress_safe()`.

Control flow: module init registers a single `scomp_alg`. Compression and decompression each translate the crypto API `unsigned int` destination length into a library `size_t`, run the safe LZO primitive, return `-EINVAL` on non-OK status, and update `*dlen` with actual output length.

State and persistence: per-stream work memory is allocated with `kvmalloc()` and released with `kvfree()`. No dictionary or persistent stream state is stored in the wrapper.

Dependencies and integration points: depends on the kernel LZO library and the synchronous compression framework. The acomp compatibility path in `scompress.c` can use this implementation for asynchronous-style compression requests.

Risks: output buffer sizing is caller-owned. The wrapper compresses raw LZO blocks without framing metadata. All library errors collapse to `-EINVAL`, reducing failure detail.

Test signals: standard crypto compression vectors, round trips across empty/small/large buffers, boundary output sizes, malformed stream rejection, and module alias lookup for `lzo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/lzo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/md4.c -->
# sources/distributed-fs/ceph-client/crypto/md4.c

Purpose: implements the MD4 message digest as a synchronous hash (`shash`) algorithm named `md4`/`md4-generic`.

Important APIs, types, and functions: `struct md4_ctx` holds four hash words, a 16-word block buffer, and a byte counter. `md4_init()`, `md4_update()`, `md4_final()`, `md4_transform_helper()`, and `md4_transform()` implement the shash lifecycle. The algorithm is registered through `crypto_register_shash()`.

Control flow: init sets RFC 1320 IV constants. Update accumulates input into a 64-byte block, processes full blocks after little-endian conversion, and stores the trailing partial block. Final appends `0x80`, zero padding, and a 64-bit bit length, processes the final block(s), writes little-endian digest bytes, and clears the context.

State and persistence: digest state lives only in the shash descriptor context. Module registration persists the algorithm while loaded. Finalization zeroes the context to avoid retaining intermediate material.

Dependencies and integration points: uses `crypto/internal/hash.h`, endian helpers, and module registration. Consumers include legacy protocols that still need MD4, such as NTLM-related code.

Risks: MD4 is cryptographically broken and should not be used for new integrity designs. Padding and byte counter logic are sensitive around 56-byte and 64-byte boundaries. This implementation has no export/import state support, unlike newer hash wrappers in this subset.

Test signals: RFC 1320 vectors, partial update versus single-shot equivalence, boundary message lengths around block and padding sizes, and crypto API registration under `md4`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/md4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/md5.c -->
# sources/distributed-fs/ceph-client/crypto/md5.c

Purpose: registers library-backed MD5 and HMAC-MD5 shash algorithms with crypto API state export/import compatibility.

Important APIs, types, and functions: exports `md5_zero_message_hash`. `crypto_md5_*` wrappers call `md5_init()`, `md5_update()`, `md5_final()`, and `md5()`. `crypto_hmac_md5_*` wrappers call `hmac_md5_preparekey()`, `hmac_md5_init()`, `hmac_md5_update()`, `hmac_md5_final()`, and `hmac_md5()`. Internal helpers `__crypto_md5_export()`, `__crypto_md5_import()`, and core variants implement shash state format.

Control flow: module init registers two algorithms: `md5` and `hmac(md5)`. Normal hash requests delegate to the library. Export copies the library context after subtracting the partial-block byte count and stores that partial count as one appended byte. Import restores the context and re-adds the partial count. HMAC import also restores the outer state from the tfm key.

State and persistence: per-request state lives in `struct md5_ctx` or `struct hmac_md5_ctx`; HMAC key state lives in the tfm context. Exported state is caller-owned and transient. The zero-message digest is static exported data.

Dependencies and integration points: depends on `<crypto/md5.h>` and `crypto/internal/hash.h`. Used by legacy protocols and by templates that request `hmac(md5)`.

Risks: MD5 is collision-broken and should be limited to compatibility use. Export/import relies on layout static assertions matching legacy `struct md5_state`. HMAC import must restore `ostate` from the current key or resumed HMACs are wrong.

Test signals: standard MD5 and HMAC-MD5 vectors, zero-message digest users, export/import mid-block and block-aligned states, keyed import after setkey, and algorithm aliases `md5-lib` and `hmac-md5-lib`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/md5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/mldsa.c -->
# sources/distributed-fs/ceph-client/crypto/mldsa.c

Purpose: exposes ML-DSA signature verification through the crypto `sig` API for ML-DSA-44, ML-DSA-65, and ML-DSA-87 strengths.

Important APIs, types, and functions: `struct crypto_mldsa_ctx` stores a public key buffer, key length, selected `enum mldsa_alg`, and `key_set` flag. `crypto_mldsa_verify()` calls `mldsa_verify()`. `crypto_mldsa_set_pub_key()`, `crypto_mldsa_key_size()`, and `crypto_mldsa_max_size()` enforce strength-specific sizes. Signing and private-key setup return `-EOPNOTSUPP`.

Control flow: module init registers three `sig_alg` entries. Each init callback sets `ctx->strength` and clears `key_set`. Public key setup checks exact key length and copies the key into the fixed maximum buffer. Verify rejects unset keys with `-EINVAL`, then delegates to the ML-DSA library. Module exit unregisters all registered algorithms.

State and persistence: key material is stored in the crypto tfm context until tfm teardown. No private keys are accepted. There is no persistent storage.

Dependencies and integration points: depends on `crypto/internal/sig.h` and `<crypto/mldsa.h>`. Integrates with callers that use the generic signature API and expect high-priority library-backed ML-DSA verification.

Risks: the implementation is verification-only; callers needing signing must handle `-EOPNOTSUPP`. Public keys are copied but not explicitly wiped on exit, though they are public. Size dispatch must stay synchronized with ML-DSA library constants.

Test signals: NIST ML-DSA verification vectors for all three strengths, exact key/signature size boundaries, unset-key failure, unsupported sign/private-key paths, and registration rollback when a later algorithm fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/mldsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/pcbc.c -->
# sources/distributed-fs/ceph-client/crypto/pcbc.c

Purpose: implements the Propagating Cipher Block Chaining (`pcbc`) skcipher template over simple block ciphers.

Important APIs and functions: `crypto_pcbc_encrypt()`, `crypto_pcbc_decrypt()`, and their segment/in-place helpers perform the mode. `crypto_pcbc_create()` allocates a simple skcipher instance and installs the PCBC encrypt/decrypt callbacks.

Control flow: instance creation delegates most child setup to `skcipher_alloc_instance_simple()`. Encryption walks the request virtually. For each block, encryption xors plaintext into IV, encrypts to ciphertext, then sets the next IV to plaintext xor ciphertext. The in-place path saves plaintext in a stack buffer before overwriting. Decryption decrypts the ciphertext block, xors IV to produce plaintext, then sets the next IV to plaintext xor ciphertext.

State and persistence: mode state is request-local in the walk IV. The child cipher is stored by the simple skcipher instance infrastructure. No state persists outside tfm/request lifetimes.

Dependencies and integration points: depends on internal cipher and skcipher helpers, `crypto_xor()`, `crypto_xor_cpy()`, and the crypto template registry. It imports `CRYPTO_INTERNAL` because it uses simple cipher internals.

Risks: PCBC is an old mode with limited modern use and should not be selected for new protocols without a compatibility requirement. The stack temporary uses `MAX_CIPHER_BLOCKSIZE`, so child block sizes must fit crypto API expectations. In-place handling is separate and must preserve the original ciphertext/plaintext for IV propagation.

Test signals: encrypt/decrypt round trips for in-place and separate buffers, multi-SG walks, non-block-multiple rejection by skcipher walk, IV update behavior, and template lookup `pcbc(cipher)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/pcbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/pcrypt.c -->
# sources/distributed-fs/ceph-client/crypto/pcrypt.c

Purpose: implements the `pcrypt` template, a parallelization wrapper for AEAD algorithms using padata worker infrastructure.

Important APIs, types, and functions: global `pencrypt`, `pdecrypt`, and `pcrypt_kset` hold padata instances and sysfs state. `struct pcrypt_instance_ctx` stores the child spawn, padata shells, and tfm counter. `struct pcrypt_aead_ctx` stores the child AEAD and callback CPU. Request paths are `pcrypt_aead_encrypt()`, `pcrypt_aead_decrypt()`, `pcrypt_aead_enc()`, `pcrypt_aead_dec()`, `pcrypt_aead_done()`, and `pcrypt_aead_serial()`.

Control flow: module init creates `/sys/kernel/pcrypt`, allocates padata instances for encryption and decryption, then registers the template. Instance creation supports AEAD only, allocates padata shells, grabs the child, copies algorithm properties, marks the instance async, and raises priority by 100. Tfm init selects a callback CPU round-robin over online CPUs and spawns the child. Encrypt/decrypt builds a child request and submits padata parallel work; if padata is busy, it falls back to direct child execution.

State and persistence: padata instances and sysfs kobjects persist while the module is loaded. Each tfm keeps its child and chosen callback CPU. Each request keeps a `pcrypt_request`, child `aead_request`, and padata metadata until completion.

Dependencies and integration points: depends on padata, kobject/sysfs, CPU masks, and AEAD crypto templates. It integrates with algorithm names such as `pcrypt(gcm(aes))`.

Risks: CPU hotplug changes may affect callback CPU selection after tfm init. Async completion ordering must route through the serial callback exactly once. Fallback direct execution changes scheduling behavior. Resource cleanup must unwind padata shells and ksets on partial init failures.

Test signals: async AEAD testmgr coverage, padata busy fallback, CPU hotplug while tfms exist, sysfs object creation/removal, child setkey/authsize forwarding, and module init rollback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/pcrypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/proc.c -->
# sources/distributed-fs/ceph-client/crypto/proc.c

Purpose: implements `/proc/crypto`, a procfs sequence view of registered crypto algorithms.

Important APIs and functions: `crypto_init_proc()` creates the `crypto` proc entry, and `crypto_exit_proc()` removes it. Sequence callbacks `c_start()`, `c_next()`, `c_stop()`, and `c_show()` iterate `crypto_alg_list` under `crypto_alg_sem`.

Control flow: opening `/proc/crypto` starts a seq iteration while holding the crypto algorithm read semaphore. For each `struct crypto_alg`, `c_show()` prints name, driver, module, priority, refcount, selftest state, internal flag, optional FIPS status, and type-specific details. Larval algorithms are reported separately. Algorithms with a `cra_type->show` hook delegate formatting to that type; legacy cipher algorithms are formatted inline.

State and persistence: the file owns no algorithm state. It reads the live in-memory registry and emits a transient procfs view.

Dependencies and integration points: depends on `crypto_alg_list`, `crypto_alg_sem`, `module_name()`, FIPS state, procfs, and type-specific `.show` callbacks such as hash, rng, skcipher, lskcipher, or scomp reporting.

Risks: output is diagnostic ABI-like text; changes can affect userspace tools that parse `/proc/crypto`. The read lock must cover list traversal. Type-specific show hooks must not sleep in ways incompatible with the read-side locking expectations.

Test signals: procfs read under concurrent algorithm registration/unregistration, FIPS-enabled output, larval entries, type-specific formatting, and absence of use-after-free under module unload stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ripemd.h -->
# sources/distributed-fs/ceph-client/crypto/ripemd.h

Purpose: defines shared RIPEMD constants used by RIPEMD-family implementations, currently consumed by `rmd160.c`.

Important APIs and data: provides `RMD160_DIGEST_SIZE`, `RMD160_BLOCK_SIZE`, initial state words `RMD_H0` through `RMD_H4`, and round constants `RMD_K1` through `RMD_K9`.

Control flow: none. This is a guarded header of macro constants.

State and persistence: none; values are compile-time constants.

Dependencies and integration points: included by `rmd160.c` to name the algorithm sizes and compression-function constants. Any future RIPEMD variants can share the same header for common IVs and constants where appropriate.

Risks: changing constants silently breaks digest compatibility. Macro names are global within includers, so additional RIPEMD headers should avoid collisions.

Test signals: RIPEMD-160 known-answer vectors indirectly validate these constants. Compile coverage ensures the include guard and macro definitions remain available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/ripemd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rmd160.c -->
# sources/distributed-fs/ceph-client/crypto/rmd160.c

Purpose: implements RIPEMD-160 as a block-only shash algorithm named `rmd160`.

Important APIs, types, and functions: `struct rmd160_ctx` stores byte count and five state words. `rmd160_transform()` implements the dual-lane 80-round compression function. `rmd160_init()`, `rmd160_update()`, and `rmd160_finup()` implement the shash interface.

Control flow: init loads RIPEMD IV constants. Update processes only full 64-byte blocks, increments `byte_count` by processed bytes, clears the temporary block, and returns the remaining byte count because the algorithm is registered with `CRYPTO_AHASH_ALG_BLOCK_ONLY`. `finup()` handles the final partial input, appends RIPEMD padding and length, processes one or two final blocks, and writes little-endian state words to the digest.

State and persistence: hash state is per descriptor. Temporary stack blocks are explicitly cleared. Module registration persists only while loaded.

Dependencies and integration points: depends on `ripemd.h`, `crypto/internal/hash.h`, endian helpers, and module crypto registration. It is referenced by signature padding code through hash prefix name `rmd160`.

Risks: the update API is unusual because it returns a remainder for block-only handling; callers must be the crypto hash framework, not ad hoc direct users. The final padding threshold and little-endian block interpretation are correctness-critical. RIPEMD-160 is legacy and weaker than modern SHA-2/SHA-3 choices.

Test signals: RIPEMD-160 known-answer vectors, chunked updates through ahash/shash wrappers, finalization at 55/56/63/64-byte boundaries, and signature verification using `pkcs1(rsa,rmd160)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rmd160.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rng.c -->
# sources/distributed-fs/ceph-client/crypto/rng.c

Purpose: implements the crypto API RNG type, default RNG management, seeding helper, reporting, allocation, and registration functions.

Important APIs and functions: exported functions include `crypto_rng_reset()`, `crypto_alloc_rng()`, `__crypto_stdrng_get_bytes()`, `crypto_del_default_rng()`, `crypto_register_rng()`, `crypto_unregister_rng()`, `crypto_register_rngs()`, and `crypto_unregister_rngs()`. Global state is `crypto_default_rng`, `crypto_default_rng_refcnt`, and `crypto_default_rng_lock`.

Control flow: `crypto_rng_reset()` seeds a tfm directly, or if `seed == NULL` with nonzero length, allocates a temporary seed and fills it with `get_random_bytes_wait()`. Default RNG access lazily allocates `stdrng`, seeds it with its required seed size, increments a protected refcount, gets bytes, then decrements the refcount. Registration installs the RNG crypto type, enforces seed size no larger than `PAGE_SIZE / 8`, and fills a no-op `set_ent` callback when absent.

State and persistence: the default RNG tfm is a global in-memory singleton protected by a mutex and refcount. Temporary seeds are wiped with `kfree_sensitive()`. Algorithm registrations persist while providers are loaded.

Dependencies and integration points: depends on the generic crypto type registry, `get_random_bytes_wait()`, procfs/netlink reporting hooks, and providers such as `stdrng`.

Risks: `crypto_put_default_rng()` decrements without underflow checking beyond mutex serialization; callers must pair get/put internally. Default RNG deletion returns `-EBUSY` while refs are active. Blocking entropy acquisition can affect init timing. Seed-size validation is part of memory safety.

Test signals: default RNG lazy allocation, deletion while busy and idle, seed reset with caller seed and generated seed, proc/netlink reporting, seed-size rejection, and registration rollback for arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rsa-pkcs1pad.c -->
# sources/distributed-fs/ceph-client/crypto/rsa-pkcs1pad.c

Purpose: implements the `pkcs1pad(rsa)` akcipher template for RSAES-PKCS1-v1_5 style public-key encryption padding and unpadding.

Important APIs, types, and functions: `struct pkcs1pad_ctx` stores the child RSA tfm and key size. `struct pkcs1pad_request` stores temporary SGs, buffers, and child request. Key setup functions call `rsa_set_key()`. Main paths are `pkcs1pad_encrypt()`, `pkcs1pad_encrypt_complete()`, `pkcs1pad_decrypt()`, and `pkcs1pad_decrypt_complete()`.

Control flow: instance creation accepts only a child whose base name is `rsa`, then registers `pkcs1pad(rsa-driver)`. Encryption checks key size, maximum source length `key_size - 11`, and destination size. It builds an encoded block beginning with `0x02`, random nonzero padding bytes, a zero separator, and plaintext, then invokes child RSA encrypt. Completion left-pads the child result to the full modulus size if needed. Decryption requires ciphertext length equal to key size, runs child RSA decrypt into a temporary buffer, checks the `0x00 0x02 PS 0x00` structure and minimum padding length, then copies plaintext to the caller buffer or reports needed size.

State and persistence: child tfm and key size persist per transform. Per-request buffers are allocated and freed, with decrypted buffers wiped via `kfree_sensitive()`.

Dependencies and integration points: depends on akcipher internals, RSA helpers, scatterlists, and random nonzero padding. Registered by `rsa.c` through `rsa_pkcs1pad_tmpl`.

Risks: PKCS#1 v1.5 encryption padding has known oracle risks if error behavior is exposed to attackers. The unpadding path branches on malformed structure and is not a full side-channel hardened protocol defense. Random padding must be nonzero. Asynchronous cleanup must free temp buffers exactly once.

Test signals: RSA encryption/decryption vectors, too-long plaintext, short destination `-EOVERFLOW`, malformed padding rejection, async child completion, leading-zero modulus output normalization, and template name validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rsa-pkcs1pad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rsa.c -->
# sources/distributed-fs/ceph-client/crypto/rsa.c

Purpose: implements the generic MPI-backed raw RSA akcipher algorithm and registers the RSA padding/signature templates.

Important APIs, types, and functions: `struct rsa_mpi_key` stores MPI values for `n`, `e`, `d`, CRT primes/exponents, and `qinv`. `rsa_enc()` and `rsa_dec()` implement akcipher request operations. `_rsa_enc()` performs RSAEP; `_rsa_dec_crt()` performs CRT RSADP. Key setup functions parse BER keys through `rsa_parse_pub_key()` and `rsa_parse_priv_key()`. `rsa_init()` registers `rsa`, `pkcs1pad`, and `pkcs1` templates.

Control flow: public-key setup frees any old key, parses ASN.1, reads `e` and `n` into MPIs, validates modulus length, and applies FIPS exponent checks when enabled. Private-key setup similarly loads CRT parameters. Encryption reads the source MPI from SG, checks `1 < m < n - 1`, computes `m^e mod n`, and writes the result. Decryption validates ciphertext and computes CRT recombination: `m1`, `m2`, `h`, and `m`.

State and persistence: RSA key MPIs persist in the akcipher tfm context until replaced or freed by `rsa_exit_tfm()`. No key is persisted outside memory.

Dependencies and integration points: depends on the MPI library, FIPS state, akcipher internals, RSA ASN.1 helper functions, and external templates declared in internal RSA headers.

Risks: raw RSA is only a primitive; callers generally need padding or signature templates. CRT private operations are sensitive and should be reviewed for side-channel properties inherited from MPI. FIPS rules reject small keys and enforce exponent constraints. `rsa_max_size()` assumes `n` is set; callers should set keys first.

Test signals: public/private key parsing, key length policy with FIPS on/off, exponent policy, raw RSA test vectors, CRT recombination correctness, invalid payload bounds, template registration rollback, and integration with `pkcs1pad` and `pkcs1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rsa_helper.c -->
# sources/distributed-fs/ceph-client/crypto/rsa_helper.c

Purpose: provides ASN.1 decoder callbacks and exported helper functions that extract raw RSA key components from BER-encoded public and private keys.

Important APIs and functions: callbacks `rsa_get_n()`, `rsa_get_e()`, `rsa_get_d()`, `rsa_get_p()`, `rsa_get_q()`, `rsa_get_dp()`, `rsa_get_dq()`, and `rsa_get_qinv()` populate `struct rsa_key` pointers and lengths. `rsa_parse_pub_key()` and `rsa_parse_priv_key()` invoke generated decoders `rsapubkey_decoder` and `rsaprivkey_decoder`.

Control flow: decoder callbacks validate non-null/nonempty fields and size relationships against the modulus size. `rsa_get_n()` additionally strips leading zeros for FIPS size checking and rejects effective modulus sizes below 2048 bits when FIPS is enabled. The parse functions do not copy key bytes; they store pointers into the original input buffer for later MPI parsing by callers.

State and persistence: no persistent state is owned here. Returned `struct rsa_key` fields borrow the caller's input buffer lifetime.

Dependencies and integration points: depends on generated ASN.1 headers `rsapubkey.asn1.h` and `rsaprivkey.asn1.h`, `asn1_ber_decoder()`, FIPS state, and `crypto/internal/rsa.h`. Used by `rsa.c` and any other RSA key consumers.

Risks: callers must keep the BER buffer alive until they copy or parse the referenced fields. Size validation mostly enforces structural bounds, not full mathematical key consistency. FIPS size checks account for leading zeros only for modulus field.

Test signals: valid public and private DER/BER keys, missing or zero-length components, components longer than modulus, leading-zero modulus in FIPS mode, too-small FIPS keys, and malformed ASN.1 decoder failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rsa_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rsassa-pkcs1.c -->
# sources/distributed-fs/ceph-client/crypto/rsassa-pkcs1.c

Purpose: implements the `pkcs1(rsa,hash)` signature template for RSASSA-PKCS1-v1_5 signing and verification through the crypto `sig` API.

Important APIs, types, and functions: static `hash_prefix_*` arrays encode ASN.1 DigestInfo prefixes for MD5, SHA-1, RIPEMD-160, SHA-2, and SHA-3 variants. `rsassa_pkcs1_find_hash_prefix()` resolves the template hash name. `rsassa_pkcs1_sign()` and `rsassa_pkcs1_verify()` implement EMSA-PKCS1-v1_5 encoding and checking. Key setup delegates to `rsa_set_key()`.

Control flow: instance creation accepts only child `rsa` and a known hash prefix, then registers names like `pkcs1(rsa,sha256)`. Signing validates key size, output length, digest length, and encoded length, builds `0x01 FF...00 || prefix || digest` in the destination buffer, and uses RSA private operation via child decrypt. Verification checks signature length and digest length, runs RSA public operation, validates leading zero, block type, minimum FF padding, zero separator, hash prefix, and digest equality.

State and persistence: per-instance state stores the selected hash prefix and child spawn. Per-tfm state stores child RSA tfm and key size. Verification allocates a temporary child request and buffer, freed with `kfree_sensitive`.

Dependencies and integration points: registered by `rsa.c` as `rsassa_pkcs1_tmpl`; depends on akcipher, sig, hash names, scatterlists, and RSA helpers.

Risks: PKCS#1 v1.5 signatures are deterministic and legacy but still widely used. The `none` prefix supports legacy protocols and disables digest length validation, which must be used only by protocols that already define the hashed input. Prefix tables must match RFC OIDs exactly.

Test signals: sign/verify for every supported hash prefix, digest-length rejection, malformed padding rejection, leading-zero normalization, unsupported hash template rejection, public/private key setup, and interoperability with known RSA PKCS#1 v1.5 vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/rsassa-pkcs1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/scatterwalk.c -->
# sources/distributed-fs/ceph-client/crypto/scatterwalk.c

Purpose: provides scatterlist walking and copying helpers used by crypto algorithms and templates.

Important APIs and functions: exported functions include `scatterwalk_skip()`, `memcpy_from_scatterwalk()`, `memcpy_to_scatterwalk()`, `memcpy_from_sglist()`, `memcpy_to_sglist()`, `memcpy_sglist()`, and `scatterwalk_ffwd()`.

Control flow: skip advances a scatter walk by consuming entries until the target offset is reached. Copy helpers repeatedly map walk segments with `scatterwalk_next()`, copy bytes, and mark source or destination completion. `memcpy_sglist()` copies between two scatterlists, handling no-op exact-overlap cases, highmem page mapping, same-page different-offset copies, dcache flushes, and multi-entry advancement. `scatterwalk_ffwd()` returns a scatterlist view advanced by `len`, either the original entry when exact or a two-entry chained temporary starting inside the current page.

State and persistence: no persistent state is kept. Walk state is caller-owned and updated in place. Temporary chained scatterlists are caller-provided.

Dependencies and integration points: depends on scatterlist APIs, highmem mapping, page cache helpers, and crypto scatterwalk inline helpers. Used by AEAD templates such as `krb5enc` and `seqiv`, plus compression and SG bridge code.

Risks: partial overlap beyond exact same-memory no-op is unsupported in `memcpy_sglist()`. Highmem handling must not cross page boundaries without mapping each page. `scatterwalk_ffwd()` assumes the source list contains enough length. Cache flush correctness matters on non-coherent architectures.

Test signals: copies across SG entry boundaries, highmem pages, same-page overlap/no-op, zero-length NULL cases, advanced views in templates, and dcache-sensitive architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/scatterwalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/scompress.c -->
# sources/distributed-fs/ceph-client/crypto/scompress.c

Purpose: implements the synchronous compression crypto type (`scomp`) and an async-compatible acomp bridge over scomp algorithms.

Important APIs, types, and functions: exported APIs include `crypto_init_scomp_ops_async()`, `crypto_register_scomp()`, `crypto_unregister_scomp()`, `crypto_register_scomps()`, and `crypto_unregister_scomps()`. `struct scomp_scratch` and per-CPU `scomp_scratch` provide fallback source buffers. Main acomp bridge path is `scomp_acomp_comp_decomp()`.

Control flow: scomp tfm init allocates algorithm streams and lazily allocates per-CPU scratch storage. The acomp bridge validates source/destination, maps virtual buffers directly when possible, maps single SG buffers when contiguous and safe, or copies SG input into a per-CPU scratch page. It locks an algorithm stream, calls `crypto_scomp_compress()` or `crypto_scomp_decompress()`, updates `req->dlen`, unmaps pages, and flushes destination dcache. Missing per-CPU scratch pages are requested via a work item.

State and persistence: algorithm stream pools persist per registered algorithm while tfms use them. Per-CPU scratch pages persist while at least one async wrapper user exists and are freed when the last user exits.

Dependencies and integration points: depends on acomp/scomp internals, scatterwalk copying, highmem, per-CPU data, workqueues, and crypto user reporting.

Risks: the async bridge supports only buffer shapes it can map or copy; complex highmem multi-page SG cases return `-ENOSYS`. Scratch fallback is page-sized, so callers must respect sizes accepted by this path. Locking combines spinlocks, mutexes, streams, and workqueues, so teardown ordering matters.

Test signals: direct scomp registration, acomp wrapper with virtual and SG buffers, highmem rejection paths, per-CPU scratch allocation on first use and fallback work, stream locking under concurrency, and cleanup after last tfm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/scompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/seed.c -->
# sources/distributed-fs/ceph-client/crypto/seed.c

Purpose: implements the SEED 128-bit block cipher as a legacy `cipher` crypto algorithm.

Important APIs, types, and functions: `struct seed_ctx` stores a 32-word key schedule. `seed_set_key()` expands the 16-byte key using KISA constants and SS tables. `seed_encrypt()` and `seed_decrypt()` run 16 Feistel rounds using the `OP` macro. The algorithm registers as `seed`/`seed-generic`.

Control flow: setkey reads four big-endian 32-bit key words, iterates 16 key-constant rounds, writes two subkeys per round, and rotates word pairs alternately. Encryption reads a 16-byte block as big-endian words, applies the round function in increasing key order, swaps halves in the final output, and writes big-endian output. Decryption uses the same round function in reverse subkey order.

State and persistence: expanded subkeys persist in the tfm context until the tfm is freed or rekeyed. No request-level state is retained by the block cipher primitive.

Dependencies and integration points: uses unaligned big-endian helpers and registers through the legacy `crypto_alg` cipher interface. Modes such as ECB/CBC can wrap it through crypto templates.

Risks: SEED is regionally standardized and legacy; new protocols normally use AES or modern AEADs. Large S-box tables and macro round logic are sensitive to transcription errors. The code assumes the crypto API enforces the 16-byte key length declared in algorithm metadata.

Test signals: RFC 4269/KISA known-answer vectors, encrypt/decrypt inverse tests, mode-template wrapping, unaligned input/output buffers, and module alias lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/seed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/seqiv.c -->
# sources/distributed-fs/ceph-client/crypto/seqiv.c

Purpose: implements the `seqiv` AEAD IV generator template, which derives an 8-byte IV from a sequence number xor a salt and stores that IV in the message.

Important APIs and functions: `seqiv_aead_encrypt()`, `seqiv_aead_decrypt()`, completion helpers, and `seqiv_aead_create()` implement the template. It uses `struct aead_geniv_ctx` from geniv infrastructure and child AEAD requests stored in request context.

Control flow: creation uses `aead_geniv_alloc()` and accepts only children with `ivsize == sizeof(u64)`. Encryption requires at least 8 bytes of cryptlen, copies source to destination for out-of-place requests, handles unaligned IV memory by duplicating it, xors the caller-provided sequence value with the salt, writes the resulting IV into the destination after associated data, and invokes the child AEAD with associated data length increased by 8. Decryption extracts the stored IV from source, increases associated data length by 8, and calls the child.

State and persistence: salt and child tfm persist in the geniv tfm context. Per-request duplicated IV memory is freed in completion and copied back to `req->iv` after successful async encryption.

Dependencies and integration points: depends on `crypto/internal/geniv.h`, AEAD API, `memcpy_sglist()`, and `scatterwalk_map_and_copy()`. Useful for CTR-like AEAD constructions needing sequence-derived nonces.

Risks: nonce uniqueness depends on callers supplying non-repeating sequence values and appropriate salt. The implementation hardcodes an 8-byte IV. Unaligned IV handling changes completion callback/data and must preserve caller completion semantics.

Test signals: AEAD encrypt/decrypt with in-place and out-of-place SGs, unaligned `req->iv`, too-short cryptlen failures, async child completion, IV copyback, and salt xor correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/seqiv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/serpent_generic.c -->
# sources/distributed-fs/ceph-client/crypto/serpent_generic.c

Purpose: implements the generic Serpent block cipher and exports core setkey/encrypt/decrypt helpers for other architecture-specific or mode code.

Important APIs, types, and functions: exported functions are `__serpent_setkey()`, `serpent_setkey()`, `__serpent_encrypt()`, and `__serpent_decrypt()`. The implementation uses `struct serpent_ctx` from `<crypto/serpent.h>`, S-box macros `S0` through `S7`, inverse S-boxes `SI0` through `SI7`, linear transform macros, and key schedule helpers.

Control flow: setkey pads keys up to 256 bits with a `1` byte then zeros, loads little-endian words, expands 132 prekeys with the PHI recurrence, and applies S-boxes to produce round keys. Encryption reads a 16-byte little-endian block, applies initial key xor, 32 Serpent rounds with S-boxes and linear transforms, final key xor, and writes output. Decryption performs inverse rounds in reverse order.

State and persistence: expanded round keys persist in the tfm context. No request state is retained. Core helpers are exported for reuse.

Dependencies and integration points: depends on unaligned little-endian helpers, crypto cipher registration, and public Serpent header definitions. Registers as `serpent`/`serpent-generic`.

Risks: macro-heavy bit-sliced code is hard to review and vulnerable to compiler behavior; the key S-box phase is deliberately marked `noinline` due to past misoptimization. Key padding and round-key indexing are correctness-critical. Serpent is secure but less common than AES, so test coverage matters.

Test signals: official Serpent known-answer vectors for 128/192/256-bit keys, random encrypt/decrypt inverse tests, exported helper users, compiler matrix coverage, unaligned buffers, and module alias lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/serpent_generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sha1.c -->
# sources/distributed-fs/ceph-client/crypto/sha1.c

Purpose: registers library-backed SHA-1 and HMAC-SHA1 shash algorithms with compatible export/import formats.

Important APIs, types, and functions: exports `sha1_zero_message_hash`. SHA-1 wrappers call `sha1_init()`, `sha1_update()`, `sha1_final()`, and `sha1()`. HMAC wrappers call `hmac_sha1_preparekey()`, `hmac_sha1_init()`, `hmac_sha1_update()`, `hmac_sha1_final()`, and `hmac_sha1()`. Export/import helpers append the current partial-block byte count to a block-aligned library context.

Control flow: module init registers `sha1` and `hmac(sha1)`. Hash and HMAC requests delegate to the library. Export subtracts the partial bytes from `bytecount`, copies the context, and stores partial as one byte. Import copies the context and re-adds partial. HMAC import restores the outer state from the tfm key before importing the inner hash context.

State and persistence: per-request shash state lives in descriptor contexts; HMAC key state lives in tfm context. Zero-message hash is static exported data.

Dependencies and integration points: depends on `<crypto/sha1.h>` and crypto shash registration. Used by legacy protocols, HMAC templates, and PKCS#1 signature prefix support.

Risks: SHA-1 is collision-broken for signatures and should be compatibility-only, though HMAC-SHA1 remains different from raw collision resistance. Layout static assertions protect legacy state ABI. Importing HMAC state with a different key would be invalid because outer state comes from current tfm key.

Test signals: SHA-1 and HMAC-SHA1 known-answer vectors, zero-message digest, export/import at partial and block boundaries, algorithm aliases, and PKCS#1 verification with SHA-1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sha1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sha256.c -->
# sources/distributed-fs/ceph-client/crypto/sha256.c

Purpose: registers library-backed SHA-224, SHA-256, HMAC-SHA224, and HMAC-SHA256 shash algorithms.

Important APIs, types, and functions: exports `sha224_zero_message_hash` and `sha256_zero_message_hash`. SHA wrappers delegate to `sha224_*` and `sha256_*` library functions. HMAC wrappers delegate to `hmac_sha224_*` and `hmac_sha256_*`. Shared `__crypto_sha256_export()` and import/core helpers implement state serialization for `struct __sha256_ctx`.

Control flow: module init registers four `shash_alg` entries. Each init/update/final/digest path is a thin wrapper over the library. Export subtracts the partial block bytes from `bytecount`, copies the context, and appends the partial byte count. Import reverses that. HMAC import restores the outer state from the current tfm key before importing the inner SHA context.

State and persistence: descriptor contexts contain SHA or HMAC state. HMAC prepared keys live in tfm context. Exported states are caller-owned snapshots. The zero-message hashes are static exported arrays.

Dependencies and integration points: depends on `<crypto/sha2.h>`, shash internals, and hash consumers including HMAC users and RSA PKCS#1 signature templates.

Risks: export/import depends on fixed offsets and size assertions. The single state-size constant covers SHA-224 and SHA-256 variants through their shared core context. HMAC import must match the key currently installed in the tfm.

Test signals: SHA-224/SHA-256 and HMAC vectors, zero-message hash users, export/import across all partial lengths, core export/import for optimized hash chaining, aliases, and PKCS#1 signature verification with SHA-224/SHA-256.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sha256.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sha3.c -->
# sources/distributed-fs/ceph-client/crypto/sha3.c

Purpose: registers library-backed SHA3-224, SHA3-256, SHA3-384, and SHA3-512 shash algorithms.

Important APIs and functions: init wrappers call `sha3_224_init()`, `sha3_256_init()`, `sha3_384_init()`, or `sha3_512_init()`. Shared update/final wrappers call `sha3_update()` and `sha3_final()`. Digest wrappers call the corresponding one-shot library functions. `crypto_sha3_export_core()` and `crypto_sha3_import_core()` copy the full `struct sha3_ctx`.

Control flow: module init registers four algorithms with digest sizes, block sizes, descriptor size, and core export/import callbacks. Runtime requests are direct library delegations. Unlike SHA-1/SHA-2 wrappers, there is no extra shash state format with partial-byte trailer; core export/import copies the whole sponge state.

State and persistence: descriptor context stores `struct sha3_ctx` for each request. No tfm key state exists. Algorithm registration persists while loaded.

Dependencies and integration points: depends on `<crypto/sha3.h>` and crypto shash internals. SHA3 names are also referenced by RSA PKCS#1 hash-prefix template support.

Risks: full-context copy export/import must remain valid if `struct sha3_ctx` changes. SHA-3 rate/block sizes differ by digest variant, so table entries must match library constants. There is no HMAC-SHA3 wrapper here.

Test signals: FIPS 202 known-answer vectors for all four variants, split update versus one-shot digest, core export/import resume, registration aliases, and PKCS#1 verification with SHA3-256/384/512.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sha3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sha512.c -->
# sources/distributed-fs/ceph-client/crypto/sha512.c

Purpose: registers library-backed SHA-384, SHA-512, HMAC-SHA384, and HMAC-SHA512 shash algorithms.

Important APIs, types, and functions: exports `sha384_zero_message_hash` and `sha512_zero_message_hash`. SHA wrappers delegate to `sha384_*` and `sha512_*`; HMAC wrappers delegate to `hmac_sha384_*` and `hmac_sha512_*`. Shared `__crypto_sha512_export()`, import, and core variants serialize `struct __sha512_ctx`.

Control flow: module init registers four algorithms. Export subtracts the current partial block count from `bytecount_lo`, copies the context, and appends the partial count. Import copies the context and re-adds partial to `bytecount_lo`. HMAC import restores the outer state from the tfm key before importing the inner SHA-512-family context.

State and persistence: descriptor contexts contain SHA-384/SHA-512 or HMAC state; HMAC key state is tfm-resident. Exported state is transient caller data. Static zero-message digest arrays are exported for other kernel users.

Dependencies and integration points: depends on `<crypto/sha2.h>` and the shash framework. Used by HMAC consumers, Kerberos AES-SHA2 profiles through hash implementations, and RSA PKCS#1 signature prefixes.

Risks: state layout static assertions are critical because export/import format must match legacy expectations. Only `bytecount_lo` partial handling is adjusted; the library must maintain high/low counters consistently. HMAC resumed state must use the same key.

Test signals: SHA-384/SHA-512 and HMAC vectors, zero-message digest checks, export/import at 128-byte block boundaries and partial lengths, aliases, and PKCS#1 signatures with SHA-384/SHA-512.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/sha512.c -->
