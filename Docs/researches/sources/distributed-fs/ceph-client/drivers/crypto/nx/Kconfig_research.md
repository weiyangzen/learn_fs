## sources/distributed-fs/ceph-client/drivers/crypto/nx/Kconfig

Purpose: defines configuration gates for IBM Power NX crypto and 842 compression acceleration. It separates symmetric/hash acceleration on pSeries from compression core support and platform-specific compression backends.

Important symbols: `CRYPTO_DEV_NX_ENCRYPT` builds `nx_crypto` for pSeries encryption/hash acceleration and depends on `PPC_PSERIES`, `IBMVIO`, and big-endian CPU support. It selects AES and CCM helpers. `CRYPTO_DEV_NX_COMPRESS` enables the shared 842 crypto API layer and selects the compression algorithm API plus software 842 decompression. `CRYPTO_DEV_NX_COMPRESS_PSERIES` and `CRYPTO_DEV_NX_COMPRESS_POWERNV` build the corresponding platform submit drivers, both gated by Power platform and `PPC_VAS` requirements.

Control flow and integration: this file does not execute code, but it controls which object groups the Makefile can build. Compression support is a two-level gate: the shared `nx-842.c` layer is selected by `CRYPTO_DEV_NX_COMPRESS`, while hardware access is supplied by exactly the platform modules that match the machine.

State and persistence: Kconfig choices persist in the kernel build configuration only. There is no runtime state here.

Dependencies: depends on PowerPC platform features, IBM VIO, VAS, the crypto API, AES/CCM helpers, and software 842 decompression support.

Risks: defaults are `y`, so unsupported or lightly tested platforms can compile these drivers unless dependency expressions are accurate. The encryption option explicitly excludes little-endian CPUs, while compression does not; this asymmetry is intentional only if the compression code handles endianness through BE conversions and platform APIs. Incorrect dependency changes can produce modules with unresolved symbols or runtime probe failures.

Test signals: build matrix should cover pSeries, PowerNV, big-endian and little-endian configurations, built-in and module forms, and combinations where compression core is enabled without one or both platform backends.
