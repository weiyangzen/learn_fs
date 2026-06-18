<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned.S

## Purpose
Implements AES ECB, CBC, and CBC-CTS using RISC-V Zvkned vector AES instructions.

## Important APIs, Types, And Functions
Exports `aes_ecb_encrypt_zvkned`, `aes_ecb_decrypt_zvkned`, `aes_cbc_encrypt_zvkned`, `aes_cbc_decrypt_zvkned`, and `aes_cbc_cts_crypt_zvkned`. Internal macros cover ECB loops, CBC chaining, vectorized CBC decrypt, and CS3 ciphertext stealing.

## Control Flow
Each entry loads round keys with `aes_begin`, selects key length labels, then processes block-aligned input. CBC updates IV from the last ciphertext block. CTS handles single-block, block-aligned, and partial-final-block cases with special fixups.

## State And Persistence
State persisted through caller buffers includes output data and updated IV for CBC modes. Vector registers hold round keys, IVs, ciphertext, and plaintext temporarily.

## Dependencies And Integration Points
Called by AES glue skcipher handlers. Depends on `aes-macros.S`, Linux AES context layout, Zvkned, VLEN >= 128, and C glue enforcing length constraints.

## Risks And Edge Cases
CBC-CTS decrypt fixups are complex and sensitive to length and in-place overlap. ECB/CBC require nonzero block-multiple lengths, which the C walk passes to assembly.

## Test Signals
Signals are AES ECB/CBC/CTS known-answer tests for all key sizes, single-block CTS, block-aligned CTS, partial-tail CTS, and in-place encryption/decryption.

Source read size: 312 lines, 10938 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned.S -->
