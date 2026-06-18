# sources/distributed-fs/ceph-client/crypto/testmgr.h lines 5625-12671

## Scope

This chunk covers a large middle range of Linux crypto self-test vector declarations in `sources/distributed-fs/ceph-client/crypto/testmgr.h`. It starts inside the final long SHA-384-style hash vector, closes that array at line 5736, then declares vector arrays for SHA-512, Whirlpool, HMAC, CMAC/XCBC/CBC-MAC, DES/3DES, Blowfish, Twofish, Serpent, SM4 skcipher modes, and the beginning of SM4-GCM AEAD vectors.

The chunk ends in the middle of `sm4_gcm_tv_template`; later lines in `testmgr.h` finish that AEAD array and continue into SM4-CCM and other algorithms. The material here is declarative test data rather than executable implementation code, but it is directly consumed by `testmgr.c` when algorithms are registered and exercised.

## Purpose

The purpose of this range is to pin known-answer tests for crypto algorithms that Ceph's vendored Linux client crypto tree can expose through the kernel crypto API. These vectors validate digest outputs, keyed MAC outputs, block cipher encryption/decryption, chaining-mode IV behavior, stream-like CTR edge cases, storage-oriented LRW/XTS modes, ciphertext stealing, and authenticated encryption output for SM4-GCM.

The vector families in this chunk are:

- Hash/MAC vectors: SHA-512, Whirlpool-512/384/256, HMAC-MD5, HMAC-RIPEMD160, HMAC-SHA1, HMAC-SHA224/256/384/512, HMAC-SHA3-224/256/384/512, AES-CMAC, 3DES-CMAC, AES-XCBC, and AES-CBC-MAC.
- Legacy and general-purpose block ciphers: DES, 3DES, Blowfish, Twofish, and Serpent in ECB, CBC, and CTR forms.
- Disk/storage modes: Twofish LRW/XTS and Serpent LRW/XTS generated from AES LRW/XTS reference vectors.
- SM4 vectors: ECB-style block tests, CBC, CTR, RFC3686-style CTR, CTS over CBC, XTS, and the beginning of GCM AEAD.

The vectors provide regression coverage for both algorithm math and crypto API contract behavior: key handling, FIPS skips, weak-key rejection, IV mutation semantics, in-place/out-of-place request paths, scatterlist fragmentation, alignment, async completion, and optional SIMD-disable paths.

## Important APIs, Types, And Data

This chunk primarily initializes three `testmgr.h` structures:

- `struct hash_testvec`: `key`, `plaintext`, `digest`, `psize`, `ksize`, plus optional expected `setkey_error`, `digest_error`, and `fips_skip`.
- `struct cipher_testvec`: `key`, `iv`, `iv_out`, `ptext`, `ctext`, `klen`, `len`, optional weak-key flag `wk`, `setkey_error`, `crypt_error`, and `fips_skip`.
- `struct aead_testvec`: `key`, `iv`, `ptext`, `assoc`, `ctext`, `klen`, `plen`, `alen`, `clen`, and optional authentication/key/error flags. In this chunk it is used only for the opening part of `sm4_gcm_tv_template`.

Important declared arrays include:

- `sha512_tv_template`: NIST/kerneli SHA-512 vectors for empty input, short ASCII inputs, long NIST patterns, and 1023-byte binary inputs.
- `wp512_tv_template`, `wp384_tv_template`, `wp256_tv_template`: Whirlpool vectors over standard text messages. The 384/256 variants reuse the Whirlpool digest prefix length expected by the target algorithm.
- `hmac_md5_tv_template`, `hmac_rmd160_tv_template`, `hmac_sha1_tv_template`: RFC-style HMAC vectors with short keys, repeated-byte keys, truncation-oriented messages, and keys larger than the hash block size.
- `hmac_sha224_tv_template` and `hmac_sha256_tv_template`: HMAC vectors including RFC 4231-style large 131-byte keys for SHA-224 and a broader SHA-256 set with short, block-size, oversized, and long-message cases.
- `aes_cmac128_tv_template`, `des3_ede_cmac64_tv_template`, and `aes_xcbc128_tv_template`: keyed MAC vectors for zero-length, partial-block, full-block, and multi-block messages.
- `aes_cbcmac_tv_template`: CBC-MAC over AES for 16, 33, 63, and 65-byte inputs, including AES-128 and AES-256 keys.
- `des_tv_template`, `des_cbc_tv_template`, `des_ctr_tv_template`: DES vectors, including weak-key rejection tests with `.wk = 1` and `.setkey_error = -EINVAL`, CBC IV output checks, and CTR wrap/non-block-size cases.
- `des3_ede_tv_template`, `des3_ede_cbc_tv_template`, `des3_ede_ctr_tv_template`: 3DES known-answer tests with 24-byte keys, larger 496-byte payloads, CBC IV outputs, and CTR partial-length coverage.
- `bf_tv_template`, `bf_cbc_tv_template`, `bf_ctr_tv_template`: Blowfish vectors over 8-byte blocks, variable key sizes up to 56 bytes, CBC and CTR large-payload cases, and CTR final partial blocks.
- `tf_tv_template`, `tf_cbc_tv_template`, `tf_ctr_tv_template`, `tf_lrw_tv_template`, `tf_xts_tv_template`: Twofish vectors covering 16/24/32-byte keys, CBC/CTR edge cases, LRW tweak keys, and XTS double-key layouts.
- `serpent_tv_template`, `serpent_cbc_tv_template`, `serpent_ctr_tv_template`, `serpent_lrw_tv_template`, `serpent_xts_tv_template`: analogous Serpent vectors, including generated LRW/XTS suites and CTR IV-output checks.
- `sm4_tv_template`, `sm4_cbc_tv_template`, `sm4_ctr_tv_template`, `sm4_ctr_rfc3686_tv_template`, `sm4_cts_tv_template`, `sm4_xts_tv_template`: SM4 block/mode vectors from standard examples and generated AES-mode equivalents.
- `sm4_gcm_tv_template`: begins with an RFC 8998 Appendix A.1 vector, then generated AES-GCM-style vectors with SM4 keys, IVs, plaintext, AAD, and `ciphertext || tag` lengths.

Several arrays include comments stating their provenance, such as NIST/kerneli for SHA-512, the original HMAC RFCs for MD5/SHA1/RIPEMD160/SHA2, generated LRW/XTS/CTS vectors, and RFC 8998 for SM4-GCM.

## Control Flow

There is no local control flow in this header span. The operational flow is driven by `testmgr.c`:

1. `alg_test_descs[]` maps algorithm names to these arrays through `__VECS(...)`, for example `cmac(aes)` to `aes_cmac128_tv_template`, `cbc(des)` to `des_cbc_tv_template`, `ctr(twofish)` to `tf_ctr_tv_template`, `ecb(sm4)` to `sm4_tv_template`, and `gcm(sm4)` to `sm4_gcm_tv_template` in the later descriptor table.
2. Hash and MAC descriptors call `alg_test_hash()`. It verifies that unkeyed vectors precede keyed vectors, splits those groups when needed for optional-key algorithms, then calls `__alg_test_hash()`.
3. `__alg_test_hash()` allocates `ahash` and, when available, `shash` transforms, allocates state buffers, and runs every `hash_testvec` through `test_hash_vec()`.
4. `test_hash_vec()` runs each vector across default and fuzzed `testvec_config` layouts. The shash and ahash paths exercise `digest()`, `init/update/final`, `finup`, state export/import, scatterlist splits, no-SIMD paths, and result-buffer overrun checks.
5. Cipher descriptors call either the single-block cipher path or the skcipher path. The skcipher path sets keys, prepares IVs, builds in-place or out-of-place scatterlists, encrypts or decrypts, checks request-structure integrity, verifies ciphertext/plaintext, and compares `iv_out` where present.
6. AEAD descriptors call `alg_test_aead()`. For SM4-GCM vectors begun here, the input is AAD plus plaintext for encryption or AAD plus authenticated ciphertext for decryption; expected `ctext` includes the authentication tag.

The arrays in this chunk therefore form the fixed known-answer layer that `testmgr.c` combines with many runtime request configurations. A single vector can be tested repeatedly with different scatterlist boundaries, alignment offsets, finalization styles, and async request flags.

## State And Persistence Behavior

The vectors are `static const` data compiled into the crypto test manager. They do not persist mutable runtime state to disk and do not modify Ceph filesystem metadata, kernel keyrings, or user data.

Runtime state is transient:

- Hash tests allocate transform/request objects and temporary result/state buffers, then compare output against the immutable `.digest` field.
- Cipher tests allocate request buffers and IV storage. If `.iv` is absent, `testmgr.c` supplies an all-zero IV. If `.iv_out` is present, the post-operation IV buffer must match it.
- Weak-key DES tests set `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS` through `.wk` and expect `setkey()` to fail with `.setkey_error = -EINVAL`.
- FIPS handling is declarative. Vectors marked `.fips_skip = 1` are skipped when `fips_enabled` is true.
- The `zeroed_string` global is used as a stable all-zero byte source for zero-input or zero-key vectors. Length fields, not C string terminators, determine how much data is consumed.

Because data blobs are represented as adjacent C string literals with explicit lengths, the length fields are part of the persistent test contract. A mismatch between a literal and `.psize`, `.len`, `.plen`, `.clen`, or `.alen` can silently turn into a false failure or insufficient coverage.

## Dependencies And Integration Points

This header depends on the crypto test harness definitions at the top of `testmgr.h` and on the consumers in `testmgr.c`. It integrates with algorithm implementations in the same source tree, including:

- Hash/MAC implementations such as `sha1.c`, SHA-2/SHA-3 implementations elsewhere in the tree, `rmd160.c`, `cmac.c`, `xcbc.c`, and CBC-MAC support.
- Block ciphers such as `blowfish_common.c`, `twofish_generic.c`, `serpent_generic.c`, `sm4_generic.c`, DES/3DES implementations, and mode wrappers such as `cbc.c`, `ctr.c`, `cts.c`, `gcm.c`, and XTS/LRW providers.
- `testmgr.c` descriptor entries, which must reference the exact array names and count all elements through `__VECS`.
- Kernel crypto API entry points: `crypto_alloc_ahash`, `crypto_alloc_shash`, `crypto_skcipher_setkey`, `crypto_skcipher_encrypt/decrypt`, `crypto_aead_setkey`, `crypto_aead_encrypt/decrypt`, and the lower-level `crypto_cipher_encrypt_one/decrypt_one` path.

Several algorithms in the descriptor table use explicit generic driver names, such as `cmac-aes-lib`, `cbcmac-aes-lib`, and generic AES/SM4 mode compositions. These mappings are important when `testmgr.c` compares an optimized implementation against a known generic implementation during slow tests.

## Risks And Edge Cases

The most important correctness risk is data/length drift. This chunk contains thousands of bytes of hex literals; the test manager trusts explicit length fields. Off-by-one errors in `.psize`, `.len`, `.plen`, `.clen`, `.alen`, or key lengths can make valid implementations fail or, worse, stop testing trailing bytes.

The chunk starts and ends inside arrays. Line 5625 is part of a previous hash vector's plaintext, and line 12671 is inside one `sm4_gcm_tv_template` ciphertext/tag literal. Chunk-level research or automated extraction must not treat this range as syntactically standalone C.

Keyed and unkeyed hash ordering matters. `alg_test_hash()` requires unkeyed vectors to appear before keyed vectors for optional-key algorithms. The HMAC and MAC arrays in this range are all keyed; SHA-512 and Whirlpool arrays are unkeyed. Reordering mixed arrays elsewhere can cause test manager rejection before vector execution.

DES weak-key vectors intentionally expect `setkey()` failure only when `.wk` requests weak-key rejection. If an implementation ignores `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS`, these vectors will flag it. Conversely, setting `.wk` on normal vectors would make them fail on implementations that correctly reject weak keys.

IV post-state checks are mode-specific. CBC vectors generally expect IV mutation to the final ciphertext block; many CTR vectors expect either a counter-advanced IV or unchanged high-order IV fields depending on the mode semantics. Incorrect `.iv_out` values turn API-state behavior into false failures even if ciphertext is correct.

CTR and CTS vectors cover non-block-multiple lengths such as 247, 499, 503, 17, 31, 47, and 189 bytes. These are high-value edge cases because implementations often split full-block fast paths from tail handling.

LRW and XTS vectors use composite keys and tweak IVs. Their `.klen` values include both data and tweak keys, so shortening them to the base cipher key size would test a different algorithm contract.

Several old algorithms in this chunk are not modern security recommendations. DES, 3DES, Blowfish, MD5, SHA1, and RIPEMD160 vectors remain valuable for compatibility and regression testing, but should not be interpreted as endorsement for new protocol design.

The SM4-GCM vectors begun here rely on AEAD convention that `.ctext` is authenticated ciphertext concatenated with the tag. `.clen` includes both parts. Treating the tag as separate data would break the test-manager comparison path.

## Test Signals

Useful verification signals for this chunk are crypto self-test outcomes rather than standalone unit tests:

- Building the crypto test manager should compile `testmgr.h`; because this range has very large adjacent string literals, syntax errors or missing commas fail at compile time.
- Loading or registering affected algorithms should trigger `testmgr.c` known-answer tests for names such as `sha512`, `wp512`, `hmac(sha256)`, `cmac(aes)`, `ecb(des)`, `cbc(des3_ede)`, `ctr(blowfish)`, `xts(twofish)`, `xts(serpent)`, `ecb(sm4)`, `cts(cbc(sm4))`, and `gcm(sm4)`.
- Hash/MAC failures report as `alg: shash` or `alg: ahash` wrong-result, setkey, digest, export/import, or buffer-overrun errors tied to a vector number and test configuration.
- Cipher failures report as `alg: skcipher` wrong-result, wrong-output-IV, setkey, request-corruption, scatterlist-corruption, or buffer-overrun errors.
- DES weak-key vectors should pass by observing the expected `-EINVAL` from setkey when weak keys are forbidden.
- FIPS-mode runs should skip vectors marked `.fips_skip = 1`, which are present in this line range for some non-FIPS cipher vectors.
- Slow-test/fuzz-test runs are especially valuable because the same static vectors are replayed across randomized scatterlist divisions, key/IV alignments, no-SIMD settings, and in-place/out-of-place layouts.

For edits to this chunk, high-signal validation is a crypto self-test build and execution path that exercises the named algorithms, plus focused review that every literal length, key length, IV length, and authenticated ciphertext length still matches the intended vector.
