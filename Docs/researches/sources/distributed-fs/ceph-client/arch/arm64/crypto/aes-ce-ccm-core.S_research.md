# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-ce-ccm-core.S

## Purpose
This arm64 assembly file implements the AES-CCM encrypt/decrypt transform using ARMv8 Crypto Extensions.

## APIs, Types, And Functions
It exports `ce_aes_ccm_encrypt` and `ce_aes_ccm_decrypt`, matching the C glue declarations. Internal macros include `load_round_keys`, `dround`, `aes_encrypt`, and `aes_ccm_do_crypt`. The local function `ce_aes_ccm_crypt_tail` handles partial final blocks and optional final MAC encryption.

## Control Flow, State, And Persistence
The entry points load expanded AES round keys, load the current MAC, update the counter, run AES rounds, XOR plaintext/ciphertext into the MAC, write output blocks, update the IV counter, and optionally finalize the tag with the original IV. Tail handling rewinds pointers for short blocks, uses a `.rodata` permutation table, masks plaintext/ciphertext selection, and writes back the MAC. State is entirely caller-provided buffers and SIMD registers; there is no persistent global state.

## Dependencies And Integration
The file depends on arm64 assembler support, `linux/linkage.h`, `asm/assembler.h`, and ARMv8 Crypto Extension instructions. It is linked with `aes-ce-ccm-glue.o`.

## Risks And Test Signals
Risks include counter endian mistakes, tail-block out-of-bounds accesses, incorrect final-round key cancellation, and register clobber assumptions. Test through crypto API AES-CCM vectors, partial-block cases, in-place encryption/decryption, and CPUs with AES feature support.
