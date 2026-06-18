<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue.c

Purpose: This file registers the base x86 assembly-optimized Twofish `crypto_alg` cipher driver. It exposes single-block encrypt/decrypt wrappers for the legacy cipher API and exports the assembly symbols to higher-level modes.

Important APIs/types/functions: Assembly functions `twofish_enc_blk` and `twofish_dec_blk` are exported with `EXPORT_SYMBOL_GPL`. `twofish_encrypt()` and `twofish_decrypt()` adapt the assembly routines to `struct crypto_tfm`. `alg` registers `twofish` under driver name `twofish-asm` with priority 200 and `CRYPTO_ALG_TYPE_CIPHER`.

Control flow: Module init calls `crypto_register_alg(&alg)`. Cipher users call setkey through generic `twofish_setkey`, then single-block encrypt/decrypt through the wrapper functions. Module exit unregisters the algorithm.

State and persistence: Per-transform state is `struct twofish_ctx`. The only module-level state is the static registration descriptor. The assembly exports persist while the module is loaded.

Dependencies and integration points: It depends on generic Twofish key setup and the architecture-specific single-block assembly files. It provides fallback symbols for 3-way and AVX skcipher modules.

Risks and test signals: This is the common scalar fallback, so any bug affects all higher-level optimized variants. Tests should run Crypto API cipher vectors for all Twofish key sizes, ensure exported symbols resolve for dependent modules, and compare skcipher fallbacks against this base driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue.c -->
