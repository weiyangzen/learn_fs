# sources/distributed-fs/ceph-client/lib/crypto/tests/chacha20poly1305_kunit.c lines 1-6183

## Scope

This chunk covers the front portion of the ChaCha20-Poly1305 KUnit test source. It includes the SPDX/copyright header, crypto and KUnit includes, the shared `struct chacha20poly1305_testvec`, the explanatory vector provenance comment, all 118 encryption-side ChaCha20-Poly1305 test vector byte arrays, the `chacha20poly1305_enc_vectors[]` descriptor table, and the beginning of `dec_input001[]`.

The executable KUnit harness, decryption-vector table, XChaCha20-Poly1305 vectors, helper functions, suite registration, and module metadata are outside this chunk. This range is therefore primarily static test data and descriptor wiring, not algorithm implementation.

## Purpose

The purpose of this chunk is to provide known-answer test material for the kernel ChaCha20-Poly1305 AEAD implementation. Each encryption vector binds plaintext input, expected ciphertext plus 16-byte Poly1305 tag, associated data, nonce, and key into a common test-vector shape consumed later by the KUnit runner.

The first vector is the RFC7539 section 2.8.2 AEAD example. Subsequent generated vectors cover varied payload and AAD lengths, including empty plaintext, empty AAD, short one-byte cases, block-sized and non-block-sized messages, and larger messages. Later marked vectors come from Wycheproof and specifically stress RFC7539 behavior, miscellaneous edge cases, integer-overflow-oriented sizes, special tag cases, and Poly1305 intermediate-sum boundaries. The comments state that the Wycheproof coverage is used on the encrypt side because the test is mostly stressing primitive interactions rather than only the combined AEAD construction.

## Important APIs, Types, and Data

- `#include <crypto/chacha20poly1305.h>` supplies the public kernel ChaCha20-Poly1305 and XChaCha20-Poly1305 APIs exercised by the later harness.
- `#include <crypto/chacha.h>` and `#include <crypto/poly1305.h>` support later test-only construction of a 96-bit-nonce helper path.
- `#include <kunit/test.h>` provides KUnit allocation and assertion APIs used after this chunk.
- `#include <linux/unaligned.h>`, `<linux/init.h>`, `<linux/mm.h>`, `<linux/kernel.h>`, and `<linux/slab.h>` provide kernel helpers used by later code in the same file.
- `struct chacha20poly1305_testvec` is the central descriptor type. It stores pointers to `input`, `output`, `assoc`, `nonce`, and `key`; byte lengths for input, associated data, and nonce; and a `failure` flag used by decryption-side negative tests. In this chunk's encryption table, `failure` is left at the zero-initialized default.
- `enc_inputNNN[]` arrays hold plaintext for encryption known-answer tests. The set includes zero-length inputs and payloads ranging from single bytes through multi-kilobyte test material.
- `enc_outputNNN[]` arrays hold the exact expected encryption output: ciphertext followed by `POLY1305_DIGEST_SIZE` bytes of authentication tag. For every encryption vector, expected output length is `ilen + 16`.
- `enc_assocNNN[]` arrays hold associated data authenticated but not encrypted. Several are empty, while Wycheproof cases include many non-empty boundary lengths.
- `enc_nonceNNN[]` arrays hold either 8-byte nonces for the exported kernel ChaCha20-Poly1305 API or 12-byte RFC7539-style nonces for the later test-only helper path. In this chunk, 69 encryption vectors use 8-byte nonces and 49 use 12-byte nonces.
- `enc_keyNNN[]` arrays are all 32 bytes, matching `CHACHA20POLY1305_KEY_SIZE`.
- `chacha20poly1305_enc_vectors[]` maps `enc_input001` through `enc_input118` to their corresponding output, AAD, nonce, and key arrays, and records sizes with `sizeof(...)` so empty arrays and exact nonce lengths are preserved without hand-maintained constants.

## Control Flow

There is no executable control flow in lines 1-6183. The only runtime-relevant structure is the static `chacha20poly1305_enc_vectors[]` array initializer.

The later `test_chacha20poly1305()` function iterates this table with `ARRAY_SIZE(chacha20poly1305_enc_vectors)`. For each vector, it calls a wrapper that dispatches by `nlen`: 8-byte nonces go to `chacha20poly1305_encrypt()`, while 12-byte nonces go through a local test-only 96-bit-nonce implementation built from ChaCha20 and Poly1305 primitives. The later harness then compares the generated output against `output` over `ilen + POLY1305_DIGEST_SIZE`.

The later harness also reuses only the 8-byte-nonce entries from this table for scatterlist in-place encryption tests via `chacha20poly1305_encrypt_sg_inplace()`. That means this chunk's nonce-length mix deliberately controls which vectors exercise the public in-place API and which exercise the RFC7539 helper.

At the chunk tail, `dec_input001[]` begins with the RFC7539 ciphertext/tag bytes that correspond to the first encryption vector. The rest of that decryption vector and all decryption-table wiring are outside this chunk.

## State and Persistence Behavior

All material in this chunk is file-scope `static const` data. It is compiled into read-only kernel test object storage and has no mutation, allocation, reference counting, locking, or persistence side effects.

The only "state" encoded here is declarative test state:

- Pointer relationships from each `chacha20poly1305_testvec` entry to its byte arrays.
- Length metadata derived by `sizeof(...)`.
- Default zero initialization of omitted `failure` fields in the encryption vector table.
- Nonce width selection encoded by each `nlen` value.

Because array lengths are inferred at compile time, edits to a byte array automatically update the table length fields if the initializer continues to use `sizeof(array)`. However, the semantic relationship between input length and output length remains implicit and is validated only by the later KUnit comparisons.

## Dependencies and Integration Points

- Kernel crypto API: the data feeds tests for `chacha20poly1305_encrypt()`, `chacha20poly1305_encrypt_sg_inplace()`, and later decryption/XChaCha APIs defined through `<crypto/chacha20poly1305.h>`.
- ChaCha20 and Poly1305 primitives: 12-byte RFC7539 nonce vectors integrate with the later file-local helper that calls `chacha_init()`, `chacha20_crypt()`, `poly1305_init()`, `poly1305_update()`, and `poly1305_final()`.
- KUnit: the vector table is consumed by the later KUnit case `test_chacha20poly1305`, which allocates temporary buffers and reports per-vector failures.
- Scatterlist crypto path: 8-byte nonce vectors are reused for in-place scatterlist encryption coverage, so this chunk indirectly tests both contiguous-buffer and SG-buffer implementations.
- RFC7539 and Wycheproof: vector provenance is part of the integration contract. The first vector anchors standards conformance; the marked Wycheproof blocks target edge cases that are easy to miss in hand-written coverage.
- Kernel build/test object layout: because all arrays are `static const`, no symbol is exported. Integration is local to this KUnit translation unit.

## Risks and Edge Cases

- The encryption outputs include both ciphertext and tag. Accidentally treating `enc_outputNNN[]` as ciphertext-only would shift comparisons and make tag coverage disappear.
- Empty arrays are intentional. The table's `sizeof(empty_array)` records zero, so replacing empty arrays with `NULL` or special cases would change how zero-length plaintext/AAD coverage is represented.
- Nonce length is semantically significant. An 8-byte nonce vector exercises the public kernel API with `get_unaligned_le64()` later; a 12-byte nonce vector exercises the local RFC7539 helper. Changing byte counts or adding/removing nonce bytes changes the code path under test.
- The `failure` field is present in the shared type but not initialized in encryption entries. Adding a positional field before it or changing initializer order would silently corrupt table interpretation.
- Large static vector data is easy to edit inconsistently. For every vector, `output` must remain exactly `input length + 16`; `key` must remain 32 bytes; and nonce length must remain either 8 or 12 for the later dispatcher.
- Wycheproof vectors target subtle Poly1305 and length-boundary behavior. Trimming "redundant-looking" vectors can remove coverage for integer-size transitions, tag corner cases, and carry/intermediate-sum behavior.
- The first decryption array starts inside this chunk but is incomplete here. Any per-file narrative must merge this with the following chunk before drawing conclusions about decryption coverage.
- This source is a KUnit test, but it lives under the crypto test tree in a Ceph-client source snapshot. Changes can affect kernel crypto validation even though no production Ceph code calls these arrays directly.

## Test Signals

The direct test signal from this chunk is the encryption known-answer corpus:

- `ARRAY_SIZE(chacha20poly1305_enc_vectors)` should be 118.
- Every encryption table entry should produce bytes identical to its `enc_outputNNN[]` over `ilen + POLY1305_DIGEST_SIZE`.
- All 8-byte nonce entries should also pass `chacha20poly1305_encrypt_sg_inplace()` when the later harness copies plaintext into an in-place buffer.
- All 12-byte nonce entries should pass through the test-only RFC7539 helper and validate primitive interaction between ChaCha20 key-stream generation and Poly1305 authentication.
- Empty plaintext/AAD vectors should produce tag-only or small ciphertext-plus-tag outputs without special-case failures.
- Boundary vectors should cover payload/AAD sizes around 16-byte Poly1305 block boundaries, 64-byte ChaCha blocks, and larger message sizes.
- Wycheproof-labeled groups should preserve coverage for RFC7539 cases, miscellaneous edge cases, integer-overflow-oriented lengths, special tag cases, and Poly1305 intermediate-sum edge cases.

Useful maintenance checks for this chunk include verifying that every `enc_inputNNN`, `enc_outputNNN`, `enc_assocNNN`, `enc_nonceNNN`, and `enc_keyNNN` referenced by `chacha20poly1305_enc_vectors[]` exists; that no output array length differs from input length plus 16; that each key is 32 bytes; and that no nonce length outside 8 or 12 is introduced unless the later dispatcher is extended.

## Chunk Boundary Notes

This chunk should be merged with later chunks for any final per-file report. The executable harness that consumes these vectors starts after the full vector corpus, around the later helper functions and KUnit suite registration. The decryption side is only partially visible here: `dec_input001[]` begins at line 6170 and continues beyond the assigned range.
