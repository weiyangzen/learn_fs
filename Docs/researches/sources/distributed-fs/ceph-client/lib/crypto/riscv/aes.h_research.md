# sources/distributed-fs/ceph-client/lib/crypto/riscv/aes.h

## Purpose
Provides RISC-V AES architecture hooks that use Zvkned vector AES when available and generic AES otherwise.

## Important APIs, Types, and Functions
Declares `aes_encrypt_zvkned` and `aes_decrypt_zvkned`. Defines `aes_preparekey_arch`, `aes_encrypt_arch`, `aes_decrypt_arch`, `aes_mod_init_arch`, and static key `have_zvkned`.

## Control Flow
Key preparation always calls `aes_expandkey_generic` and produces both normal and inverse schedules when requested. Encrypt/decrypt check `have_zvkned` and `may_use_simd()`. Accelerated calls enter `kernel_vector_begin()`, call the Zvkned assembly with normal round keys and key length, then call `kernel_vector_end()`. Fallback calls generic AES; decryption fallback uses inverse round keys.

## State and Persistence
The static branch persists whether Zvkned and sufficient vector length were detected at init. Key objects store generic-format round keys. No vector state escapes the begin/end region.

## Dependencies and Integration Points
Depends on RISC-V SIMD/vector headers, generic AES expansion and fallback routines, and the assembly file in this directory. `aes_mod_init_arch` checks `riscv_isa_extension_available(NULL, ZVKNED)` and `riscv_vector_vlen() >= 128`.

## Risks
The accelerated and fallback decrypt paths use different key schedules, so key preparation must keep both schedules available. `may_use_simd()` must be respected for contexts that cannot use vector state.

## Test Signals
AES known-answer tests with vector enabled/disabled and decryption tests that intentionally exercise both accelerated normal-round-key use and generic inverse-key fallback.
