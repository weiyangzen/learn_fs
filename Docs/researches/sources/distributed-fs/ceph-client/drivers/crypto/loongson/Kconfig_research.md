# sources/distributed-fs/ceph-client/drivers/crypto/loongson/Kconfig

Purpose: declares the configuration symbol for the Loongson RNG crypto driver.

Important declarations: `CRYPTO_DEV_LOONGSON_RNG` is a tristate option named "Support for Loongson RNG Driver" and depends on `MFD_LOONGSON_SE`.

Control flow and integration: enabling this symbol allows the Makefile to build `loongson-rng.o`. The dependency ensures the Loongson Security Engine MFD layer is present before this RNG driver can be selected.

State and persistence: build configuration only; no runtime state.

Risks and test signals: Kconfig should be validated for module and built-in combinations with `MFD_LOONGSON_SE`. Missing crypto RNG dependencies are supplied by includes/registration rather than explicit selects, so build coverage is important.
