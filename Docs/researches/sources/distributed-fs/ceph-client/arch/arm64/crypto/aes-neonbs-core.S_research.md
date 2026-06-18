## sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-neonbs-core.S

### Purpose
Implements ARM64 NEON bit-sliced AES block transforms for the kernel crypto API glue in `aes-neonbs-glue.c`. It provides constant-time AES key conversion plus ECB, CBC decrypt, CTR, and XTS encrypt/decrypt workers that process up to eight 16-byte blocks per inner call.

### Important APIs, Types, And Functions
Exports `aesbs_convert_key`, `aesbs_ecb_encrypt`, `aesbs_ecb_decrypt`, `aesbs_cbc_decrypt`, `aesbs_ctr_encrypt`, `aesbs_xts_encrypt`, and `aesbs_xts_decrypt`. Local helpers include `aesbs_encrypt8`, `aesbs_decrypt8`, `__xts_crypt8`, the bit-slice transpose macros, S-box/inverse S-box macros, round-key load macros, CTR increment, XTS tweak multiplication, and constant permutation tables `M0`, `SR`, `ISR`, and variants.

### Control Flow
Callers pass normal AES round keys, converted bit-sliced keys, block counts, IV/counter/tweak buffers, and round count. ECB loads up to eight blocks, invokes the encrypt/decrypt eight-block core, and stores only the blocks requested. CBC decrypt decrypts batches then XORs with the previous ciphertext/IV and persists the final IV. CTR builds counters, encrypts them, XORs with input, and carries partial-byte masking in the caller. XTS applies tweak whitening before and after the AES core and advances tweaks in GF(2^128).

### State, Persistence, And Dependencies
The file keeps no static writable state. Persistent effects are writes to output buffers and IV/counter/tweak buffers supplied by the C glue. It depends on `linux/linkage.h`, `linux/cfi_types.h`, `asm/assembler.h`, NEON/SIMD register conventions, and the C glue's `scoped_ksimd()` protection.

### Integration Points
The symbols are declared by `aes-neonbs-glue.c` and registered as Linux skcipher algorithms. The code relies on the generic AES key expansion and skcipher walk code to provide block-aligned chunks, tail handling, and safe SIMD entry/exit.

### Risks
The main risks are off-by-one block masks in the up-to-eight-block paths, IV/counter/tweak update mistakes across walk boundaries, endian or permutation-table drift, CFI/linkage mismatch for typed symbols, and using NEON without the caller disabling preemption or saving kernel SIMD state.

### Test Signals
Use `tcrypt`/crypto selftests for AES ECB, CBC decrypt, CTR, and XTS with 128/192/256-bit keys; compare against generic AES for chunk boundaries from 1 to 8 blocks and scatterlist splits; run KASAN/KMSAN-style tests around short tails and overlapping buffers; cross-build ARM64 with CFI enabled.
