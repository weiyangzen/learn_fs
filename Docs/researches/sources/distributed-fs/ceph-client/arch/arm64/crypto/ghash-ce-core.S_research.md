## sources/distributed-fs/ceph-client/arch/arm64/crypto/ghash-ce-core.S

### Purpose
Provides PMULL-accelerated GHASH and integrated AES-GCM encryption/decryption assembly for ARMv8 Crypto Extensions.

### Important APIs, Types, And Functions
Exports `pmull_ghash_update_p64`, `pmull_gcm_encrypt`, and `pmull_gcm_decrypt`. Local helpers include `pmull_gcm_ghash_4x`, `pmull_gcm_enc_4x`, `load_round_keys`, AES round macros, PMULL reduction macros, and `.Lpermute_table` for short-block and tag comparisons.

### Control Flow
`pmull_ghash_update_p64` consumes full GHASH blocks, optionally combining a buffered head block, and stores the updated digest. `pmull_gcm_encrypt` and `pmull_gcm_decrypt` share `pmull_gcm_do_crypt`: load AES keys and GHASH powers, process four-block rounds, use special paths for 1-63 byte final chunks, hash ciphertext on encrypt or input ciphertext on decrypt, and optionally finalize with length block plus tag generation/comparison.

### State, Persistence, And Dependencies
The assembly updates caller-provided digest, counter, destination, and tag buffers only. It depends on ARM64 AES instructions, PMULL, NEON registers, `asm/assembler.h`, and C glue that supplies key schedules, GHASH tables, safe buffers for overlapping tail loads, and `scoped_ksimd()`.

### Integration Points
Used by `ghash-ce-glue.c` for `gcm(aes)` and `rfc4106(gcm(aes))`. The assembly expects AES round-count conventions from `struct aes_enckey` and GHASH reflected key tables produced by the glue.

### Risks
Short input paths intentionally use overlapping loads and may read before the first input pointer unless the caller provides a safe bounce buffer. Other risks are authsize masking errors, counter endian drift, tag compare mistakes, PMULL reduction bugs, and register-clobber ABI issues.

### Test Signals
Run AES-GCM and RFC4106 vectors with all supported tag sizes, AAD-only cases, zero-length plaintext, 1-63 byte tails, fragmented scatterlists, in-place decrypt failure paths, and KASAN guard-page tests around final chunks.
