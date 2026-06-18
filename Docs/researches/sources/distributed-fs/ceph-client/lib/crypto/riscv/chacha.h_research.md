# sources/distributed-fs/ceph-client/lib/crypto/riscv/chacha.h

## Purpose
Provides RISC-V ChaCha architecture hooks using Zvkb vector acceleration for full blocks and generic ChaCha fallback for unsupported or non-SIMD contexts.

## Important APIs, Types, and Functions
Declares `chacha_zvkb`, defines `chacha_crypt_arch`, `chacha_mod_init_arch`, and maps `hchacha_block_arch` to `hchacha_block_generic`. Maintains static key `use_zvkb`.

## Control Flow
`chacha_crypt_arch` computes full-block and tail-byte counts. If Zvkb is unavailable or SIMD is unusable, it calls generic ChaCha for the entire buffer. Otherwise it begins a vector region, calls `chacha_zvkb` for full blocks, then copies any tail into a 64-byte stack buffer, encrypts one block in place with `chacha_zvkb`, copies only the requested tail bytes to output, and ends the vector region.

## State and Persistence
The ChaCha state counter is updated by the assembly for full blocks and for the synthetic one-block tail. The stack tail buffer is transient but not explicitly zeroed. The static key records CPU capability after init.

## Dependencies and Integration Points
Depends on RISC-V vector/SIMD headers, `crypto_simd_usable()`, and generic ChaCha functions. Module init checks `ZVKB` and vector length at least 128.

## Risks
Tail processing encrypts a stack buffer containing copied plaintext bytes and zeros/uninitialized bytes for the rest depending on stack contents; only the requested output bytes are copied, but explicit zeroing could reduce residual data. State counter update for tail consumes a whole block, which is correct for stream position.

## Test Signals
Known-answer tests for 0, 1, 63, 64, 65, and multi-block byte counts validate full-block and tail paths. Tests should check the updated counter after tail-only calls.
