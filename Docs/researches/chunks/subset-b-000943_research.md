# sources/distributed-fs/ceph-client/crypto/testmgr.h lines 33815-38163

## Scope

This chunk is the final slice of `crypto/testmgr.h`. It starts inside the tail of the preceding `adiantum_xchacha20_aes_tv_template` data and then defines the remaining crypto test-vector tables through the header guard terminator. The source path is under a Ceph-client snapshot tree, but this file is Linux kernel crypto self-test data, not Ceph filesystem logic.

The visible declarations cover:

- Cipher vectors for generic CTS-CBC AES, ESSIV-CBC AES, AES-XCTR, and AES-HCTR2.
- Compression/decompression vectors for deflate, LZO, LZO-RLE, LZ4, LZ4HC, and zstd.
- Hash/checksum vectors for CRC32, CRC32C, xxhash64, and BLAKE2b-160/256/384/512.
- AEAD/authenc vectors for ESSIV authenc-HMAC-SHA256-CBC-AES and Kerberos AES/Camellia CTS authentication modes.
- Local helper data and macros: `COMP_BUF_SIZE`, `struct comp_testvec`, `blake2_ordered_sequence`, and `AUTHENC_KEY_HEADER()`.

## Purpose

`testmgr.h` supplies known-answer tests to the kernel crypto test manager. This chunk extends coverage for storage-oriented encryption modes, checksum algorithms, compression transforms, and Kerberos encryption profiles. The data is consumed by `crypto/testmgr.c`, which maps algorithm names to these tables through `__VECS(...)` and runs the appropriate test harness (`alg_test_skcipher`, `alg_test_aead`, `alg_test_hash`, or `alg_test_comp`) when implementations are registered or explicitly tested.

The purpose is defensive validation rather than runtime feature implementation. Every table describes inputs, keys, IVs or associated data, lengths, and expected outputs so the crypto API can reject broken drivers or regressions in generic fallback implementations.

## Important APIs, Types, And Tables

The chunk uses the file-level test-vector contracts defined near the top of `testmgr.h`: `struct cipher_testvec`, `struct aead_testvec`, and `struct hash_testvec`. It also introduces `struct comp_testvec`, a fixed-buffer compression vector with `inlen`, `outlen`, `input[COMP_BUF_SIZE]`, and `output[COMP_BUF_SIZE]`; `COMP_BUF_SIZE` is 512 bytes, so all compression inputs and expected outputs in this chunk must fit that static storage.

`cts_mode_tv_template` contains RFC3962-derived AES CTS-CBC vectors using the 16-byte key for "chicken teriyaki" and plaintext lengths around the CTS boundary: 17, 31, 32, 47, 48, and 64 bytes. These are registered in `testmgr.c` for `cts(cbc(aes))` and validate ciphertext stealing around partial final blocks and exact block multiples.

The compression tables are paired by direction. `deflate_comp_tv_template` and `deflate_decomp_tv_template` cover raw deflate with the documented `winbits=-11`, default compression, and max memory-level parameters. `lzo_comp_tv_template`, `lzo_decomp_tv_template`, `lzorle_comp_tv_template`, and `lzorle_decomp_tv_template` validate LZO and LZO-RLE encodings over repeated short strings and a UBIFS-themed text payload. `lz4_comp_tv_template`, `lz4_decomp_tv_template`, `lz4hc_comp_tv_template`, and `lz4hc_decomp_tv_template` use a 255-byte LZ4 description and distinguish normal LZ4 from high-compression output size. `zstd_comp_tv_template` and `zstd_decomp_tv_template` cover short and longer zstd frames; the decompression inputs include frame checksums/trailers that make them slightly larger than the compression outputs in the matching compression tests.

`crc32_tv_template` and `crc32c_tv_template` contain keyed and unkeyed checksum vectors. They test empty input, "abcdefg", a seed-only case, several 40-byte windows, a 240-byte concatenation, and a large 2048-byte deterministic pattern. The key fields represent initial CRC values; digest fields are four-byte expected results in the byte order expected by the crypto hash API.

`xxhash64_tv_template` adds 64-bit xxhash vectors for empty, one-byte, short, and 222-byte messages with the seed `b1 79 37 9e 00 00 00 00` and unseeded cases. These are registered by `testmgr.c` for `xxhash64` through `alg_test_hash`.

`essiv_aes_cbc_tv_template` reuses AES-CBC-style data but supplies ESSIV-derived IV material. It covers AES-128, AES-192, and AES-256 keys, includes a 496-byte long vector, and is registered for `essiv(cbc(aes),sha256)`. `essiv_hmac_sha256_aes_cbc_tv_temp` covers `essiv(authenc(hmac(sha256),cbc(aes)),sha256)` with AEAD-style associated data, auth tags appended to ciphertext, and authenc keys containing an rtattr header plus authentication key plus encryption key.

`blake2_ordered_sequence` is a 256-byte ascending byte string reused by the BLAKE2b vectors. `blake2b_160_tv_template`, `blake2b_256_tv_template`, `blake2b_384_tv_template`, and `blake2b_512_tv_template` validate digest-size variants with empty input, selected input sizes from 1 to 256 bytes, and keyed modes with 1-byte, 32-byte, and 64-byte keys. Their digest fields use compound `u8[]` literals rather than string literals.

`aes_xctr_tv_template` and `aes_hctr2_tv_template` are wide-block/storage-mode AES vectors. `aes_xctr_tv_template` tests AES-XCTR with 16-, 24-, and 32-byte keys, 16-byte IVs, and message sizes including small, partial, and multi-block payloads. `aes_hctr2_tv_template` tests HCTR2, using 32-byte IV/tweak values and AES-256 keys over 16-, 32-, 128-, 255-, and 512-byte messages. `testmgr.c` registers HCTR2 as `hctr2(aes)` with the generic driver `hctr2_base(xctr(aes-lib),polyval-lib)`.

`AUTHENC_KEY_HEADER(enckeylen)` is endian-dependent. On little-endian builds it emits the rtattr header as `08 00 01 00`; on big-endian builds it emits `00 08 00 01`; both append a four-byte `crypto_authenc_key_param` encryption-key length. Kerberos and ESSIV authenc vectors depend on this macro so the same source builds correct key blobs on both endian families.

`krb5_test_aes128_cts_hmac_sha256_128` and `krb5_test_aes256_cts_hmac_sha384_192` implement RFC8009 Appendix A vectors for `authenc(hmac(sha256),cts(cbc(aes)))` and `authenc(hmac(sha384),cts(cbc(aes)))`. They model Kerberos confounder-plus-plaintext inputs and include cases for no plaintext, less than one AES block, exactly one block, and more than one block. The AES-128 profile uses a 16-byte integrity key plus 16-byte encryption key and a 16-byte tag; the AES-256 profile uses a 32-byte encryption-key length field, a 24-byte integrity key portion in the authenc layout shown here, a 32-byte encryption key, and 24-byte authentication tags.

`krb5_test_camellia_cts_cmac` implements RFC6803 section 10 vectors for `krb5enc(cmac(camellia),cts(cbc(camellia)))`. It covers Camellia-128 and Camellia-256 profiles with plaintext sizes of 0, 1, 9, 13, and 30 bytes after the 16-byte confounder. Unlike the RFC8009 AES authenc vectors, these entries omit `.assoc` and `.alen`, so the harness treats associated data as absent.

## Control Flow

There is no executable control flow in this header slice. The effective flow is data-driven:

1. Crypto implementations register algorithm names with the kernel crypto API.
2. `testmgr.c` looks up the algorithm in its `alg_test_descs` table.
3. The descriptor selects one of this chunk's vector arrays through `__VECS(...)`.
4. The selected harness allocates a transform, calls setkey or setauthsize where required, encrypts/decrypts or hashes/compresses/decompresses each vector, and compares the result and length against the literal expected fields.

The vector layout controls the test path. `cipher_testvec` entries drive skcipher encryption and decryption, using NULL IV as zero IV where applicable and explicit `.iv` where supplied. `aead_testvec` entries drive associated-data handling and expect ciphertext plus tag in `.ctext`; `.clen` must equal payload ciphertext plus authentication tag length. `hash_testvec` entries drive keyed or unkeyed digest operation based on `.key` and `.ksize`. `comp_testvec` entries drive compression or decompression depending on whether the table is connected as `.comp` or `.decomp` in `testmgr.c`.

Endian preprocessor branches affect construction of authenc key blobs before tests run. The harness sees only the compiled string literal; a wrong branch or length field changes setkey parsing, not later encryption flow.

## State And Persistence Behavior

This chunk defines only `static const` data and preprocessor macros. There is no mutable state, no filesystem persistence, and no runtime allocation in this file. Persistence is compile-time: the arrays are built into the kernel or module image that includes `testmgr.h`.

The test-manager state exists elsewhere. During testing, `testmgr.c` allocates transform objects and request buffers, then reads these vectors as immutable expected data. The only "state" encoded here is semantic: seeds in checksum keys, authenc rtattr/encryption-key-length headers, IVs, associated data, plaintext/ciphertext lengths, compression output lengths, and digest sizes.

The most important state constraints are length consistency and byte-order consistency. `.len`, `.plen`, `.clen`, `.alen`, `.psize`, `.ksize`, `.inlen`, and `.outlen` tell the harness how many bytes of each string or array are meaningful. Several literals contain embedded NULs and are not C strings in the semantic sense; their explicit lengths are authoritative.

## Dependencies And Integration Points

The header depends on `testmgr.h`'s earlier type definitions and on kernel integer aliases such as `u8`. It is included by `crypto/testmgr.c`, where the arrays are wired to algorithm descriptors. Important mappings visible in `testmgr.c` include:

- `cts_mode_tv_template` -> `cts(cbc(aes))`.
- deflate vectors -> `deflate` and `deflate-iaa`.
- `crc32_tv_template`, `crc32c_tv_template`, and `xxhash64_tv_template` -> hash tests for `crc32`, `crc32c`, and `xxhash64`.
- BLAKE2b tables -> `blake2b-160`, `blake2b-256`, `blake2b-384`, and `blake2b-512`.
- ESSIV vectors -> `essiv(cbc(aes),sha256)` and `essiv(authenc(hmac(sha256),cbc(aes)),sha256)`.
- `aes_hctr2_tv_template` -> `hctr2(aes)`.
- Kerberos AES CTS-HMAC vectors -> authenc CTS AES algorithm names.
- `krb5_test_camellia_cts_cmac` -> `krb5enc(cmac(camellia),cts(cbc(camellia)))`.

Algorithm dependencies are the corresponding crypto API implementations and generic fallback drivers, including AES, CBC, CTS, ESSIV, SHA-256, HMAC, authenc, CMAC, Camellia, POLYVAL, XCTR, HCTR2, CRC32, CRC32C, xxhash64, BLAKE2b, deflate, LZO, LZ4, and zstd.

The vectors also integrate with FIPS policy through the descriptors in `testmgr.c`, not directly in this header. Some algorithms using these vectors are marked `fips_allowed`, while BLAKE2b is explicitly not FIPS allowed in the descriptor table.

## Risks And Edge Cases

The biggest risk is silent vector corruption. Because most fields are opaque byte strings with explicit lengths, a one-byte edit, bad line splice, incorrect `.len`, or missing escape sequence can cause a self-test failure that looks like an implementation regression.

Chunk line 33815 begins mid-array in the tail of `adiantum_xchacha20_aes_tv_template`. A final merged per-file report should reconcile that the first visible data belongs to the previous declaration that began before this chunk. This research file treats it as trailing context and focuses on declarations that start or end in this line range.

Compression vectors are bounded by `COMP_BUF_SIZE`. New or edited vectors must keep both source and expected output within 512 bytes and must keep `.inlen`/`.outlen` aligned with the meaningful bytes, not with C string termination.

The checksum vectors rely on keyed initial states and byte-order-specific digest representation. Altering seed values, digest byte order, or treating digest strings as host-endian integers would invalidate tests across architectures.

Authenc key layout is sensitive. `AUTHENC_KEY_HEADER()` and the ESSIV authenc literals encode netlink rtattr-style metadata and encryption-key lengths. Wrong endian bytes, incorrect `klen`, or mismatched Ki/Ke sizing can fail during setkey before cryptographic comparison is reached.

AEAD vectors require `.clen` to include the authentication tag. In the Kerberos tables, the plaintext includes a 16-byte confounder and the comments describe only the application plaintext. Miscounting confounder, plain text, or tag length would cause false failures.

CTS, XCTR, HCTR2, and ESSIV are storage-mode and block-boundary-sensitive algorithms. Their vectors intentionally include partial final blocks, exact block multiples, long payloads, all-zero padding regions in IVs or associated data, and nonstandard tweak sizes. Simplifying or deduplicating them can reduce coverage in exactly the cases these modes are meant to protect.

BLAKE2b digest fields use `u8[]` compound literals. This is valid for the static const table as used here, but it differs from the many string-literal digests elsewhere in the file; mechanical transformations that assume every digest is a string literal would break these entries.

## Test Signals

Build coverage should compile the crypto test manager with endian variants where possible, because both ESSIV/authenc and Kerberos authenc key headers have `__LITTLE_ENDIAN` branches.

Runtime self-test signals should include successful `testmgr` coverage for `cts(cbc(aes))`, `deflate`, `deflate-iaa` where available, `crc32`, `crc32c`, `xxhash64`, BLAKE2b digest sizes, `essiv(cbc(aes),sha256)`, `essiv(authenc(hmac(sha256),cbc(aes)),sha256)`, `hctr2(aes)`, `authenc(hmac(sha256),cts(cbc(aes)))`, `authenc(hmac(sha384),cts(cbc(aes)))`, and `krb5enc(cmac(camellia),cts(cbc(camellia)))`.

High-value negative signals are setkey failures for malformed authenc key headers, length mismatches in compression outputs, checksum digest mismatches on big-endian or little-endian hosts, and AEAD decrypt failures where the tag length or associated-data length is miscounted.

Regression tests should exercise both generic drivers and accelerated drivers. The generic-driver names in `testmgr.c` provide a baseline for AES, SHA/HMAC, CBC/CTS/ESSIV, HCTR2, CRC, and BLAKE2b behavior; hardware or architecture-specific drivers should match these same vectors byte for byte.

For storage-mode algorithms, test output should include short and long I/O sizes: CTS boundary sizes, ESSIV 16/32/64/496-byte cases, HCTR2 16/32/128/255/512-byte cases, and zstd/LZ4/LZO compression/decompression length checks. These are the most likely areas for off-by-one, final-block, or request-walk bugs.
