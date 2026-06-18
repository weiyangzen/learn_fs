## sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-neonbs-glue.c

### Purpose
Registers bit-sliced NEON AES skcipher implementations for ECB, CBC, CTR, and XTS and adapts Linux scatterlist requests to the assembly workers in `aes-neonbs-core.S`.

### Important APIs, Types, And Functions
Context types are `struct aesbs_ctx`, `struct aesbs_cbc_ctr_ctx`, and `struct aesbs_xts_ctx`. Important functions are `aesbs_setkey`, `aesbs_cbc_ctr_setkey`, `aesbs_xts_setkey`, `__ecb_crypt`, `cbc_encrypt`, `cbc_decrypt`, `ctr_encrypt`, `__xts_crypt`, `xts_encrypt`, `xts_decrypt`, `aes_init`, and `aes_exit`. Assembly entry points include `aesbs_convert_key`, `aesbs_ecb_encrypt`, `aesbs_ecb_decrypt`, `aesbs_cbc_decrypt`, `aesbs_ctr_encrypt`, and XTS/CTR variants.

### Control Flow
Setkey expands the AES key with generic helpers and converts encrypt/decrypt round keys into bit-sliced form. ECB/CBC/CTR/XTS requests walk virtual scatterlists, choose whole-block work for assembly, and handle partial CTR/XTS tails in C where necessary. CBC encryption uses the generic CBC path while CBC decrypt uses the parallel assembly path. Module init registers all skcipher algorithms through `simd_register_skciphers_compat()`.

### State, Persistence, And Dependencies
Per-transform state is round keys and round count in crypto contexts; per-request state is the skcipher walk, IV, and temporary tail buffers. There is no filesystem persistence. Dependencies include `asm/neon.h`, `asm/simd.h`, AES/CTR/XTS helpers, `crypto/internal/simd.h`, skcipher/scatterwalk APIs, and module registration.

### Integration Points
This is the public kernel crypto API surface for `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, and `xts(aes)` on ARM64 NEON. Ceph depends on these indirectly through kernel crypto users such as network, disk, and protocol authentication paths.

### Risks
Risks include incorrect fallback or tail behavior for non-block-size CTR lengths, XTS ciphertext stealing mistakes, IV persistence across scatterlist segments, invalid key length handling, and accidentally calling assembly when SIMD is unavailable.

### Test Signals
Run crypto manager selftests and `tcrypt` vectors for all registered modes, including scatterlist fragmentation, in-place encryption, odd CTR lengths, XTS data-unit sizes around 16 bytes, invalid key lengths, and module load/unload on ARM64 systems with NEON.
