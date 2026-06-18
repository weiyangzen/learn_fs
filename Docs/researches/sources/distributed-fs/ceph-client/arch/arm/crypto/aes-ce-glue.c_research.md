<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-glue.c -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-glue.c

## Purpose
C CryptoAPI glue for ARMv8 Crypto Extensions AES skcipher algorithms, registering ECB, CBC, CTS-CBC, CTR, and XTS providers backed by `aes-ce-core.S`.

## Important APIs/types/functions
- Key setup: `ce_aes_expandkey()`, `ce_aes_setkey()`, `xts_set_key()`, `num_rounds()`.
- Request handlers: `ecb_encrypt/decrypt`, `cbc_encrypt/decrypt`, `cts_cbc_encrypt/decrypt`, `ctr_encrypt`, `xts_encrypt/decrypt`.
- Registered `skcipher_alg aes_algs[]` with driver names `ecb-aes-ce`, `cbc-aes-ce`, `cts-cbc-aes-ce`, `ctr-aes-ce`, and `xts-aes-ce`.
- Module feature gating: `module_cpu_feature_match(AES, aes_init)`.

## Control flow
Key expansion validates AES key sizes, builds encryption keys, then uses AES extension helpers to derive decryption keys. Each skcipher handler creates a `skcipher_walk`, enters kernel NEON around assembly calls, processes full walk segments, and returns walk residuals. CTS and XTS create subrequests when ciphertext stealing spans scatterlist boundaries. CTR handles final partial block by generating one keystream block and XOR-copying the tail.

## State and persistence behavior
Algorithm state is per-tfm in `crypto_aes_ctx` or `crypto_aes_xts_ctx`. Request state lives in `skcipher_walk`, IV buffers, scatterlist subrequests, and stack tail buffers. Module registration persists providers until `aes_exit()`.

## Dependencies and integration points
Depends on CryptoAPI skcipher internals, ARM NEON/SIMD management, CPU feature matching, AES library constants, scatterwalk helpers, XTS key verification, and assembly entry points.

## Risks and edge cases
NEON begin/end pairing is critical; this source contains duplicate `kernel_neon_begin()` calls in `xts_encrypt()` and an extra brace in `cbc_encrypt_walk()` as read, both strong compile/runtime risk signals if present in the active tree. CTS/XTS scatterlist tail handling must preserve IV/tweak state across subrequests. XTS rejects messages shorter than one block.

## Test signals
Run `crypto/testmgr` and `tcrypt` for all registered modes, including scatterlist splits, in-place operation, partial CTR tails, CTS one-block and partial-final-block cases, XTS stealing, and module load on CPUs with/without AES feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/aes-ce-glue.c -->
