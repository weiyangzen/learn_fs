# sources/distributed-fs/ceph-client/drivers/vfio/cdx/private.h

## Purpose

`private.h` defines the CDX VFIO driver's private data structures, region-offset encoding, BME flag, and interrupt helper prototypes or stubs.

## Important APIs, Types, and Functions

`VFIO_CDX_OFFSET_SHIFT` is 40, so VFIO region offsets encode the region index in the upper address bits. `vfio_cdx_index_to_offset()` converts a region index to VFIO offset. `struct vfio_cdx_irq` stores MSI vector metadata, eventfd trigger, and IRQ name. `struct vfio_cdx_region` stores flags, resource type, physical address, and size. `struct vfio_cdx_device` embeds `struct vfio_device`, region table, IRQ lock, IRQ array, flags, and MSI count.

## Control Flow

The header has no runtime control flow. When `CONFIG_GENERIC_MSI_IRQ` is enabled, it declares the real interrupt helpers; otherwise, it provides static stubs returning `-EINVAL` and doing no cleanup.

## State and Persistence Behavior

It defines state layout but owns none directly. The layouts persist for the lifetime of the loaded module ABI between `main.c` and `intr.c`.

## Dependencies and Integration Points

It depends on mutex definitions and, through users, CDX/VFIO/eventfd types. It is the shared contract between the CDX VFIO open/mmap/ioctl path and the optional MSI implementation.

## Risks and Edge Cases

The 40-bit offset split caps index encoding assumptions and must remain aligned with `vfio_cdx_mmap()`. Conditional interrupt stubs mean the same driver can build without MSI support but userspace `SET_IRQS` will fail.

## Test Signals

Compile both MSI and non-MSI configurations, validate offset encode/decode for several region indexes, and confirm `BME_SUPPORT` gating works with the embedded flags field.
