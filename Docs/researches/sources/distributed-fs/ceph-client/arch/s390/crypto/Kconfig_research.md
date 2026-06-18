<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/Kconfig

Purpose: Declares user-visible Kconfig options for s390 CPU-accelerated crypto algorithms.

Important APIs/types/functions: Defines menu "Accelerated Cryptographic Algorithms for CPU (s390)", `config CRYPTO_AES_S390`, and `config CRYPTO_HMAC_S390`. AES selects `CRYPTO_SKCIPHER`; HMAC selects `CRYPTO_HASH`.

Control flow: Kconfig-time only. These options control whether corresponding architecture crypto modules can be built and describe the hardware generation support for AES modes and SHA2 HMAC.

State and persistence: No runtime state; selections affect build configuration and module availability.

Dependencies and integration points: Integrated with `arch/s390/crypto/Makefile` and kernel crypto API registration in `aes_s390.c` and `hmac_s390.c`. Protected-key options used by `paes_s390.c` and `phmac_s390.c` are controlled elsewhere but built in the same directory.

Risks: Missing selects can produce link/build failures or unavailable algorithms. Help text must match actual CPACF capability checks in implementation files.

Test signals: Kconfig matrix builds for built-in/module/disabled AES and HMAC, and runtime `crypto_alg` availability matching selected options and CPU support.

Source read size: 33 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/Kconfig -->
