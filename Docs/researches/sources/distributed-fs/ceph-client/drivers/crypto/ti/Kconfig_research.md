# sources/distributed-fs/ceph-client/drivers/crypto/ti/Kconfig

Purpose: adds the TI DTHE V2 cryptography engine configuration symbol to the kernel crypto driver Kconfig tree.

Important APIs and control flow: `CRYPTO_DEV_TI_DTHEV2` is a tristate option named "Support for TI DTHE V2 cryptography engine". It is available on TI K3 platforms or compile-test builds, selects `CRYPTO_ENGINE`, `CRYPTO_SKCIPHER`, AES block modes ECB/CBC/CTR/XTS, AEAD modes GCM/CCM, and `SG_SPLIT`. The help text describes hardware cryptographic offload for TI K3 SoCs with side-channel resistance benefits.

State and persistence behavior: no runtime state exists here; selecting the symbol controls whether the TI DTHE V2 objects are compiled and whether their crypto-mode dependencies are forced on.

Dependencies and integration points: depends on `ARCH_K3 || COMPILE_TEST` and integrates with the adjacent Makefile that builds `dthev2.o`. The selected crypto helpers indicate the driver is expected to register skcipher and AEAD algorithms through the crypto engine framework and use scatterlist splitting.

Risks and test signals: risks include missing dependencies for DMA, platform, or firmware interfaces if those are required by the implementation but not expressed here, broad `select` usage forcing crypto algorithms into minimal configs, and compile-test exposing architecture assumptions. Test signals include `allyesconfig`, K3 defconfig, and `COMPILE_TEST` builds; module load on K3 SoCs; and availability of ECB/CBC/CTR/XTS/GCM/CCM algorithm registrations when enabled.
