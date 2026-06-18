<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/Makefile

Purpose: Maps s390 crypto Kconfig symbols to objects in the architecture crypto directory.

Important APIs/types/functions: Builds `aes_s390.o`, `paes_s390.o`, `prng.o`, `hmac_s390.o`, `phmac_s390.o`, and always builds `arch_random.o`.

Control flow: Build-time only; object inclusion follows `CONFIG_CRYPTO_AES_S390`, `CONFIG_CRYPTO_PAES_S390`, `CONFIG_S390_PRNG`, `CONFIG_CRYPTO_HMAC_S390`, and `CONFIG_CRYPTO_PHMAC_S390`.

State and persistence: No runtime state.

Dependencies and integration points: Ties Kconfig to CPACF-backed crypto drivers and the always-present arch random static-key/counter definitions.

Risks: Incorrect object mapping silently removes accelerated algorithms or links drivers into unsupported builds.

Test signals: s390 crypto config matrix builds and module autoload/alias checks for AES, PAES, HMAC, PHMAC, PRNG, and arch random support.

Source read size: 11 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/Makefile -->
