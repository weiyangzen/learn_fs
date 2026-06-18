<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/rockchip/Makefile

Purpose: defines the Rockchip crypto accelerator module build.

Important build contract: `CONFIG_CRYPTO_DEV_ROCKCHIP` builds `rk_crypto.o` from `rk3288_crypto.o`, `rk3288_crypto_skcipher.o`, and `rk3288_crypto_ahash.o`.

Control flow and integration: the core platform driver, skcipher algorithms, and ahash algorithms are always linked together when the Rockchip crypto driver is enabled, matching the shared registration table in `rk3288_crypto.c`.

State and persistence: no runtime state; object composition controls which external algorithm symbols declared in `rk3288_crypto.h` must be provided.

Dependencies: Kbuild and the Rockchip crypto Kconfig symbol.

Risks and test signals: missing either algorithm object breaks the core registration externs. Build-test the driver as built-in and module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/rockchip/Makefile -->
