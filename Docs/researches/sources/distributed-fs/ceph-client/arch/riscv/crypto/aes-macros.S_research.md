<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-macros.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-macros.S

## Purpose
Provides shared RISC-V vector AES assembly macros for the accelerated AES mode implementations.

## Important APIs, Types, And Functions
Macros include `aes_begin`, `aes_encrypt`, `aes_decrypt`, and `aes_crypt`. They load expanded round keys from `struct crypto_aes_ctx`, select AES-128/192/256 paths, set vector type/length, and emit Zvkned AES round instructions.

## Control Flow
Callers invoke `aes_begin` to preload round keys into vector registers, branch to key-length labels, then call encrypt/decrypt macros over vector registers containing one or more blocks.

## State And Persistence
State is transient vector register contents and the caller's key pointer progression. No memory is persisted except through caller stores.

## Dependencies And Integration Points
Included by AES ECB/CBC/CTS, CTR, and XTS assembly files. Depends on RV64I, vector VLEN >= 128, Zvkned, and the generic AES key schedule layout.

## Risks And Edge Cases
The macros assume key layout and key-length storage offsets used by Linux AES. Register allocation mistakes affect every AES mode. AES-192 is explicitly supported through generic key expansion rather than Zvkned key expansion.

## Test Signals
Signals are AES crypto manager known-answer tests across 128/192/256-bit keys and all modes using these macros.

Source read size: 166 lines, 5418 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-macros.S -->
