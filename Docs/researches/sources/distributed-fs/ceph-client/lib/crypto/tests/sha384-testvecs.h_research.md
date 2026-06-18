# sources/distributed-fs/ceph-client/lib/crypto/tests/sha384-testvecs.h

Purpose: generated SHA-384 test vectors for the common KUnit hash and HMAC template.

Important APIs/types/functions: defines `hash_testvecs[]` entries with `SHA384_DIGEST_SIZE` digests, `hash_testvec_consolidated`, and `hmac_testvec_consolidated`. The including driver supplies all function and type bindings.

Control flow: none locally. The table covers empty input, short data, SHA-512-family 128-byte block boundaries and nearby sizes, 256/511/513/1000/3333-byte cases, and larger 4 KiB to 16 KiB cases. The shared template iterates these lengths and validates digest/HMAC behavior against the arrays.

State and persistence: constant read-only data only. It has no allocation, side effects, I/O, or persistent state.

Dependencies: `<crypto/sha2.h>` definitions in the including file, `SHA384_DIGEST_SIZE`, `u8`, `size_t`, and the `hash-test-template.h` variable contract.

Integration points: included only by `sha384_kunit.c` in this subset. It tests the SHA-384 API, which is usually implemented as SHA-512 with different IV and truncated output.

Risks: table size makes human review error-prone; corrupted vector bytes can either hide implementation bugs or create false failures. Since inputs are generated elsewhere, future changes to deterministic test data generation must regenerate this header.

Test signals: good coverage for SHA-384 padding, length encoding, update/final sequencing, and HMAC key preparation/finalization.
