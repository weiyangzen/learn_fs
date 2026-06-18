# sources/distributed-fs/ceph-client/drivers/crypto/cavium/Makefile

Purpose: selects Cavium crypto accelerator subdirectories for the kernel build.

Important APIs and control flow: `obj-$(CONFIG_CRYPTO_DEV_CPT) += cpt/` descends into the Thunder CPT PF/VF driver, and `obj-$(CONFIG_CRYPTO_DEV_NITROX) += nitrox/` descends into the CNN55XX NITROX driver. There is no runtime code or state.

Dependencies and integration points: depends on Kconfig symbols produced by child Kconfig files and the parent crypto driver build. It is the top-level integration point for Cavium accelerator objects under `drivers/crypto`.

Risks and test signals: risks are limited to symbol mismatch or stale child directory selection. Test signals are `CONFIG_CRYPTO_DEV_CPT` and `CONFIG_CRYPTO_DEV_NITROX` builds entering the correct subdirectories and disabled configurations producing no Cavium crypto objects.
