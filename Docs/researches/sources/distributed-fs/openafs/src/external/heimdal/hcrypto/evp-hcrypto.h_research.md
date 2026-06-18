# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-hcrypto.h

Purpose: declares the hcrypto provider-specific EVP factories. It gives the generic EVP layer a stable set of `EVP_hcrypto_*` digest and cipher descriptors while symbol-renaming them into the `hc_` namespace to avoid OpenSSL collisions.

Important APIs/types/functions: the header exports digest factories for MD2, MD4, MD5, SHA1, SHA256, SHA384, and SHA512, plus cipher factories for RC4, RC4-40, RC2 CBC variants, DES CBC, 3DES CBC, AES CBC/CFB8 variants, and Camellia CBC variants. It relies on `EVP_MD`, `EVP_CIPHER`, and `HC_CPP_BEGIN/END` from `evp.h`.

Control flow: callers include `evp.h` first, then call a factory such as `EVP_hcrypto_aes_256_cbc()` to obtain a static descriptor consumed by `EVP_CipherInit_ex()` or `EVP_DigestInit_ex()`. This file has no executable flow of its own.

State and persistence: no runtime state is defined here. All returned descriptor storage lives in provider implementation files such as `evp-hcrypto.c`.

Dependencies and integration points: integrates generic `evp.c` selection through `EVP_DEF_OP(HCRYPTO_DEF_PROVIDER, op)` and test/validation code that explicitly calls provider factories. The symbol renames are important when this bundled Heimdal copy is built beside OpenSSL-like APIs.

Risks and test signals: declaration drift against `evp-hcrypto.c` is the main risk. Build coverage should prove every declared factory exists for the configured provider set; cipher self-tests in `test_cipher.c` and `validate.c` exercise many of these descriptors.
