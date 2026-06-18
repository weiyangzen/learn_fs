<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvkb.S -->
# sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvkb.S

## Purpose
Implements AES-CTR using RISC-V vector AES plus Zvkb byte/bit manipulation.

## Important APIs, Types, And Functions
Exports `aes_ctr32_crypt_zvkned_zvkb`. The macro loads the IV, builds vector counters from the low big-endian 32-bit counter word, encrypts counters, XORs keystream with input, and stores the updated IV.

## Control Flow
The loop processes as many blocks/bytes as vector length allows. C glue splits calls when the low 32-bit counter would overflow, while assembly handles a contiguous no-overflow segment.

## State And Persistence
Persistent state is the updated IV/counter buffer supplied by the caller. Other state is transient vector register data.

## Dependencies And Integration Points
Called by `riscv64_aes_ctr_crypt()` and depends on `aes-macros.S`, Zvkned, Zvkb, and crypto API CTR IV conventions.

## Risks And Edge Cases
The assembly intentionally does not handle 32-bit counter overflow; the C split logic is part of the correctness contract. Final partial blocks must XOR only requested bytes.

## Test Signals
Signals are CTR known-answer tests, arbitrary lengths including partial final blocks, and counter values near `0xffffffff`.

Source read size: 146 lines, 4805 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/crypto/aes-riscv64-zvkned-zvkb.S -->
