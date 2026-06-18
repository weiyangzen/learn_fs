# sources/distributed-fs/ceph-client/drivers/crypto/tegra/Makefile

Purpose: declares the NVIDIA Tegra Security Engine crypto module composition.

Important APIs and control flow: the file builds a single `tegra-se.o` module when `CONFIG_CRYPTO_DEV_TEGRA` is enabled. The module always includes `tegra-se-key.o` and `tegra-se-main.o`, with `tegra-se-aes.o` and `tegra-se-hash.o` added through `tegra-se-y`.

State and persistence behavior: no runtime state exists here; the file controls link-time inclusion of host1x/platform glue, shared keyslot management, AES/AEAD/CMAC algorithms, and SHA/HMAC algorithms.

Dependencies and integration points: depends on the Kconfig symbol `CONFIG_CRYPTO_DEV_TEGRA` from the surrounding crypto driver tree and on all four objects exporting/consuming symbols declared in `tegra-se.h`. The object grouping means AES and hash support are compiled together even though compatible data at runtime selects either AES or hash initialization per device instance.

Risks and test signals: risks include unresolved symbols if any object is omitted, overlinking unused AES/hash code into configurations that only instantiate one hardware class, and build failures if `CONFIG_CRYPTO_DEV_TEGRA` lacks host1x/crypto dependencies elsewhere. Test signals include clean module linkage, presence of all four objects in `tegra-se.o`, and successful registration on both `nvidia,tegra234-se-aes` and `nvidia,tegra234-se-hash` compatibles.
