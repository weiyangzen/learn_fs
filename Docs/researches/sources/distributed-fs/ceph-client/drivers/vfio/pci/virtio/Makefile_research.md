# sources/distributed-fs/ceph-client/drivers/vfio/pci/virtio/Makefile

This Makefile builds the virtio VFIO PCI module. It emits `virtio-vfio-pci.o` when `CONFIG_VIRTIO_VFIO_PCI` is enabled, always links `main.o` and `migrate.o`, and conditionally links `legacy_io.o` when `CONFIG_VIRTIO_VFIO_PCI_ADMIN_LEGACY` is enabled.

Its integration point is purely with Kbuild. The object composition matches the Kconfig split: generic driver binding and migration are core module functionality, while legacy I/O emulation is optional. There is no runtime state in this file.

Risks are build composition issues: missing `legacy_io.o` would leave transitional ops unresolved only if the C code were not fully guarded, and missing `migrate.o` would remove migration ops referenced by `main.o`. Test signals are `make M=drivers/vfio/pci/virtio` under both legacy-enabled and legacy-disabled configs, plus module symbol checks for migration and legacy functions.
