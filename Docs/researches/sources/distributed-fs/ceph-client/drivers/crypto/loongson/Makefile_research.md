# sources/distributed-fs/ceph-client/drivers/crypto/loongson/Makefile

Purpose: adds the Loongson RNG object to the kernel build when `CONFIG_CRYPTO_DEV_LOONGSON_RNG` is enabled.

Important declarations: `obj-$(CONFIG_CRYPTO_DEV_LOONGSON_RNG) += loongson-rng.o`.

Control flow and integration: links the platform RNG driver into the crypto drivers tree under the selected config symbol.

State and persistence: build-time only.

Risks and test signals: build tests should verify the symbol compiles as module and built-in and that no additional objects are required.
