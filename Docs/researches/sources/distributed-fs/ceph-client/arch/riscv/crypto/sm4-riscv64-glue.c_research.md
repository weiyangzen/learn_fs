<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-glue.c -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-glue.c

## Purpose
Registers a RISC-V vector-accelerated SM4 cipher implementation with generic fallback when SIMD is unavailable.

## Important APIs, Types, And Functions
Declares `sm4_expandkey_zvksed_zvkb` and `sm4_crypt_zvksed_zvkb`. Defines setkey/encrypt/decrypt wrappers and `riscv64_sm4_alg` for the crypto cipher API.

## Control Flow
Setkey uses vector expansion when `crypto_simd_usable()` and key length is valid, otherwise generic `sm4_expandkey()`. Encrypt/decrypt use vector crypt when usable, otherwise generic `sm4_crypt_block()`. Module init registers only if ZVKSED, ZVKB, and VLEN >= 128 are available.

## State And Persistence
Persistent state is `struct sm4_ctx` round keys and crypto algorithm registration. Vector state is used only inside kernel vector sections.

## Dependencies And Integration Points
Integrated with Linux crypto cipher API, generic SM4 library, RISC-V vector state management, and runtime ISA detection.

## Risks And Edge Cases
Fallback and vector key expansion must produce identical round-key ordering. Registering only single-block `sm4` means mode users rely on higher-level templates. Missing SIMD checks could use vector state in invalid contexts.

## Test Signals
Signals are SM4 known-answer tests, module load/unload, fallback operation in non-SIMD contexts, and runtime rejection on unsupported CPUs.

Source read size: 107 lines, 2848 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-glue.c -->
