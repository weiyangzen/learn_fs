# sources/distributed-fs/ceph-client/drivers/virtio/Makefile

## Purpose
The virtio Makefile maps Kconfig symbols to compiled virtio core, transport, and device-driver objects.

## Important APIs, types, and functions
Important mappings include `CONFIG_VIRTIO -> virtio.o virtio_ring.o`, `CONFIG_VIRTIO_ANCHOR -> virtio_anchor.o`, `CONFIG_VIRTIO_PCI_LIB -> virtio_pci_modern_dev.o`, `CONFIG_VIRTIO_PCI_LIB_LEGACY -> virtio_pci_legacy_dev.o`, `CONFIG_VIRTIO_MMIO -> virtio_mmio.o`, `CONFIG_VIRTIO_PCI -> virtio_pci.o`, `CONFIG_VIRTIO_BALLOON -> virtio_balloon.o`, `CONFIG_VIRTIO_INPUT -> virtio_input.o`, `CONFIG_VIRTIO_VDPA -> virtio_vdpa.o`, `CONFIG_VIRTIO_MEM -> virtio_mem.o`, `CONFIG_VIRTIO_DMA_SHARED_BUFFER -> virtio_dma_buf.o`, `CONFIG_VIRTIO_DEBUG -> virtio_debug.o`, and `CONFIG_VIRTIO_RTC -> virtio_rtc.o`.

## Control flow
Kbuild evaluates the selected config values and builds objects either built-in or modular. Composite objects such as `virtio_pci-y` and `virtio_rtc-y` add feature-specific implementation files based on suboptions.

## State and persistence
Only build graph state exists. The resulting objects determine which runtime drivers and exported symbols are present.

## Dependencies and integration points
The file is synchronized with `drivers/virtio/Kconfig` and source filenames. It connects virtio bus core, rings, PCI/MMIO/vDPA transports, balloon, input, memory, dma-buf, debug, and RTC drivers to the kernel build.

## Risks and test signals
Risks include missing object mappings after Kconfig additions, stale filenames, composite object omissions, and building transport pieces without their required core. Test signals include per-symbol module and built-in builds, `make W=1`, checking module names against help text, and config combinations for PCI legacy/admin legacy and RTC subfeatures.
