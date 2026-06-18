<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-zvksed-zvkb.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-zvksed-zvkb.S

## Purpose
Implements SM4 key expansion and single-block encryption/decryption primitives using RISC-V vector crypto instructions.

## Important APIs, Types, And Functions
Exports `sm4_expandkey_zvksed_zvkb` and `sm4_crypt_zvksed_zvkb`. It uses `vsm4k.vi` for key schedule rounds, `vsm4r.vs` for cipher rounds, `vrev8.v` for endian conversion, and `FAMILY_KEY` constants.

## Control Flow
Key expansion loads the user key, xors the SM4 family key, computes 32 round keys four at a time, stores encryption keys forward and decryption keys in reverse. Crypt loads one block, executes eight groups of four rounds, reverses endian/order, and stores output.

## State And Persistence
State is caller-provided round-key arrays and output block. Vector registers are temporary.

## Dependencies And Integration Points
Called by SM4 glue and depends on RV64I, VLEN >= 128, Zvksed, Zvkb, and Linux SM4 context layout.

## Risks And Edge Cases
Endian and reverse-key ordering are correctness-critical. The primitive processes one block; mode-level batching must happen elsewhere.

## Test Signals
Signals are SM4 encrypt/decrypt known-answer tests, setkey comparison with generic SM4, and cross-endian review of stored blocks.

Source read size: 117 lines, 3685 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/sm4-riscv64-zvksed-zvkb.S -->
