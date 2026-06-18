# sources/distributed-fs/ceph-client/drivers/misc/rp1/Kconfig

Purpose: defines the build option for Raspberry Pi RP1 PCIe-attached peripheral controller support.

Important symbol: `MISC_RP1` is a tristate depending on `OF_IRQ` and `PCI_MSI`. Help text says the driver enables the DT node after PCIe endpoint configuration and handles interrupts for RP1 child devices.

Control flow: selecting this option builds the RP1 PCI driver and requires device-tree IRQ and MSI support.

State and persistence: build-only configuration.

Dependencies and integration points: drives `rp1/Makefile` and the PCI/OF child-device population code in `rp1_pci.c`.

Risks and test signals: build matrix should cover module and built-in forms and ensure missing MSI/OF_IRQ prevents invalid configurations.
