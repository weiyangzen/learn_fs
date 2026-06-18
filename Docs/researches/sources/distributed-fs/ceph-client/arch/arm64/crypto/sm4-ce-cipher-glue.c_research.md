## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-cipher-glue.c

### Purpose
Registers the ARMv8 Crypto Extension single-block SM4 cipher driver and selects assembly or generic fallback based on SIMD availability.

### Important APIs, Types, And Functions
Defines `sm4_ce_setkey`, `sm4_ce_encrypt`, `sm4_ce_decrypt`, `sm4_ce_alg`, `sm4_ce_mod_init`, and `sm4_ce_mod_fini`. It declares assembly `sm4_ce_do_crypt`.

### Control Flow
Setkey delegates to generic `sm4_expandkey()`. Encrypt/decrypt fetch the transform context and check `crypto_simd_usable()`: if false, they call generic `sm4_crypt_block()` with encrypt/decrypt keys; otherwise, they enter `scoped_ksimd()` and call the CE assembly primitive. Module init registers a `CRYPTO_ALG_TYPE_CIPHER` driver named `sm4-ce`.

### State, Persistence, And Dependencies
Transform state is `struct sm4_ctx` containing expanded encryption and decryption keys. No request queueing or persistent storage exists. Dependencies include `asm/neon.h`, `asm/simd.h`, `crypto/algapi.h`, `crypto/internal/simd.h`, `crypto/sm4.h`, CPU feature matching, and module metadata.

### Integration Points
Provides the `sm4` base cipher used by other kernel crypto modes and by direct users of the cipher API. The driver has priority 300 and aliases `sm4` and `sm4-ce`.

### Risks
The critical behavior is fallback correctness when SIMD is unavailable in interrupt/atomic contexts. A missing CPU feature gate or incorrect key schedule choice would affect all users of the base SM4 cipher.

### Test Signals
Run crypto selftests for `sm4`, force paths with SIMD usable/unusable where possible, test invalid key lengths, compare `sm4-ce` against generic SM4, and verify module register/unregister cleanup.
