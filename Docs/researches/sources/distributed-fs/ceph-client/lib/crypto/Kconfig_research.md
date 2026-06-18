# sources/distributed-fs/ceph-client/lib/crypto/Kconfig

## Purpose
This Kconfig file defines configuration symbols for the kernel crypto library modules and their architecture-specific acceleration toggles.

## Important APIs, Types, and Functions
Important symbols in this subset include `CRYPTO_LIB_AES`, `CRYPTO_LIB_AES_ARCH`, `CRYPTO_LIB_AESCFB`, `CRYPTO_LIB_AES_CBC_MACS`, `CRYPTO_LIB_AESGCM`, `CRYPTO_LIB_ARC4`, `CRYPTO_LIB_BLAKE2B`, `CRYPTO_LIB_BLAKE2B_ARCH`, `CRYPTO_LIB_BLAKE2S_ARCH`, `CRYPTO_LIB_CHACHA`, and `CRYPTO_LIB_CHACHA_ARCH`. It also defines related symbols for GF128, Curve25519, Poly1305, SHA, SM3, NH, and utility libraries.

## Control Flow
Kconfig selection is declarative. Library symbols select their required helper libraries, and arch-acceleration symbols default to `y` on architectures with supported code and constraints such as `!UML`, `!KMSAN`, vector crypto toolchain support, or efficient unaligned access.

## State and Persistence
Configuration choices persist in the kernel build configuration, not at runtime. They control which objects and arch headers are compiled.

## Dependencies and Integration Points
It integrates with `lib/crypto/Makefile`, generic crypto library headers, and architecture-specific acceleration files. Dependencies avoid unsupported environments such as UML/KMSAN for sensitive SIMD implementations.

## Risks and Test Signals
Risks include selecting arch code without toolchain/runtime support, missing generic fallbacks, and dependency loops. Test signals include allyesconfig/allmodconfig builds across architectures and crypto selftests under selected symbols.
