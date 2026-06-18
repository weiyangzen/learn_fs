# sources/distributed-fs/ceph-client/samples/vfio-mdev/mbochs.c

## Purpose

`mbochs.c` implements a mediated VFIO virtual PCI display device that emulates enough of QEMU/Bochs stdvga for guests such as `bochs-drm` to use a framebuffer, MMIO VBE registers, EDID region, mmap, and DMA-BUF graphics plane export.

## Important APIs, Types, and Functions

Core state is `struct mdev_state`, containing `vfio_device`, virtual config space, BAR masks, VBE registers, video-memory pages, EDID registers/blob, dmabuf list, and locks. `struct mbochs_type` defines small/medium/large mdev types; `struct mbochs_mode` describes an active framebuffer; `struct mbochs_dmabuf` tracks exported framebuffers. Major functions include `mbochs_create_config_space()`, `mbochs_check_framebuffer()`, access handlers for PCI config/MMIO/EDID/memory BAR, `mbochs_init_dev()`, `mbochs_probe()`, read/write/mmap operations, page fault handlers, DMA-BUF map/unmap/release/export helpers, VFIO region/device/ioctl handlers, and module init/exit.

## Control Flow

Module init allocates a char-device range, registers the mdev driver, class, parent device, and three mdev types. Creating an mdev allocates VFIO state and registers an emulated IOMMU VFIO device. Device init reserves memory from the atomic MB pool, allocates config/page arrays, sets EDID limits, builds PCI config space, and resets VBE registers. VFIO reads/writes dispatch by file offset to config, MMIO, EDID, or memory BAR handlers. Guest VBE writes define the framebuffer; `VFIO_DEVICE_QUERY_GFX_PLANE` validates it and creates or finds a matching dmabuf; `VFIO_DEVICE_GET_GFX_DMABUF` exports it to an fd.

## State and Persistence Behavior

Global state includes class/device/cdev/parent registration and `mbochs_avail_mbytes`. Per-mdev state persists until removal: virtual config, VBE registers, lazily allocated pages, EDID content, active plane id, and dmabuf list. Pages are allocated on access or dmabuf creation and released on close. DMA-BUF objects can outlive list unlinking until their release callback drops page references.

## Dependencies and Integration Points

It depends on VFIO, mdev, emulated IOMMU iommufd helpers, PCI constants, DMA-BUF, DRM fourcc/plane definitions, page fault/mmap APIs, sysfs attributes, and guest drivers expecting Bochs VBE behavior.

## Risks and Edge Cases

Memory accounting is global MB-based and must be balanced on init/release errors. `mdev_access()` memory BAR offset subtracts `MBOCHS_MMIO_BAR_OFFSET` rather than `MBOCHS_MEMORY_BAR_OFFSET`, which is suspicious in a sample and deserves scrutiny. Framebuffer validation only supports 32 bpp XRGB8888 and rejects small/overflowing modes. DMA-BUF export requires page-aligned offsets. Locking around dmabuf list and page references is delicate.

## Test Signals

Load the module, create each mdev type under sysfs, bind it to VFIO, query VFIO regions, boot a guest with the mdev, verify Bochs DRM detects a display, change VBE modes, query/export graphics planes, mmap BAR0, and check available memory counts before/after removal.
