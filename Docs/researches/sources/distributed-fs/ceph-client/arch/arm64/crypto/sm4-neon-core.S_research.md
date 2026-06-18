## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-neon-core.S

### Purpose
Implements SM4 ECB-like bulk crypt, CBC decrypt, and CTR crypt using plain ARMv8 NEON table operations for systems without SM4 Crypto Extensions.

### Important APIs, Types, And Functions
Exports `sm4_neon_crypt`, `sm4_neon_cbc_dec`, and `sm4_neon_ctr_crypt`. Important macros include `SM4_PREPARE`, `transpose_4x4`, `transpose_4x4_2x`, `rotate_clockwise_4x4`, `ROUND4`, `ROUND8`, `SM4_CRYPT_BLK4`, and `SM4_CRYPT_BLK8`. The S-box is loaded into vectors v16-v31.

### Control Flow
Bulk crypt loads 8, 4, or tail blocks, transposes words for parallel S-box lookup, performs 32 SM4 rounds in groups, rotates output back, and stores blocks. CBC decrypt parallelizes decryption then XORs with IV/previous ciphertext and persists the final IV. CTR constructs counter blocks, encrypts them, XORs source data, and updates the counter buffer.

### State, Persistence, And Dependencies
No internal writable state. It mutates caller-provided output, IV, and counter buffers. Dependencies are `linux/linkage.h`, `asm/assembler.h`, NEON table instructions, generic SM4 expanded keys, and C glue providing `scoped_ksimd()`.

### Integration Points
Used by `sm4-neon-glue.c` for lower-priority `ecb(sm4)`, `cbc(sm4)`, and `ctr(sm4)` drivers on ARM64 NEON.

### Risks
Risks include S-box table indexing errors, transposition/rotation mistakes, tail paths that process 1-3 blocks through a 4-lane macro, and incorrect IV/counter persistence across scatterlist boundaries.

### Test Signals
Run SM4 ECB/CBC/CTR vectors against generic SM4, with nblocks 1 through 9, fragmented walks, in-place requests, CTR tails handled by C glue, and CPU configurations where CE drivers are absent.
