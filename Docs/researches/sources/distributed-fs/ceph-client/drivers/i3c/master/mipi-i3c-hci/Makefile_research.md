# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/Makefile

Purpose: Kbuild file for the MIPI I3C Host Controller Interface core module and optional PCI glue.

Important APIs/types/functions: `obj-$(CONFIG_MIPI_I3C_HCI) += mipi-i3c-hci.o` builds the aggregate HCI module from `core.o`, `ext_caps.o`, `pio.o`, `dma.o`, command v1/v2, DAT/DCT support, and quirks. `obj-$(CONFIG_MIPI_I3C_HCI_PCI) += mipi-i3c-hci-pci.o` builds PCI support.

Control flow: Kbuild aggregates the listed objects when the matching configs are enabled. Runtime behavior is in the HCI source files.

State and persistence: Build output is `mipi-i3c-hci` and optionally `mipi-i3c-hci-pci`, built-in or modular according to config.

Dependencies/integration: `MIPI_I3C_HCI` and `MIPI_I3C_HCI_PCI` from master Kconfig, internal HCI object decomposition, PCI glue, and MFD dependencies from Kconfig.

Risks: New HCI components must be added to the aggregate list. PCI glue requires the core HCI object. Missing object entries create link or feature gaps.

Test signals: Build core-only HCI and HCI+PCI configurations as modules and built-ins; verify aggregate object symbol resolution.
