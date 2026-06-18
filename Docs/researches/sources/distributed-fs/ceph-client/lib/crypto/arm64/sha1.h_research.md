# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha1.h

## Purpose
ARM64 SHA1 architecture dispatch header that selects the SHA1 Crypto Extensions transform when available.

## Important APIs, Types, And Functions
Declares `sha1_ce_transform`, defines static key `have_ce`, overrides `sha1_blocks()`, and provides `sha1_mod_init_arch()`.

## Control Flow
`sha1_blocks()` branches to `sha1_ce_transform()` inside `scoped_ksimd()` when the static key is likely and `may_use_simd()` succeeds. Otherwise it calls `sha1_blocks_generic()`. Init enables the key if `cpu_have_named_feature(SHA1)`.

## State, Persistence, And Dependencies
Hash state is caller-owned. Persistent state is a single static key initialized after CPU feature detection. Dependencies include `asm/simd.h`, `linux/cpufeature.h`, and the generic SHA1 implementation.

## Integration Points
Included by the generic SHA1 library when arm64 arch acceleration is configured. It is used by HMAC and FIPS self-test paths that rely on SHA1 compatibility.

## Risks
Incorrect use of CE without `may_use_simd()` can break kernel execution contexts. The fallback must remain present for CPUs lacking SHA1 CE. Algorithm-level risk is SHA1's weak collision security.

## Test Signals
Feature-gated boot tests, KUnit or crypto testmgr SHA1 vectors, and forced static-key off runs verify the wrapper.
