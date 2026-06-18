## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-cc.h

Purpose: public declarations for Apple CommonCrypto-backed EVP provider functions.

Important APIs/macros: symbol-renames all `EVP_cc_*` names to `hc_EVP_cc_*`. Declares digest providers for MD2, MD4, MD5, SHA1, and SHA256; cipher providers for RC2 variants, RC4 variants, DES-CBC, 3DES-CBC, AES CBC/CFB8 variants, and Camellia CBC variants.

Control flow: none in the header; implementation may return static descriptors or `NULL` depending on platform and feature support.

State and persistence: no state declared. Provider state is allocated by the EVP core according to descriptor `ctx_size` in `evp-cc.c`.

Dependencies: assumes `EVP_MD`, `EVP_CIPHER`, and `HC_CPP_BEGIN/HC_CPP_END` are already defined by included EVP headers. Does not include them itself.

Integration points: included by `evp-cc.c` and provider-selection code that wants CommonCrypto descriptors.

Risks: declarations exist even though implementation is Apple-gated; linking or provider selection must match build conditions. Camellia declarations are present but currently implemented as `NULL` providers. Header depends on include order for EVP types/macros.

Test signals: compile tests with proper EVP include order, symbol-renaming checks, and Apple/non-Apple link configuration tests.
