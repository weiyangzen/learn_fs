# sources/distributed-fs/ceph-client/drivers/crypto/cavium/cpt/Kconfig

Purpose: defines configuration symbols for the Cavium Thunder CPT cryptographic accelerator driver.

Important APIs and control flow: hidden `CRYPTO_DEV_CPT` is selected by user-visible `CAVIUM_CPT`. `CAVIUM_CPT` is a tristate prompt gated by `ARCH_THUNDER || COMPILE_TEST`, `PCI_MSI`, and `64BIT`; selecting it enables compilation of the PF/VF driver modules.

State and dependencies: Kconfig has no runtime state. It declares platform, MSI-X, and 64-bit assumptions used by the driver’s 48-bit DMA, PCI SR-IOV, and MMIO code.

Integration points: integrates with the kernel crypto hardware menu and the CPT Makefile through `CONFIG_CAVIUM_CPT`.

Risks and test signals: risks include compile-test coverage without real Thunder hardware and missing crypto algorithm selects in this Kconfig, because algorithm dependencies are pulled by source includes or parent configs. Test signals include allmodconfig/allyesconfig builds, ARCH_THUNDER builds, and disabled PCI_MSI/32-bit configs hiding the prompt.
