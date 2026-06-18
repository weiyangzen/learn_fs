# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_priv.h

This private header defines the internal contract among VFIO PCI core implementation files. It declares capability sentinel IDs, ioeventfd limits and state, and cross-file helpers for interrupts, config virtualization, BAR/VGA I/O, power/memory locking, IGD, zPCI, and DMA-buf support.

The only concrete type defined here is `struct vfio_pci_ioeventfd`, which records a virqfd-backed MMIO/PIO write trigger: list node, owning `vfio_pci_core_device`, virqfd handle, target BAR address, write data, BAR position/index, access width, and whether memory decode must be tested. The rest of the file is prototypes plus conditional inline stubs for optional configs.

Integration is broad: `vfio_pci_core.c` calls config, IRQ, zPCI, DMA-buf, and memory helpers; `vfio_pci_config.c` calls interrupt and DMA-buf move hooks; `vfio_pci_rdwr.c` consumes the ioeventfd definition and memory helpers; optional IGD/zPCI/DMA-buf files are compiled behind config switches. The stubs preserve call sites when features are disabled, returning `-ENODEV`, `-ENOTTY`, `-EINVAL`, or no-op semantics as appropriate.

State and persistence behavior are indirect. This header standardizes ownership expectations: `memory_lock` protects BAR memory accessibility and DMA-buf revocation; `igate` protects eventfd replacement and IRQ setup; optional feature state is owned by the corresponding C files. There is no standalone persistent storage.

Risks are mostly contract drift: prototypes must match exported definitions, disabled-feature stubs must preserve caller assumptions, and helper semantics like `vfio_pci_memory_lock_and_enable()` must remain paired with restore/unlock. Test signals include allmodconfig/minimal config builds, feature-disabled builds for VGA/IGD/zPCI/DMA-buf, static analysis for lock pairing, and compile coverage for every implementation file that includes the header.
