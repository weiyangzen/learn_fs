# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/evp-hcrypto.h

This kernel header declares the trimmed hcrypto EVP provider and names it with `HCRYPTO_DEF_PROVIDER hckernel`. It exposes AES-128-CBC, AES-256-CBC, and SHA1 as supported functions, and declares stubs for SHA2, MD*, RC2/RC4, DES, AES-192/CFB8, and Camellia.

There is no runtime control flow or persistence. Integration is with upstream hcrypto provider dispatch that constructs function names using `HCRYPTO_DEF_PROVIDER` and with `evp-algs.c`. Risks are header/implementation drift and callers assuming all declared algorithms are implemented. Test signals are compile/link coverage and runtime checks that unsupported algorithms are rejected cleanly.
