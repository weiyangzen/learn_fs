<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvbb-zvkg.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvbb-zvkg.S

## Purpose
Implements AES-XTS encrypt/decrypt using RISC-V vector AES, bitmanip, and GCM multiply support.

## Important APIs, Types, And Functions
Exports `aes_xts_encrypt_zvkned_zvbb_zvkg` and `aes_xts_decrypt_zvkned_zvbb_zvkg`. Internal macros generate tweak multiplication, byte/bit reversals, block loops, and ciphertext stealing paths.

## Control Flow
The routines load round keys with `aes_begin`, load/update the tweak, process full blocks in vector batches, multiply tweaks in GF(2^128), and handle final partial blocks with XTS ciphertext stealing.

## State And Persistence
State includes transient vector registers and the caller-provided tweak buffer, which is updated to the next tweak.

## Dependencies And Integration Points
Called by the AES glue XTS path after C prepares the initial tweak by AES-encrypting the IV. Depends on Zvkned, Zvbb, Zvkg, VLEN >= 128, and XTS crypto API semantics.

## Risks And Edge Cases
Partial-block stealing and tweak endian handling are high-risk. The C glue must ensure the last full and partial blocks are in a single walk segment.

## Test Signals
Signals are XTS known-answer tests for encrypt/decrypt, non-block-aligned lengths, in-place buffers, and fragmented scatterlists.

Source read size: 312 lines, 10728 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvbb-zvkg.S -->
