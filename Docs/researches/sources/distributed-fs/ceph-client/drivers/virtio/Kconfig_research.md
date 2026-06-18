# sources/distributed-fs/ceph-client/drivers/virtio/Kconfig

## Purpose
This Kconfig file defines the build configuration menu for the Linux virtio bus and many virtio transport/device drivers. It controls core virtio availability, PCI/MMIO/vDPA transports, memory, input, balloon, DMA buffer, debug, and RTC support.

## Important APIs, types, and functions
It is declarative Kconfig. Key symbols include `VIRTIO_ANCHOR`, `VIRTIO`, `VIRTIO_PCI_LIB`, `VIRTIO_PCI_LIB_LEGACY`, `VIRTIO_MENU`, `VIRTIO_HARDEN_NOTIFICATION`, `VIRTIO_PCI`, `VIRTIO_PCI_ADMIN_LEGACY`, `VIRTIO_PCI_LEGACY`, `VIRTIO_VDPA`, `VIRTIO_PMEM`, `VIRTIO_BALLOON`, `VIRTIO_MEM`, `VIRTIO_INPUT`, `VIRTIO_MMIO`, `VIRTIO_MMIO_CMDLINE_DEVICES`, `VIRTIO_DMA_SHARED_BUFFER`, `VIRTIO_DEBUG`, and `VIRTIO_RTC` with its PTP/ARM/RTC-class suboptions.

## Control flow
`VIRTIO` is selected by transports and selects `VIRTIO_ANCHOR`. The visible `VIRTIO_MENU` gates most user-facing options. Per-driver dependencies ensure required subsystems are present, such as PCI, VDPA, LIBNVDIMM, BALLOON, PAGE_REPORTING, INPUT, HAS_IOMEM/HAS_DMA, DMA_SHARED_BUFFER, PTP clocks, ARM arch timer, and RTC class.

## State and persistence
State is build-time only in `.config`; selected symbols drive Makefile object inclusion and preprocessor conditionals. There is no runtime state.

## Dependencies and integration points
This file integrates virtio with kbuild, transport subsystems, memory hotplug, input, DMA-buf, debugfs, page reporting, and timekeeping/PTP/RTC options.

## Risks and test signals
Risks are missing dependencies, stale selects, options visible on unsupported architectures, and feature combinations that compile but cannot operate. Test signals include randconfig/allmodconfig builds, minimal configs for each transport, `VIRTIO_BALLOON` with page reporting, `VIRTIO_INPUT` without INPUT rejected, RTC suboption dependency checks, and legacy PCI enable/disable combinations.
