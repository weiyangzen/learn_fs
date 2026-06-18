# sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/Makefile

This Makefile builds the Intel Xe VFIO PCI variant. It emits `xe-vfio-pci.o` when `CONFIG_XE_VFIO_PCI` is enabled and links `main.o` into that module.

The integration point is Kbuild only. The file reflects a compact driver variant whose implementation is in `main.c` under the same directory, with VFIO PCI core selected by Kconfig. It has no runtime state or persistence behavior.

Risks are limited to build composition: the Kconfig option must select required VFIO PCI core support, and the referenced `main.o` must provide the PCI driver/module entry points. Test signals include `make M=drivers/vfio/pci/xe`, allmodconfig coverage, disabled-option builds, and module symbol/modinfo checks.
