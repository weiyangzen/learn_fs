# sources/distributed-fs/ceph-client/drivers/crypto/ti/Makefile

Purpose: declares the build composition for the TI DTHE V2 crypto driver.

Important APIs and control flow: when `CONFIG_CRYPTO_DEV_TI_DTHEV2` is enabled, the build produces `dthev2.o` from `dthev2-common.o` and `dthev2-aes.o`.

State and persistence behavior: no runtime state exists here; it controls link-time aggregation of common DTHE V2 support and AES-mode implementation code.

Dependencies and integration points: depends on the Kconfig symbol in the same directory and on the implementation objects exporting a complete module entry/registration path between common and AES files.

Risks and test signals: risks include unresolved symbols if common/AES object ownership is split incorrectly, future hash/RNG support requiring Makefile updates, and stale object names if implementation files are renamed. Test signals include clean module or built-in linkage for `CONFIG_CRYPTO_DEV_TI_DTHEV2=y/m` and modpost showing a single `dthev2` module from both objects.
