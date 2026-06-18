# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue.c

## Purpose
This shared C glue registers arm64 accelerated AES skcipher algorithms for either ARMv8 Crypto Extensions or NEON, depending on the including wrapper.

## APIs, Types, And Functions
It defines contexts `crypto_aes_xts_ctx` and `crypto_aes_essiv_cbc_ctx`, key callbacks `skcipher_aes_setkey`, `xts_set_key`, and `essiv_cbc_set_key`, and request handlers for ECB, CBC, CTS-CBC, ESSIV-CBC, CTR, XCTR, and XTS encryption/decryption. The `aes_algs[]` table registers `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, `xctr(aes)`, `xts(aes)`, `cts(cbc(aes))`, and `essiv(cbc(aes),sha256)` with mode-specific driver names and priorities.

## Control Flow, State, And Persistence
Requests use `skcipher_walk_virt` over scatterlists and enter `scoped_ksimd` around backend SIMD/AES operations. CBC and ECB process full blocks; CTR/XCTR copy sub-block tails into aligned temporary buffers to avoid out-of-bounds access; CTS-CBC and XTS split requests when ciphertext stealing crosses scatterwalk boundaries; ESSIV derives a second AES key from `sha256(in_key)`. Persistent state is per-transform AES expanded keys.

## Dependencies And Integration
The file depends on kernel crypto skcipher internals, AES/CTR/XTS/SHA helpers, scatterwalk, SIMD context helpers, and backend symbols selected by macros. CE builds use `module_cpu_feature_match(AES, aes_init)`; NEON builds use normal `module_init`.

## Risks And Test Signals
Risks include tail handling in CTR/XCTR, CTS/XTS scatterlist splitting, IV mutation semantics, incorrect key verification, SIMD usage in invalid contexts, and registration conflicts when bit-sliced AES is enabled. Test with crypto selftests and testmgr vectors for all modes, in-place and fragmented scatterlists, non-block-size lengths for stream-like modes, invalid XTS keys, and CPU feature matrix builds.
