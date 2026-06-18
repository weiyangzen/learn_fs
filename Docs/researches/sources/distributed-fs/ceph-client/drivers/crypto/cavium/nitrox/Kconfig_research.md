# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/Kconfig

Purpose: defines Kconfig symbols for Cavium/Marvell NITROX CNN55XX crypto accelerator support.

Important APIs and control flow: hidden `CRYPTO_DEV_NITROX` selects core crypto dependencies `CRYPTO_SKCIPHER`, `CRYPTO_AES`, `CRYPTO_LIB_DES`, and `FW_LOADER`. User-visible `CRYPTO_DEV_NITROX_CNN55XX` is a tristate requiring `PCI_MSI && 64BIT` and selecting the hidden symbol.

State and dependencies: Kconfig has no runtime state; it encodes assumptions used by driver PCI, MSI-X, firmware, and DMA code.

Integration points: selected symbol drives the `nitrox/Makefile` to build `n5pf`.

Risks and test signals: risks include missing explicit `PCI` dependency if inherited elsewhere is absent, and no prompt gating on actual platform family. Test signals include build visibility only with 64-bit MSI-capable configs, firmware loader availability, and crypto dependencies enabled for skcipher and AEAD algorithms.
