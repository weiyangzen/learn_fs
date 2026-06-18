# sources/distributed-fs/ceph-client/arch/x86/crypto/Kconfig

## Purpose
Kconfig menu for x86 accelerated cryptographic algorithms. It exposes selectable CPU-specific cipher and AEAD implementations and declares their architecture and crypto-core dependencies.

## Important APIs, Types, And Functions
This is configuration rather than code. Symbols include `CRYPTO_AES_NI_INTEL`, Blowfish/Camellia/CAST/Serpent/SM4/Twofish/ARIA accelerated variants, and `CRYPTO_AEGIS128_AESNI_SSE2`. Dependencies gate 64-bit-only implementations, while `select` and `imply` pull in crypto API, common cipher, mode, and library support such as `CRYPTO_AEAD`, `CRYPTO_SKCIPHER`, `CRYPTO_LIB_AES`, `CRYPTO_LIB_GF128MUL`, `CRYPTO_SM4`, and `CRYPTO_ARIA`.

## Control Flow And State
The menu determines which modules or built-in objects the Makefile can build. It does not perform CPU feature runtime checks itself; those are handled in glue modules. The help text documents expected instruction-set prerequisites and parallel block counts.

## Dependencies And Integration
Feeds `arch/x86/crypto/Makefile`, the kernel crypto API, module aliasing, and architecture feature-specific glue code. `CRYPTO_AES_NI_INTEL` enables AES-NI/VAES implementations including CTR, XCTR, XTS, and GCM assembly in this work item. `CRYPTO_AEGIS128_AESNI_SSE2` enables the AEGIS glue and assembly pair.

## Risks And Test Signals
Risks include missing `select` dependencies, enabling x86_64-only code on 32-bit builds, stale feature descriptions, and inadvertently selecting mode helpers with recursive dependency issues. Signals are Kconfig dependency checks, randconfig/allmodconfig builds, module load tests, and crypto selftests under each enabled symbol.
