## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-core.S

### Purpose
Implements high-throughput ARMv8 Crypto Extension SM4 key expansion and block-mode workers for ECB-like bulk crypt, CBC, CBC-CTS, CTR, XTS, and MAC update.

### Important APIs, Types, And Functions
Exports `sm4_ce_expand_key`, `sm4_ce_crypt_block`, `sm4_ce_crypt`, `sm4_ce_cbc_enc`, `sm4_ce_cbc_dec`, `sm4_ce_cbc_cts_enc`, `sm4_ce_cbc_cts_dec`, `sm4_ce_ctr_enc`, `sm4_ce_xts_enc`, `sm4_ce_xts_dec`, and `sm4_ce_mac_update`. It uses `SM4_PREPARE` and block macros from `sm4-ce-asm.h`, plus local CTR and XTS tweak helpers.

### Control Flow
Key expansion loads FK/CK constants, produces encryption keys, and writes reversed decryption keys. Bulk crypt handles 8-, 4-, and 1-block tails. CBC encrypt chains serially; CBC decrypt parallelizes and XORs with previous ciphertext. CTS and XTS use permutation tables and overlapping loads/stores for partial final blocks. CTR constructs little-endian internal counters from big-endian buffers and persists the new counter. MAC update optionally encrypts before or after block folding.

### State, Persistence, And Dependencies
All state is caller-owned key arrays, IV/counter/tweak buffers, digest buffers, and source/destination memory. Dependencies include `sm4-ce-asm.h`, ARMv8 SM4 instructions, `asm/assembler.h`, and C glue that validates sizes and wraps SIMD use.

### Integration Points
Used by `sm4-ce-glue.c` and exported symbols used by CCM/GCM glue through `sm4-ce.h`.

### Risks
Risks include CTS overlapping memory math, XTS tweak advancement and ciphertext stealing, CTR carry/endian handling, CBC IV persistence, and keeping exported prototypes synchronized with C declarations.

### Test Signals
Run SM4 ECB/CBC/CTS/CTR/XTS/CMAC/XCBC/CBCMAC vectors, chunk sizes around 1/4/8 blocks, partial CTS/XTS lengths, in-place requests, IV/counter continuation across scatterlist segments, and cross-build/disassembly for SM4 opcodes.
