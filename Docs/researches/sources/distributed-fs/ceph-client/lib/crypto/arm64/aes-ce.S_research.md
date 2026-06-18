# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-ce.S

## Purpose
This file provides ARM64 Crypto Extension versions of AES block modes by defining AES instruction macros and including the shared `aes-modes.S` template.

## Important APIs, Types, And Functions
Through `AES_FUNC_START(func)` it emits `ce_aes_ecb_encrypt`, `ce_aes_ecb_decrypt`, CBC/CTS/CTR/XCTR/XTS/ESSIV variants, and optionally `ce_aes_mac_update`. Local macros include `load_round_keys`, `enc_prepare`, `dec_prepare`, `do_block_Nx`, `encrypt_block{,4x,5x}`, and `decrypt_block{,4x,5x}`.

## Control Flow
The file preloads round keys into vector registers and maps template block operations to ARMv8 `aese/aesmc` or `aesd/aesimc`. `aes-modes.S` then supplies the mode control flow. Multi-block paths interleave up to five blocks to improve throughput, while single-block/tail paths reuse the same macros.

## State And Persistence
There is no global mutable state. Mode functions mutate caller-provided buffers and IV/tweak state according to mode contracts.

## Dependencies And Integration Points
It requires ARMv8 crypto extensions and includes `aes-modes.S`. Symbols are declared/exported by `arm64/aes.h` for in-kernel crypto mode users.

## Risks And Edge Cases
The included template assumes macro semantics for encryption, decryption, key switching, and XTS tweak helpers. Any macro mismatch affects all modes. Calls must be gated by AES feature availability and SIMD usability.

## Test Signals
AES mode selftests for ECB, CBC, CTS, CTR, XCTR, XTS, ESSIV, and CBC-MAC on AES-capable arm64 hardware are key. Compare with `aes-neon.S` and generic fallbacks.
