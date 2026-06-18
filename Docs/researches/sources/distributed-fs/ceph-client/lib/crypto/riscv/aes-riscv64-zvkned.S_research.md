# sources/distributed-fs/ceph-client/lib/crypto/riscv/aes-riscv64-zvkned.S

## Purpose
Implements RISC-V vector AES single-block encrypt and decrypt using the Zvkned vector AES extension.

## Important APIs, Types, and Functions
Exports `aes_encrypt_zvkned` and `aes_decrypt_zvkned`. Macros `__aes_crypt_zvkned` and `aes_crypt_zvkned` wrap shared AES macro code from `../../arch/riscv/crypto/aes-macros.S` and select 128-, 192-, or 256-bit paths based on key length.

## Control Flow
Each function loads a 16-byte block into vector register `v16` with `vle32.v`, invokes `aes_begin` and `aes_crypt` from the included macro library, stores the result with `vse32.v`, and returns. Label targets `128:` and `192:` implement key-size dispatch while the fall-through path handles 256-bit keys.

## State and Persistence
Only caller-provided output is written. Vector state is used transiently inside a kernel vector region managed by the C wrapper. No globals are mutated.

## Dependencies and Integration Points
Requires RV64I, RISC-V V with VLEN at least 128, and Zvkned. Declared by `riscv/aes.h`, which performs CPU feature and SIMD gating and provides generic fallback.

## Risks
The assembly expects standard round keys, including for decryption; this differs from generic fallback decryption, which uses inverse keys. Vector length assumptions are enforced by the wrapper, so direct calls without gating would be unsafe.

## Test Signals
AES encrypt/decrypt known-answer tests for 128/192/256-bit keys under Zvkned and fallback paths. Tests should verify decryption uses normal round keys in the accelerated path.
