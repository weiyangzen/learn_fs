# sources/distributed-fs/ceph-client/lib/crypto/tests/chacha20poly1305_kunit.c lines 6184-9085

## Scope

This chunk covers the tail of `lib/crypto/tests/chacha20poly1305_kunit.c`. It begins in the middle of the first ChaCha20-Poly1305 decryption ciphertext vector and continues through all decryption vectors, the XChaCha20-Poly1305 encrypt/decrypt vectors, a test-only 96-bit nonce ChaCha20-Poly1305 helper, the KUnit test body, suite registration, and module metadata.

Most of lines 6184-8819 are static test-vector data. The executable logic starts with `chacha20poly1305_encrypt_bignonce()` at line 8826, then dispatch and assertion helpers, then `test_chacha20poly1305()` at line 8885. The chunk ends by registering the single KUnit case in the `chacha20poly1305` suite and declaring GPL module metadata.

## Purpose

The code validates the kernel's ChaCha20-Poly1305 and XChaCha20-Poly1305 helpers against fixed vectors and scatterlist in-place behavior. It is not production crypto logic, but it is a regression harness for production APIs exported by `<crypto/chacha20poly1305.h>` and their lower-level primitive interactions.

The covered vectors exercise:

- RFC7539-style ChaCha20-Poly1305 decryption with 64-bit nonce input as used by the kernel helper API.
- Empty plaintext/ciphertext cases where the input is only a 16-byte Poly1305 tag.
- Non-empty associated data and empty associated data.
- Multiple plaintext lengths, including one-byte messages and larger generated messages.
- A final ChaCha20-Poly1305 decryption vector marked as expected failure.
- One XChaCha20-Poly1305 encryption vector and the matching decryption vector using a 24-byte nonce.
- In-place scatterlist encryption/decryption using one segment for normal vectors and an optional slow chunk-splitting stress path for up to three segments.

The chunk also includes a local `chacha20poly1305_encrypt_bignonce()` helper so the KUnit test can validate vectors whose nonce length is 12 bytes. The public kernel `chacha20poly1305_encrypt()` interface in this file path receives an 8-byte nonce converted with `get_unaligned_le64()`, so the test-only helper manually composes the 96-bit nonce variant from lower-level ChaCha20 and Poly1305 primitives.

## Important APIs, Types, and Functions

- `struct chacha20poly1305_testvec` is defined earlier in the file and is the common vector descriptor: `input`, `output`, `assoc`, `nonce`, `key`, input length, associated-data length, nonce length, and an optional `failure` boolean.
- `dec_input001` through `dec_input013`, `dec_output001` through `dec_output013`, `dec_assoc*`, `dec_nonce*`, and `dec_key*` provide ChaCha20-Poly1305 decryption vector material. Each `dec_input` is ciphertext plus 16-byte Poly1305 tag; each `dec_output` is expected plaintext. `dec_input013` is listed with `failure = true`.
- `chacha20poly1305_dec_vectors[]` at lines 8600-8629 binds the decryption arrays into descriptors using `sizeof()` for ciphertext/tag length, associated-data length, and nonce length. The final descriptor sets the failure flag.
- `xenc_input001`, `xenc_output001`, `xenc_assoc001`, `xenc_nonce001`, and `xenc_key001` provide a single XChaCha20-Poly1305 encryption vector. The nonce is 24 bytes.
- `xchacha20poly1305_enc_vectors[]` at lines 8721-8725 wraps the XChaCha encryption vector.
- `xdec_input001`, `xdec_output001`, `xdec_assoc001`, `xdec_nonce001`, and `xdec_key001` mirror the XChaCha vector for decryption.
- `xchacha20poly1305_dec_vectors[]` at lines 8817-8821 wraps the XChaCha decryption vector.
- `chacha20poly1305_encrypt_bignonce()` at lines 8826-8858 is a test-only 12-byte-nonce ChaCha20-Poly1305 implementation built from `chacha_init()`, `chacha20_crypt()`, `poly1305_init()`, `poly1305_update()`, and `poly1305_final()`.
- `chacha20poly1305_test_encrypt()` at lines 8860-8875 dispatches encryption vectors by nonce length: 8 bytes go through the public `chacha20poly1305_encrypt()` API, 12 bytes go through the local helper, and any other length fails the KUnit test.
- `decryption_success()` at lines 8877-8883 centralizes expected decrypt result handling. Expected-failure vectors pass only when the decrypt function returns false; normal vectors pass only when the function returns true and the plaintext comparison succeeds.
- `test_chacha20poly1305()` at lines 8885-9071 is the single KUnit test case. It allocates scratch buffers, iterates vector arrays, validates regular and scatterlist APIs, validates XChaCha APIs, and optionally runs the slow chunk-splitting stress loop.
- `chacha20poly1305_test_cases[]`, `chacha20poly1305_test_suite`, and `kunit_test_suite()` at lines 9073-9082 register the test with KUnit under the suite name `chacha20poly1305`.

## Control Flow

Vector setup is static. The decryption vector table maps each group of static arrays into `struct chacha20poly1305_testvec` entries. The XChaCha encrypt and decrypt tables do the same for their single vector each. No runtime construction or mutation of these arrays occurs.

`test_chacha20poly1305()` starts by allocating two 4096-byte buffers with `kunit_kmalloc()`: `computed_output` for out-of-place API results and `input` for the optional scatterlist chunk stress path. `KUNIT_ASSERT_NOT_NULL()` aborts the test if allocation fails, so later loops can assume both buffers exist.

The first loop iterates `chacha20poly1305_enc_vectors`, which are defined earlier in the file. Each iteration clears the full scratch output buffer, calls `chacha20poly1305_test_encrypt()`, and compares the resulting ciphertext plus `POLY1305_DIGEST_SIZE` tag against the expected vector output. This dispatch is where 8-byte nonce vectors use `chacha20poly1305_encrypt()` and 12-byte nonce vectors use `chacha20poly1305_encrypt_bignonce()`.

The second loop reuses encryption vectors to test `chacha20poly1305_encrypt_sg_inplace()`. It skips vectors whose nonce length is not 8 bytes, because the scatterlist API under test takes a 64-bit nonce. For each supported vector, the plaintext is copied into `computed_output`, a single-entry scatterlist is initialized with room for plaintext plus tag, and the in-place API is expected to return true and transform the buffer into the expected ciphertext/tag.

The third loop validates out-of-place `chacha20poly1305_decrypt()` against `chacha20poly1305_dec_vectors`. It clears `computed_output`, decrypts into it, and then calls `decryption_success()` with the returned boolean, the vector's `failure` flag, and a plaintext `memcmp()` over `ilen - POLY1305_DIGEST_SIZE`. Normal vectors require successful authentication plus matching plaintext; the expected-failure vector requires authentication failure.

The fourth loop validates `chacha20poly1305_decrypt_sg_inplace()`. It copies each ciphertext/tag into `computed_output`, initializes a single-entry scatterlist over the full encrypted input length, calls the in-place decrypt API, and evaluates the same success predicate. Successful decryptions leave plaintext in the start of the buffer; failed decryptions are accepted only when marked as expected failure.

The fifth and sixth loops validate the XChaCha APIs. `xchacha20poly1305_encrypt()` is checked by comparing output ciphertext/tag against the XChaCha encryption vector, and `xchacha20poly1305_decrypt()` is checked with `decryption_success()` against the matching XChaCha decryption vector. These APIs take the vector nonce pointer directly rather than converting an 8-byte nonce to `u64`.

The final loop is gated by `IS_ENABLED(DEBUG_CHACHA20POLY1305_SLOW_CHUNK_TEST)`. When enabled at build time, it exhaustively splits buffers of total length `POLY1305_DIGEST_SIZE` through 1024 bytes into up to three scatterlist segments. For each split `(i, j)`, it zeroes the scatterlist input, encrypts in place with `chacha20poly1305_encrypt_sg_inplace()`, computes the expected all-zero out-of-place encryption, compares the full ciphertext/tag, decrypts out of place and verifies zero plaintext, then decrypts in place and verifies the scatterlist buffer returns to zero plaintext. Any failure jumps to `chunkfail` and reports the length and split indexes.

Suite registration is direct: a single `KUNIT_CASE(test_chacha20poly1305)` is placed in the suite named `chacha20poly1305`, and `kunit_test_suite()` emits the module/init integration KUnit needs to discover and run the case.

## State and Persistence Behavior

All vector arrays are `static const u8` and persist for the module lifetime in read-only data. They hold deterministic test inputs and expected outputs, not mutable state.

`chacha20poly1305_dec_vectors[]`, `xchacha20poly1305_enc_vectors[]`, and `xchacha20poly1305_dec_vectors[]` are also static const tables. They persist as descriptors pointing to the byte arrays and encode lengths using compile-time `sizeof()` expressions, reducing the risk of manual length mismatches in the table.

`chacha20poly1305_encrypt_bignonce()` uses only stack-local crypto state: `struct poly1305_desc_ctx`, `struct chacha_state`, a union for the one-time Poly1305 key and length footer, a 16-byte ChaCha state bottom row, and an eight-word little-endian key array. It leaves no persistent state after returning. The Poly1305 padding source is `page_address(ZERO_PAGE(0))`, a global zero page used only as immutable zero bytes for padding updates.

`test_chacha20poly1305()` uses KUnit-managed allocations. Buffers allocated with `kunit_kmalloc()` are tied to the test lifetime and automatically released by KUnit cleanup. The test intentionally reuses the buffers across loops, clearing or copying before each assertion to avoid stale output from earlier vectors influencing later comparisons.

Scatterlist state is stack-local. `sg_src[3]` is initialized as either a single segment with `sg_init_one()` or a three-entry table with `sg_init_table()`, `sg_set_buf()`, and `sg_init_marker()` in the slow chunk path. In-place crypto APIs mutate the pointed-to buffer contents but not any persistent file-level state.

There is no filesystem persistence, no runtime configuration update, no global mutable module state, and no interaction with Ceph client state. The only persisted externally visible result is KUnit pass/fail reporting.

## Dependencies and Integration Points

- Public AEAD helper APIs from `<crypto/chacha20poly1305.h>`: `chacha20poly1305_encrypt()`, `chacha20poly1305_decrypt()`, `chacha20poly1305_encrypt_sg_inplace()`, `chacha20poly1305_decrypt_sg_inplace()`, `xchacha20poly1305_encrypt()`, and `xchacha20poly1305_decrypt()`.
- Primitive crypto APIs from `<crypto/chacha.h>` and `<crypto/poly1305.h>`: `struct chacha_state`, `chacha_init()`, `chacha20_crypt()`, `struct poly1305_desc_ctx`, `poly1305_init()`, `poly1305_update()`, `poly1305_final()`, `POLY1305_KEY_SIZE`, and `POLY1305_DIGEST_SIZE`.
- Key and nonce handling helpers from `<linux/unaligned.h>`: `get_unaligned_le64()` for normal 8-byte nonce vectors and `get_unaligned_le32()` for loading the 256-bit key into the local 12-byte nonce helper.
- Kernel endian helpers: `cpu_to_le64()` writes associated-data and plaintext lengths into the Poly1305 footer in little-endian order.
- Memory helpers: `kunit_kmalloc()`, `memset()`, `memcpy()`, and `memcmp()` are used for scratch allocation, buffer setup, and assertions.
- Scatterlist APIs: `struct scatterlist`, `sg_init_one()`, `sg_init_table()`, `sg_set_buf()`, and `sg_init_marker()` exercise in-place crypto over both contiguous and optionally split buffers.
- KUnit APIs from `<kunit/test.h>`: `KUNIT_ASSERT_NOT_NULL()`, `KUNIT_EXPECT_TRUE_MSG()`, `KUNIT_FAIL()`, `KUNIT_CASE()`, `struct kunit_case`, `struct kunit_suite`, and `kunit_test_suite()`.
- MM/kernel helpers: `ZERO_PAGE(0)` and `page_address()` supply zero padding for the test-only Poly1305 implementation; `GFP_KERNEL`, `ARRAY_SIZE()`, and `IS_ENABLED()` provide standard kernel allocation and compile-time feature gating.
- Build/module integration: `MODULE_DESCRIPTION()` and `MODULE_LICENSE()` identify the test module and its GPL license metadata.

## Risks and Edge Cases

- The assigned range starts mid-array at line 6184. The first logical decryption vector begins before the chunk boundary, so final per-file reconciliation should merge this with the previous chunk to describe `dec_input001` from its true declaration at line 6170.
- `chacha20poly1305_encrypt_bignonce()` is a test-only implementation of the 12-byte nonce construction. A mistake in this helper could make 12-byte nonce encryption vector failures look like production helper regressions, even though the production `chacha20poly1305_encrypt()` path here uses an 8-byte nonce.
- The 12-byte nonce helper manually builds the AEAD transcript: one-time Poly1305 key from ChaCha block 0, associated-data padding, ciphertext update, ciphertext padding, little-endian lengths, and final tag. Any change to padding calculations `(0x10 - len) & 0xf` or length encoding would silently invalidate expected vectors.
- `page_address(ZERO_PAGE(0))` assumes the zero page can be directly addressed in this KUnit environment. If this test is moved to a context where that assumption is invalid, the padding updates would need a different zero buffer source.
- The fixed `MAXIMUM_TEST_BUFFER_LEN` is 4096 bytes. Current vectors and slow chunk lengths fit within it, but adding larger vectors without increasing the buffer would risk out-of-bounds writes or truncated comparisons.
- Decryption comparisons use `ilen - POLY1305_DIGEST_SIZE`. Vectors must always have `ilen >= POLY1305_DIGEST_SIZE`; a malformed vector shorter than the tag size would underflow the unsigned size and produce an invalid comparison range.
- Expected-failure handling ignores plaintext comparison when authentication fails. That is appropriate for authentication failure, but it means expected-failure vectors only assert a false return, not a specific output buffer clearing or preservation policy.
- Scatterlist encryption tests only cover 8-byte nonce vectors. The 12-byte nonce helper has no scatterlist equivalent in this file, so in-place coverage is limited to the production 64-bit nonce API.
- The regular scatterlist loops use a single scatterlist segment. Multi-segment behavior is covered only when `DEBUG_CHACHA20POLY1305_SLOW_CHUNK_TEST` is enabled, so default builds may miss chunk-boundary regressions.
- The slow chunk path has cubic-ish nested iteration over lengths and split points up to 1024 bytes. It is intentionally compile-time gated because enabling it in routine test runs can be expensive.
- In the slow chunk path, encryption writes the tag after the plaintext portion of the same backing buffer. The scatterlist length passed to `sg_set_buf()` must cover `total_len` so the in-place API has tag space.
- The chunk stress path compares all-zero plaintext/ciphertext cases with `enc_key001` and nonce zero. It is good for chunking and padding boundaries, but not broad key/AD/nonce diversity.
- `chacha20poly1305_test_encrypt()` calls `KUNIT_FAIL()` for unsupported nonce lengths but has a `void` return, so a bad vector nonce length can still leave `computed_output` in a partially meaningful state before the following expectation runs. The failure is recorded, but later diagnostics may show a secondary mismatch.
- Vector data is large and hand-maintained. The `sizeof()` usage protects table lengths, but it does not prove that `input`, `output`, `assoc`, `nonce`, and `key` arrays are semantically paired correctly.

## Test Signals

- KUnit should report suite `chacha20poly1305` with case `test_chacha20poly1305`.
- Normal ChaCha20-Poly1305 encryption vectors pass when computed ciphertext plus 16-byte tag exactly matches each `chacha20poly1305_enc_vectors[]` output.
- Normal ChaCha20-Poly1305 scatterlist encryption vectors pass when `chacha20poly1305_encrypt_sg_inplace()` returns true and mutates the single buffer to the same ciphertext/tag as the out-of-place vector.
- Decryption vectors pass when every normal vector returns true and produces matching plaintext, while `dec_input013` returns false because its descriptor sets `failure = true`.
- Scatterlist decryption vectors pass under the same success predicate, validating authentication and in-place plaintext recovery for the normal vectors and authentication failure for the expected-failure vector.
- XChaCha20-Poly1305 encryption passes when the 24-byte nonce vector produces `xenc_output001`.
- XChaCha20-Poly1305 decryption passes when `xdec_input001` authenticates and recovers `xdec_output001`.
- With `DEBUG_CHACHA20POLY1305_SLOW_CHUNK_TEST=y`, failures identify the exact `total_len/i/j` split that broke chunked scatterlist encryption or decryption.
- Useful regression additions would include malformed ciphertext shorter than `POLY1305_DIGEST_SIZE`, tampered associated data, tag-only messages with non-empty associated data, multi-segment scatterlists in the default test path, and XChaCha expected-failure coverage.

## Chunk Boundary Notes

Earlier chunks define the file header, includes, `struct chacha20poly1305_testvec`, the comment explaining vector origins, all ChaCha20-Poly1305 encryption vectors, and the start of `dec_input001`. This chunk should be merged with those earlier sections for a complete per-file report so the vector provenance and encryption/decryption symmetry are not split across artificial chunk boundaries.

This chunk is the final per-file control section: it supplies the remaining vector data, all executable KUnit test flow, and suite/module registration.
