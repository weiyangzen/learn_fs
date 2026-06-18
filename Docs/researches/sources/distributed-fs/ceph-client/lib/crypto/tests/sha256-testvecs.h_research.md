# sources/distributed-fs/ceph-client/lib/crypto/tests/sha256-testvecs.h

Purpose: generated SHA-256 test-vector data for the common KUnit hash test template. It declares `hash_testvecs[]`, where each entry binds a message length to a `SHA256_DIGEST_SIZE` expected digest, plus consolidated expected digests for all hash and HMAC vector outputs.

Important APIs/types/functions: the file is data-only and expects the including C file to have `u8`, `size_t`, and `SHA256_DIGEST_SIZE` in scope. `hash_testvecs[]`, `hash_testvec_consolidated`, and `hmac_testvec_consolidated` are consumed by `hash-test-template.h` after the including test driver defines the SHA-256 macro layer.

Control flow: none locally. The generated lengths intentionally cover empty input, short inputs, block-boundary and near-boundary cases around 64 and 128 bytes, multi-block inputs, and larger 16 KiB data. The template loops over these lengths, generates deterministic message bytes, compares individual digests, then verifies the consolidated digest over all vector results.

State and persistence: static const data only; no mutable state, allocation, I/O, or persistence. Dependencies are the SHA-256 constants and the shared test template contract.

Integration points: included by `sha256_kunit.c`, which binds these generic names to the SHA-256 implementation and HMAC-SHA256 implementation.

Risks: stale generated data would make the KUnit test enforce incorrect outputs; manual edits are high risk because the table has no self-describing input bytes. Boundary coverage depends on `gen-hash-testvecs.py` and the shared deterministic input generator matching the template.

Test signals: strong regression signal for digest correctness, block padding, length accounting, and HMAC coverage across boundary lengths.
