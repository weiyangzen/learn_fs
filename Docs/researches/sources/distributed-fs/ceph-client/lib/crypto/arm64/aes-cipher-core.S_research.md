# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-cipher-core.S

## Purpose
This ARM64 assembly file provides scalar/table-based AES single-block encrypt/decrypt routines for systems or contexts where Crypto Extensions are unavailable.

## Important APIs, Types, And Functions
It exports `__aes_arm64_encrypt` and `__aes_arm64_decrypt`. The body uses table lookup macros such as `__pair1` to read 32-bit T-table entries and combine SubBytes, ShiftRows, MixColumns, and round key operations.

## Control Flow
The routines load a plaintext/ciphertext block, map bytes through AES lookup tables round by round, xor round keys, perform the final round without MixColumns, and store the block. The implementation is straight-line/macro-expanded around the round count.

## State And Persistence
No persistent state is kept. It reads the expanded key schedule and writes the caller's output block.

## Dependencies And Integration Points
It depends on Linux linkage, assembler helpers, cache alignment definitions, and AES tables available from the surrounding build. `arm64/aes.h` uses these routines as the fallback for `aes_encrypt_arch` and `aes_decrypt_arch`.

## Risks And Edge Cases
Table-based AES can have cache side-channel considerations compared with AES instructions. It must remain a fallback for contexts without AES CE but should not be preferred when CE is available. Key schedule layout must match the CE path.

## Test Signals
AES known-answer tests with AES feature disabled, comparison with CE output for all key sizes, and side-channel policy review for table use in kernel contexts are useful signals.
