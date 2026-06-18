<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-avx.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-avx.h

Purpose: This header defines the shared C ABI for SM4 AVX and AVX2 glue code. It allows the AVX2 module to reuse common ECB, CBC encrypt, CBC decrypt, and CTR request-walking helpers from the AVX implementation.

Important APIs/types/functions: `sm4_crypt_func` is a function pointer for bulk helpers taking round keys, destination, source, and IV. Declarations include `sm4_avx_ecb_encrypt`, `sm4_avx_ecb_decrypt`, `sm4_cbc_encrypt`, `sm4_avx_cbc_decrypt`, and `sm4_avx_ctr_crypt`.

Control flow: There is no standalone execution. AVX and AVX2 glue code call these helpers with an appropriate block size and assembly function pointer for the selected vector width.

State and persistence: The header owns no state. It describes mutation of caller request buffers and IV through `struct skcipher_request`.

Dependencies and integration points: It includes Linux types and `crypto/sm4.h`. It integrates `sm4_aesni_avx_glue.c` and `sm4_aesni_avx2_glue.c`.

Risks and test signals: Function-pointer signatures must match the assembly wrappers and common C helpers. Build tests should ensure both modules link, and runtime tests should verify that AVX2 can call AVX-provided shared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/sm4-avx.h -->
