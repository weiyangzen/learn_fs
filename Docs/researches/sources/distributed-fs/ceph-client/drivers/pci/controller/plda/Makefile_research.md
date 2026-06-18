# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/Makefile

Purpose: Maps PLDA PCIe Kconfig symbols to build objects.

Important APIs/types/functions: `obj-$(CONFIG_PCIE_PLDA_HOST) += pcie-plda-host.o` builds the shared PLDA host helper. `obj-$(CONFIG_PCIE_MICROCHIP_HOST) += pcie-microchip-host.o` builds the Microchip host driver. `obj-$(CONFIG_PCIE_STARFIVE_HOST) += pcie-starfive.o` builds the StarFive host driver.

Control flow: No runtime flow. Kbuild expands these assignments based on `.config`, compiling objects built-in or into modules according to the tristate values inherited from Kconfig.

State and persistence: Build output state is controlled by generated configuration. The file itself is declarative and has no runtime state.

Dependencies/integration: Must remain consistent with `plda/Kconfig` symbols and with actual source filenames in the same directory. It participates in the parent PCI controller Makefile traversal.

Risks: A symbol/name mismatch silently drops a driver from the build or causes a missing object error. Because `PCIE_PLDA_HOST` is selected by concrete drivers, disabling or renaming the shared object breaks both Microchip and StarFive builds.

Test signals: `make drivers/pci/controller/plda/` with each relevant config, module builds for Microchip/StarFive, and allmodconfig/allyesconfig coverage.
