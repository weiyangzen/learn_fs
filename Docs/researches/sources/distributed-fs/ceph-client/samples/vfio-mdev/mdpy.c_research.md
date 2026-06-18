# sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy.c

## Purpose
`mdpy.c` is a sample Linux kernel mediated-device driver that exposes an emulated VFIO PCI display adapter. It creates `mdpy` mdev types for VGA, XGA, and HD framebuffer sizes and presents a simple mmap-capable display memory BAR to userspace VMMs.

## APIs, Types, And Functions
Important state is held in `struct mdev_state`: embedded `struct vfio_device`, virtual PCI config space, BAR mask, framebuffer memory, selected `mdpy_type`, and an `ops_lock`. The `mdpy_type` table defines sysfs mdev types and DRM formats. Core functions are `mdpy_create_config_space()`, `mdev_access()`, `mdpy_read()`, `mdpy_write()`, `mdpy_mmap()`, `mdpy_ioctl()`, and VFIO callbacks in `mdpy_dev_ops`. Module setup uses `alloc_chrdev_region()`, `mdev_register_driver()`, `class_register()`, `device_register()`, and `mdev_register_parent()`.

## Control Flow
Module init creates a parent device and registers mdev types. `mdpy_probe()` allocates a VFIO device and registers an emulated IOMMU-backed VFIO group device. Device init allocates config space and a `vmalloc_user()` framebuffer, initializes a gray gradient, and emits PCI config fields plus a vendor capability containing format, width, and height. VFIO read/write dispatch breaks accesses into aligned 4/2/1 byte chunks and routes them through `mdev_access()`. IOCTLs answer VFIO device, region, IRQ, reset, and graphics-plane queries.

## State And Persistence
All device state is volatile kernel memory. Config writes persist only in `vconfig`; framebuffer writes persist only until reset or device release. There is no disk persistence, migration stream, or external backing store. `ops_lock` serializes config and BAR accesses.

## Dependencies And Integration Points
The file depends on VFIO, mdev, PCI config constants, IOMMU emulation helpers, sysfs attribute groups, DRM fourcc, and local `mdpy-defs.h`. It integrates with QEMU or another VFIO consumer via VFIO PCI regions and the `VFIO_DEVICE_QUERY_GFX_PLANE` API.

## Risks And Test Signals
This is a sample driver, not hardware-backed production code. Risk areas include unchecked guest-visible semantics, small config space, no IRQ support, and simple BAR bounds handling. Useful signals are successful module load/unload, creation of mdev instances under sysfs, VFIO region queries, framebuffer mmap/read/write behavior, reset returning the gradient, and userspace display consumers correctly interpreting the graphics plane.
