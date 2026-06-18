## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-neon-glue.c

### Purpose
Registers plain NEON SM4 skcipher drivers for ECB, CBC, and CTR and bridges skcipher walks to `sm4-neon-core.S`.

### Important APIs, Types, And Functions
Declares assembly `sm4_neon_crypt`, `sm4_neon_cbc_dec`, and `sm4_neon_ctr_crypt`. Key functions are `sm4_setkey`, `sm4_ecb_do_crypt`, `sm4_ecb_encrypt`, `sm4_ecb_decrypt`, `sm4_cbc_encrypt`, `sm4_cbc_decrypt`, `sm4_ctr_crypt`, `sm4_init`, and `sm4_exit`.

### Control Flow
Setkey delegates to generic `sm4_expandkey()`. ECB and CBC decrypt process whole blocks through NEON assembly. CBC encrypt remains generic and serial because chaining prevents useful parallelization. CTR sends whole blocks to assembly and handles final partial bytes with generic `sm4_crypt_block()`, `crypto_inc()`, and `crypto_xor_cpy()`. Module init registers three skcipher algorithms.

### State, Persistence, And Dependencies
Transform state is `struct sm4_ctx`; per-request state is skcipher walk and IV. Dependencies include skcipher internals, `crypto/internal/simd.h`, `crypto/sm4.h`, `asm/neon.h`, and `asm/simd.h`.

### Integration Points
Provides lower-priority SM4 software acceleration (`cra_priority` 200) through the kernel crypto API, acting as a fallback below Crypto Extension implementations.

### Risks
Fallback/generic CBC encrypt must stay semantically identical to assembly decrypt. Tail handling in CTR must only run on the final walk segment, and assembly must never run without kernel SIMD context.

### Test Signals
Run SM4 ECB/CBC/CTR vectors, fragmented scatterlists, partial CTR lengths, in-place operation, comparison with `sm4-ce` and generic SM4, and module load/unload tests on ARM64 NEON-only configurations.
