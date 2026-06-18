<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx.h

Purpose: This header declares the AVX Serpent 8-way assembly ABI used by x86 Serpent glue modules.

Important APIs/types/functions: `SERPENT_PARALLEL_BLOCKS` is set to 8. The declared routines are `serpent_ecb_enc_8way_avx`, `serpent_ecb_dec_8way_avx`, and `serpent_cbc_dec_8way_avx`, each taking a cipher context, destination pointer, and source pointer. It forward-declares `struct crypto_skcipher` and includes Serpent and block operation headers.

Control flow: There is no runtime control flow in this header. C glue includes it to size walk thresholds and call the assembly entry points.

State and persistence: The header defines no storage. It describes use of caller-owned context and request buffers.

Dependencies and integration points: It depends on `crypto/serpent.h`, `crypto/b128ops.h`, and Linux integer types. It connects `serpent_avx_glue.c`, `serpent_avx2_glue.c`, and the AVX assembly implementation.

Risks and test signals: The constant must match the assembly's exact block count. A prototype mismatch would break the x86-64 calling convention at runtime. Build tests across AVX and AVX2 modules and Crypto API Serpent vectors are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-avx.h -->
