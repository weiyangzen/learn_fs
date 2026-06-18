# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_aesni_avx2_glue.c

Purpose: Registers the AVX2/AES-NI Camellia ECB and CBC skcipher implementations at higher priority than the AVX and scalar asm variants.

Important APIs/functions: declares `camellia_ecb_enc_32way`, `camellia_ecb_dec_32way`, and `camellia_cbc_dec_32way`. Uses `camellia_setkey`, `ecb_encrypt`, `ecb_decrypt`, `cbc_encrypt`, `cbc_decrypt`, and module init/exit callbacks. Registers `ecb-camellia-aesni-avx2` and `cbc-camellia-aesni-avx2` at priority 500.

Control flow: module init checks AVX, AVX2, AES, OSXSAVE, and SSE/YMM xfeatures before registering skciphers. ECB handlers process 32-way chunks, then 16-way chunks, then 2-way and scalar tails. CBC encrypt remains scalar because encryption is chaining-dependent. CBC decrypt processes 32-way, 16-way, 2-way, and scalar chunks.

State and persistence: per-transform state is `struct camellia_ctx`; no request-specific context is needed. Module state is limited to registered algorithm descriptors.

Dependencies and integration points: depends on `camellia.h`, `ecb_cbc_helpers.h`, x86 feature helpers, AVX2 assembly, AVX 16-way exported symbols, and scalar/2-way exports from `camellia_glue.c`.

Risks: feature gating must reject unsupported OS YMM state. The fallback chain spans symbols from multiple compilation units, so Kconfig/linkage changes can break tails. CBC decrypt correctness depends on helper macro walking order matching assembly assumptions about previous ciphertext.

Test signals: verify driver priority selection, 32-block and mixed-size ECB/CBC requests, all key sizes, in-place CBC decrypt, scalar tails, and module load failure on missing AVX2.
