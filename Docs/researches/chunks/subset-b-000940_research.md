# sources/distributed-fs/ceph-client/crypto/testmgr.h lines 12672-19875

## Scope

This chunk covers the third large slice of Linux crypto `testmgr.h` in the `sources/distributed-fs/ceph-client` snapshot. The file path is under a Ceph client source tree, but this header is the Linux kernel crypto self-test vector catalog, not Ceph distributed-filesystem logic.

The requested range starts in the tail of `sm4_gcm_tv_template` and ends inside the long generated payload of `aes_ctr_rfc3686_tv_template`. Complete templates inside the range include SM4 CCM/MAC vectors, CAST6 cipher-mode vectors, AES ECB/CBC/CTR/LRW/XTS vectors, and many `authenc(hmac(...),...)` AEAD vectors for AES, DES, and 3DES. The range also includes the start of `aes_ctr_rfc3686_tv_template`, but not its full closing state; adjacent chunks must reconcile the partial edge arrays.

## Purpose

`testmgr.h` supplies static known-answer test vectors consumed by `crypto/testmgr.c` to validate kernel crypto algorithm implementations. This chunk's vectors exercise symmetric cipher, hash/MAC, and AEAD behavior for algorithms that are often hardware-accelerated or mode-wrapped:

- SM4 authenticated modes and MAC modes: GCM tail, CCM, CBC-MAC, CMAC, and XCBC.
- CAST6 block cipher modes: raw block cipher, CBC, CTR, LRW, and XTS.
- AES block cipher modes: raw AES, CBC, CTR, LRW, XTS, and the beginning of RFC3686 CTR.
- `authenc` AEAD compositions using HMAC-MD5, HMAC-SHA1, HMAC-SHA224, HMAC-SHA256, HMAC-SHA384, or HMAC-SHA512 with AES-CBC, AES-CTR-RFC3686, DES-CBC, or 3DES-CBC.
- Null-cipher `authenc` coverage for HMAC-MD5 and HMAC-SHA1 with `ecb(cipher_null)`.

The data is meant to catch incorrect key setup, IV handling, authentication tag production, digest truncation/length handling, endian-sensitive authenc key parsing, counter increment/wrap behavior, tweak computation for disk-encryption modes, and scatterlist-independent encryption/decryption correctness.

## Important APIs, Types, And Data

The important local types are defined near the top of `testmgr.h`, outside this chunk. `struct cipher_testvec` holds key, IV, optional expected output IV, plaintext, ciphertext, weak-key flags, key length, data length, and expected error fields. `struct hash_testvec` holds optional key, plaintext, expected digest, input size, key size, and expected errors. `struct aead_testvec` holds key, IV, plaintext, associated data, authenticated ciphertext with tag appended, verification-failure flags, key length, plaintext length, AAD length, ciphertext length, and expected error fields.

Complete arrays in this chunk:

- `sm4_ccm_tv_template`: seven AEAD CCM vectors. The first is from RFC8998 appendix A.2; the rest are generated from AES-CCM-style vectors and cover AAD, zero-length plaintext, zero-length AAD, 8-byte tags, 16-byte tags, and a large 719-byte plaintext with a 735-byte ciphertext-plus-tag.
- `sm4_cbcmac_tv_template`: three keyed hash/MAC vectors with 16-, 33-, and 63-byte inputs, all with 16-byte keys and 16-byte MAC outputs.
- `sm4_cmac128_tv_template`: three keyed CMAC vectors mirroring the CBC-MAC message sizes but with CMAC-specific digests.
- `sm4_xcbc128_tv_template`: six XCBC vectors generated from AES-XCBC-style cases, including zero-length input, short unaligned input, exactly one block, and multi-block/non-block-aligned messages.
- `cast6_tv_template`: four raw CAST6 block-cipher vectors. Three are RFC2612 vectors for 128-, 192-, and 256-bit keys over a zero block, and one larger generated vector with 496 bytes.
- `cast6_cbc_tv_template`: one 496-byte generated CBC vector with `iv_out`, checking final chaining-state propagation.
- `cast6_ctr_tv_template`: two generated CTR vectors, including a 17-byte non-block-multiple case and a 496-byte case, both with expected `iv_out`.
- `cast6_lrw_tv_template`: one 512-byte LRW vector using a 48-byte combined key and a 16-byte sector/tweak IV.
- `cast6_xts_tv_template`: one 512-byte XTS vector using a 64-byte combined key and a 16-byte tweak.
- `aes_tv_template`: four AES raw block vectors: FIPS-197 AES-128/192/256 single-block vectors plus a larger generated AES-256 vector.
- `aes_cbc_tv_template`: five CBC vectors from RFC3602, NIST SP800-38A, and Crypto++, with `iv_out` values for final chaining state.
- `hmac_md5_aes_cbc_tv_temp`: seven authenc vectors combining HMAC-MD5 with AES-CBC.
- `hmac_md5_ecb_cipher_null_tv_template`: two authenc vectors combining HMAC-MD5 with `ecb(cipher_null)`.
- `hmac_sha1_aes_cbc_tv_temp`: seven authenc vectors combining HMAC-SHA1 with AES-CBC.
- `hmac_sha1_aes_ctr_rfc3686_tv_temp`: seven authenc vectors combining HMAC-SHA1 with AES-CTR-RFC3686.
- `hmac_sha1_ecb_cipher_null_tv_temp`: two authenc vectors combining HMAC-SHA1 with `ecb(cipher_null)`.
- `hmac_sha224_aes_cbc_tv_temp`, `hmac_sha256_aes_cbc_tv_temp`, `hmac_sha384_aes_cbc_tv_temp`, and `hmac_sha512_aes_cbc_tv_temp`: seven vectors each for SHA-2 HMAC variants over AES-CBC.
- `hmac_sha224_aes_ctr_rfc3686_tv_temp`, `hmac_sha256_aes_ctr_rfc3686_tv_temp`, `hmac_sha384_aes_ctr_rfc3686_tv_temp`, `hmac_sha512_aes_ctr_rfc3686_tv_temp`, and `hmac_md5_aes_ctr_rfc3686_tv_temp`: seven vectors each for HMAC plus AES-CTR-RFC3686 authenc transforms.
- `hmac_md5_des_cbc_tv_temp`, `hmac_sha1_des_cbc_tv_temp`, `hmac_sha224_des_cbc_tv_temp`, `hmac_sha256_des_cbc_tv_temp`, `hmac_sha384_des_cbc_tv_temp`, and `hmac_sha512_des_cbc_tv_temp`: one DES-CBC authenc vector each.
- `hmac_md5_des3_ede_cbc_tv_temp`, `hmac_sha1_des3_ede_cbc_tv_temp`, `hmac_sha224_des3_ede_cbc_tv_temp`, `hmac_sha256_des3_ede_cbc_tv_temp`, `hmac_sha384_des3_ede_cbc_tv_temp`, and `hmac_sha512_des3_ede_cbc_tv_temp`: one 3DES-CBC authenc vector each.
- `aes_lrw_tv_template`: nine LRW vectors, including published-style disk encryption cases and generated cases with different AES key sizes and nontrivial 16-byte tweaks.
- `aes_xts_tv_template`: five XTS vectors with combined keys and sector/tweak IVs, including full-sector 512-byte cases and generated cases.
- `aes_ctr_tv_template`: five CTR vectors, including NIST SP800-38A AES-128/192/256 cases and generated vectors that stress counter carry and non-block-multiple payload length.

Partial arrays at chunk boundaries:

- Lines 12672-12865 are the tail of `sm4_gcm_tv_template`, specifically the completion of a 60-byte generated vector and a 719-byte generated vector. The array declaration and earlier SM4-GCM cases are in the previous chunk.
- Lines 19442-19875 start `aes_ctr_rfc3686_tv_template` and include the six RFC3686 vectors plus the start of a very long Crypto++ generated vector. The remainder of that vector is in the next chunk.

The authenc test keys embed Linux `rtattr`-style authentication key metadata followed by encryption key length and key material. Several arrays conditionally encode the first two key bytes differently under `__LITTLE_ENDIAN` versus big-endian builds, so the same source produces native-endian `struct rtattr` headers.

## Control Flow

There is no executable control flow in this chunk. Runtime flow comes from `testmgr.c`, which indexes these arrays through `__VECS()` or `____VECS()` entries in the algorithm test descriptor table.

At runtime, the crypto test manager looks up an algorithm name such as `cbc(aes)`, `ctr(aes)`, `xts(aes)`, `ccm(sm4)`, `cmac(sm4)`, or `authenc(hmac(sha256),cbc(aes))`. It allocates the appropriate `crypto_skcipher`, `crypto_ahash`/`shash`, or `crypto_aead` transform, calls setkey/setauthsize where needed, builds requests from the vector fields, encrypts or hashes plaintext, compares output against `ctext` or `digest`, then decrypts authenticated ciphertext where applicable and compares back to `ptext`.

For `cipher_testvec`, the manager tests both encryption and decryption. If `iv_out` is present, stateful modes such as CBC and CTR are also expected to leave the IV/counter in the documented post-operation state. For `hash_testvec`, the manager compares produced MAC/digest bytes to `digest` and honors expected setkey or digest errors if present. For `aead_testvec`, `ctext` represents `ciphertext || authentication tag`; encryption output and decryption verification are both checked unless `novrfy` or expected-error fields say otherwise.

The chunk's vectors are reached from `testmgr.c` mappings for algorithms including `cbc(aes)`, `ecb(aes)`, `ctr(aes)`, `lrw(aes)`, `xts(aes)`, `rfc3686(ctr(aes))`, `cbc(cast6)`, `ecb(cast6)`, `ctr(cast6)`, `lrw(cast6)`, `xts(cast6)`, `ccm(sm4)`, `cbcmac(sm4)`, `cmac(sm4)`, `xcbc(sm4)`, and multiple `authenc(...)` compositions.

## State And Persistence Behavior

All data in this chunk is `static const`, so it is compiled into read-only kernel image/module storage. There is no filesystem persistence, no mutation of these arrays at runtime, and no per-instance state owned by the header.

The stateful behavior being tested belongs to crypto algorithm implementations, not to this header. The vectors record expected state transitions through fields such as `iv_out`, expected ciphertext, expected plaintext recovery, and expected authentication tag bytes. CBC vectors verify final IV equals the last ciphertext block; CTR vectors verify counter advancement across partial and full blocks; LRW and XTS vectors verify tweak-dependent transformations; authenc vectors verify AAD handling and tag construction.

The authenc key layout is persistent test data with architecture-sensitive bytes selected at compile time. The `#ifdef __LITTLE_ENDIAN` blocks ensure the `rtattr` header used by authenc key parsing is byte-ordered as kernel code expects on the target architecture. This means the semantic vector is stable across architectures, but the literal compiled key bytes differ.

## Dependencies And Integration Points

This header depends on the test manager's vector structs and on shared helpers such as `zeroed_string`, which supplies zero plaintext/key material in several templates. The arrays are not exported directly; inclusion by `testmgr.c` makes them visible to the crypto self-test descriptor table.

Primary integration is with the Linux crypto API self-test path. The relevant call sites in `testmgr.c` bind these arrays to algorithm descriptors using `__VECS()`/`____VECS()`. These descriptors are exercised during crypto algorithm registration self-tests, explicit testmgr runs, and module load paths depending on kernel configuration and crypto self-test policy.

The chunk also integrates with standards and reference-vector sources:

- RFC8998 for SM4-GCM and SM4-CCM test material.
- RFC2612 for CAST6 raw block vectors.
- FIPS-197 for AES block vectors.
- RFC3602 and NIST SP800-38A for AES-CBC and AES-CTR cases.
- RFC3686 for nonce-suffixed AES-CTR key/IV composition.
- Crypto++ and generated vectors for long-message, edge-length, disk-mode, and counter-carry coverage.

The algorithms being tested are implemented elsewhere under the Linux crypto subsystem, potentially in generic C, architecture-specific assembly, and hardware driver backends. Passing these vectors is an integration requirement for those implementations to be accepted by the crypto API self-test framework.

## Risks And Edge Cases

The main risk is silent corruption of literal byte strings or length fields. Because the vectors are static data, a one-byte typo in `key`, `iv`, `ptext`, `assoc`, `ctext`, or `digest`, or a mismatch in `klen`, `plen`, `alen`, `clen`, `psize`, or `len`, will look like an algorithm regression. Large generated vectors make such errors difficult to spot visually.

Boundary coverage is intentionally dense. The chunk includes zero-length AEAD plaintext, zero-length AAD, short non-block-multiple CTR data, 17-byte CTR data, 33- and 63-byte MAC inputs, 499-byte generated CTR payloads, 512-byte disk-mode sectors, and a 719-byte SM4 AEAD payload. Implementations that only work for block-aligned or short messages can fail here.

Endian-specific authenc keys are a maintenance hazard. The `rtattr` header bytes must match `__LITTLE_ENDIAN` handling while the rest of the key layout stays common. Incorrectly refactoring those literals could break big-endian or little-endian builds differently.

Authenc vectors depend on the combined-key contract: authentication key metadata, authentication key bytes, encryption key length, and encryption key bytes must be parsed exactly as `authenc` expects. A mismatch can cause `setkey()` failure, wrong encryption key selection, or tags computed over the wrong associated data.

Authenticated ciphertext layout is another common trap. AEAD `ctext` is ciphertext concatenated with tag, not a detached tag stored separately. `clen` must include both encrypted plaintext and tag bytes, while `plen` is only the original plaintext length.

Mode-specific state can fail independently of raw cipher correctness. AES or CAST6 ECB vectors may pass while CBC `iv_out`, CTR counter carry, LRW tweak multiplication, XTS data-unit tweak handling, or RFC3686 nonce/counter composition fails.

The requested chunk boundaries split arrays. The previous chunk owns the declaration and initial vectors for `sm4_gcm_tv_template`; the next chunk owns the completion of the final long `aes_ctr_rfc3686_tv_template` vector. Any automated per-file report must avoid treating those partial edges as standalone complete arrays.

## Test Signals

Relevant positive signals are successful crypto self-tests for:

- `ccm(sm4)`, `gcm(sm4)` edge coverage from the partial boundary, `cbcmac(sm4)`, `cmac(sm4)`, and `xcbc(sm4)`.
- `ecb(cast6)`, `cbc(cast6)`, `ctr(cast6)`, `lrw(cast6)`, and `xts(cast6)`.
- `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, `lrw(aes)`, `xts(aes)`, and `rfc3686(ctr(aes))`.
- `authenc(hmac(md5),cbc(aes))`, `authenc(hmac(sha1),cbc(aes))`, `authenc(hmac(sha224),cbc(aes))`, `authenc(hmac(sha256),cbc(aes))`, `authenc(hmac(sha384),cbc(aes))`, and `authenc(hmac(sha512),cbc(aes))`.
- `authenc(hmac(md5),rfc3686(ctr(aes)))` and SHA1/SHA224/SHA256/SHA384/SHA512 variants over RFC3686 AES-CTR.
- HMAC-MD5/SHA1/SHA224/SHA256/SHA384/SHA512 authenc variants over DES-CBC and 3DES-CBC.
- `authenc(hmac(md5),ecb(cipher_null))` and `authenc(hmac(sha1),ecb(cipher_null))`.

Failure signals include `alg: skcipher: encryption failed`, `decryption failed`, `wrong result`, `wrong IV`, `aead: decryption failed`, `aead: auth failed`, `hash: digest failed`, or `setkey failed` messages naming the affected transform. For this chunk, failures should be triaged by checking whether the implementation mishandles key length, IV length, counter advancement, final IV state, AAD inclusion, authentication tag length, or authenc key parsing before assuming the reference vector is wrong.

Architecture-specific test coverage should include at least one little-endian and one big-endian build for the authenc templates because the key literals include conditional native-endian `rtattr` headers. Hardware-accelerated AES/SM4/CAST6 implementations should be compared against generic implementations using the same vectors to isolate acceleration bugs from shared test-data issues.
