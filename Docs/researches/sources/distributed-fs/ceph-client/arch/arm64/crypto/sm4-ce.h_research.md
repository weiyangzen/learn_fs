## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce.h

### Purpose
Declares shared SM4 Crypto Extension helper functions used across SM4 CE mode glue files.

### Important APIs, Types, And Functions
Declares `sm4_ce_expand_key(const u8 *key, u32 *rkey_enc, u32 *rkey_dec, const u32 *fk, const u32 *ck)`, `sm4_ce_crypt_block(const u32 *rkey, u8 *dst, const u8 *src)`, and `sm4_ce_cbc_enc(const u32 *rkey_enc, u8 *dst, const u8 *src, u8 *iv, unsigned int nblocks)`.

### Control Flow
The header has no runtime flow; it establishes compile-time prototypes for assembly symbols defined in `sm4-ce-core.S`. Callers use these declarations after validating key sizes and entering a safe SIMD context.

### State, Persistence, And Dependencies
No local state or persistence. It depends on included type definitions from the including C file, specifically `u8` and `u32`.

### Integration Points
Included by SM4 CCM and GCM glue, and aligns their assembly declarations with the core CE implementation.

### Risks
Prototype drift is the main risk. A type or parameter order mismatch with assembly can corrupt key, IV, or output buffers at runtime without compiler visibility.

### Test Signals
Cross-build all SM4 CE glue files with `W=1`, enable CFI/linkage checks where applicable, and run all SM4 CE mode selftests after changes to this header or the assembly symbols.
