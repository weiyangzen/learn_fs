# sources/distributed-fs/ceph-client/include/crypto/internal/kdf_selftest.h

Purpose: provides a reusable inline self-test harness for kernel key-derivation functions built on `crypto_shash`.

Important APIs, types, and flow: `struct kdf_testvec` packages key material, input keying material, one `kvec` info value, and expected output. `kdf_test()` allocates an output buffer, allocates the named shash transform, calls the supplied KDF setkey and generate functions, compares the output with the expected vector, frees resources, and reports errors.

State and persistence: all state is temporary allocation and the shash transform; no persistence exists. Test buffers may contain key material and are freed after use.

Dependencies and integration: depends on `crypto/hash.h`, `linux/uio.h`, allocation, logging, and specific KDF implementations such as SP800-108 helpers.

Risks and test signals: the helper currently maps transform allocation errors to `-ENOMEM` and uses raw `memcmp()` for known-answer data. Signals are KDF known-answer tests, error-path coverage for setkey/generate failures, allocation-failure injection, and verification that expected lengths match destination lengths.
