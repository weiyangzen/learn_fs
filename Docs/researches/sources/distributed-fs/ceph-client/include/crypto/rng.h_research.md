# sources/distributed-fs/ceph-client/include/crypto/rng.h

Purpose: exposes the public crypto API for RNG algorithms and standard RNG byte generation.

Important APIs, types, and flow: `struct rng_alg` provides `generate`, optional `seed`, seed size, and base algorithm metadata. `struct crypto_rng` wraps the transform. `crypto_stdrng_get_bytes()` calls `__crypto_stdrng_get_bytes()` when standard RNG support is enabled or returns `-EOPNOTSUPP` otherwise. Helpers allocate/free RNG transforms, access algorithm metadata, generate bytes with optional source/additional input, get bytes without source input, reset/seed a transform, and query seed size.

State and persistence: RNG/DRBG state is transform-local and may include entropy and reseed counters in implementation code. No persistence is declared here.

Dependencies and integration: depends on generic crypto allocation and is consumed by key generation, DRBG, and callers needing crypto API RNG rather than the core random subsystem.

Risks and test signals: risks include using unseeded transforms, ignoring `-EOPNOTSUPP`, weak seeding, and generate buffer length handling. Signals include RNG/DRBG known-answer tests, reseed tests, disabled Kconfig builds, concurrent generate calls, and failure-injection for seed/generate callbacks.
