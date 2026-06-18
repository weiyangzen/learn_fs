# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_aesni_avx_glue.c

Purpose: Registers the 16-way AVX/AES-NI Camellia ECB and CBC skcipher backend.

Important APIs/functions: declares and exports `camellia_ecb_enc_16way`, `camellia_ecb_dec_16way`, and `camellia_cbc_dec_16way`. Implements `camellia_setkey`, ECB/CBC callbacks, and module init/exit. Registers priority-400 `ecb-camellia-aesni` and `cbc-camellia-aesni`.

Control flow: module init validates AVX, AES, OSXSAVE, and YMM xfeatures, then registers algorithms. ECB encrypt/decrypt use 16-way vector blocks, then 2-way scalar asm, then single-block asm. CBC encrypt uses scalar encryption only. CBC decrypt uses 16-way vector decrypt, then 2-way CBC helper, then scalar decrypt.

State and persistence: transform state is `struct camellia_ctx` produced by `__camellia_setkey`; no per-request scratch is allocated by the glue. Module state is only registration metadata.

Dependencies and integration points: depends on exported scalar/2-way functions from `camellia_glue.c`, vector assembly from `camellia-aesni-avx-asm_64.S`, x86 CPU feature checks, and `ecb_cbc_helpers.h`. It also exports the 16-way routines so AVX2 glue can reuse them for tails.

Risks: all vector calls depend on crypto helper/FPU handling in the broader x86 crypto framework. Exported symbol ABI must remain stable for AVX2 tail use. CBC decrypt must preserve source ciphertext for chaining when buffers overlap.

Test signals: crypto selftests should cover 16-block boundaries, all key sizes, CBC decrypt in-place, fallback to 2-way/single tails, and module rejection on CPUs lacking AES-NI or OSXSAVE.
