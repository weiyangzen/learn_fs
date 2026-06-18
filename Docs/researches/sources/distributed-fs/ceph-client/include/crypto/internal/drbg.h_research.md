# sources/distributed-fs/ceph-client/include/crypto/internal/drbg.h

Purpose: supplies small internal helpers for NIST SP800-90A DRBG derivation functions.

Important APIs, types, and flow: `drbg_cpu_to_be32()` writes a host integer to a caller-provided buffer as big-endian bytes. `struct drbg_string` stores a buffer pointer, length, and list node so DRBG code can concatenate input strings by list traversal without copying. `drbg_string_fill()` initializes one list element.

State and persistence: no owned state beyond caller-managed list nodes and referenced buffers. No persistent state exists.

Dependencies and integration: relies on Linux endian conversion and list heads. It integrates with DRBG derivation and reseed code that needs SP800-90A ordered concatenation of entropy, nonce, personalization, additional input, and counters.

Risks and test signals: risks are unaligned buffer casts, incorrect list ordering, and referenced buffer lifetime. Signals include DRBG known-answer tests, reseed/additional-input vectors, KASAN/UBSAN for unaligned accesses, and big-endian/little-endian cross-build coverage.
