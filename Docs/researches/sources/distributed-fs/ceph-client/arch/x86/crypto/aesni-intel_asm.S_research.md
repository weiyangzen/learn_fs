# sources/distributed-fs/ceph-client/arch/x86/crypto/aesni-intel_asm.S

### Purpose
`aesni-intel_asm.S` is the baseline Intel AES-NI assembly implementation for AES key expansion and common block modes. It supports 32-bit and 64-bit x86, with x86_64-only CTR support, and supplies the low-level primitives called by `aesni-intel_glue.c` for `ecb(aes)`, `cbc(aes)`, `cts(cbc(aes))`, `ctr(aes)`, and baseline `xts(aes)`.

### Important APIs, Types, And Functions
Exported functions include `aesni_set_key()`, `aesni_enc()`, `aesni_ecb_enc()`, `aesni_ecb_dec()`, `aesni_cbc_enc()`, `aesni_cbc_dec()`, `aesni_cts_cbc_enc()`, `aesni_cts_cbc_dec()`, `aesni_ctr_enc()` on x86_64, `aesni_xts_enc()`, and `aesni_xts_dec()`. Internal helpers include `_key_expansion_128`, `_key_expansion_192a/b`, `_key_expansion_256a/b`, `_aesni_enc1`, `_aesni_enc4`, `_aesni_dec1`, `_aesni_dec4`, `_aesni_inc_init`, `_aesni_inc`, and `_aesni_gf128mul_x_ble`. The key layout stores encryption round keys at the start of `crypto_aes_ctx`, decryption round keys at a 240-byte offset, and key length at offset 480.

### Control Flow
`aesni_set_key()` expands 128/192/256-bit AES keys with `aeskeygenassist`, writes encryption round keys, then builds the inverse decryption key schedule with `aesimc` and endpoint swapping. ECB encrypt/decrypt loops process four blocks at a time when possible and one block for remainders. CBC encryption chains one block at a time through the IV, while CBC decryption parallelizes four-block decrypts and XORs with the previous ciphertext or IV. CTS-CBC helpers use a shuffle table to permute the final partial block. CTR initializes a byte-swap mask and little-endian counter, encrypts counters one or four blocks at a time, XORs with input, increments IV, and stores the updated IV. XTS encrypt/decrypt computes tweaks by multiplying by x in GF(2^128), processes four blocks where possible, and handles ciphertext stealing for partial final blocks.

### State, Persistence, And Dependencies
Persistent state is the expanded key schedule in `crypto_aes_ctx` and caller-provided IV/tweak buffers that are updated by CBC, CTR, and XTS. The assembly relies on the glue to provide valid key lengths, block-aligned lengths except for modes that explicitly handle CTS or CTR tail in C, and active kernel FPU sections. It depends on AES-NI instructions, PCL-style XMM operations, Linux frame/linkage macros, and for x86_64 CTR the ABI register mapping used by the glue.

### Integration Points
This file is the foundation for `aesni_skciphers[]` in `aesni-intel_glue.c`. The glue wraps these routines in `skcipher_walk_virt()`, handles partial CTR tails that are smaller than one AES block, validates XTS keys, aligns contexts, and registers algorithms only when `X86_FEATURE_AES` is present. The baseline XTS functions are lower priority than the newer AVX/VAES XTS functions.

### Risks
Key schedule offsets are shared implicitly with newer assembly files and the C glue. Mode functions assume the caller passes lengths they can legally process; for example ECB/CBC process only complete blocks, while glue returns leftovers to the walk. IV update behavior is part of the API and can break multi-segment requests if changed. CTS and XTS partial-block paths are shuffle-table-heavy and must preserve in-place semantics. The file uses legacy SSE encodings, so callers mixing AVX code must respect upper-register state rules in surrounding paths.

### Test Signals
Use AES ECB/CBC/CTS/CTR/XTS known-answer vectors for all key sizes, multi-block and single-block requests, CBC and CTR IV continuation over scatterwalk segments, CTS lengths 16..31 and larger, XTS partial-sector cases, in-place buffers, and comparison against generic AES software. Key expansion should be checked indirectly through both encryption and decryption vectors.
