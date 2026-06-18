# sources/distributed-fs/ceph-client/drivers/vfio/cdx/Makefile

## Purpose

This Makefile builds the CDX VFIO module.

## Important APIs, Types, and Functions

`obj-$(CONFIG_VFIO_CDX) += vfio-cdx.o` enables the module. `vfio-cdx-objs := main.o` is always included, and `intr.o` is added only under `CONFIG_GENERIC_MSI_IRQ`.

## Control Flow

Kbuild links `main.o` for the base VFIO CDX driver and conditionally links MSI/eventfd support. Without generic MSI IRQ support, `private.h` supplies no-op stubs.

## State and Persistence Behavior

No runtime state exists. It controls compiled object composition.

## Dependencies and Integration Points

It must match `VFIO_CDX` in Kconfig and the conditional prototypes in `private.h`.

## Risks and Edge Cases

If `intr.o` is excluded, IRQ ioctls return `-EINVAL`; that behavior is intentional but should be visible to userspace tests.

## Test Signals

Build both with and without `CONFIG_GENERIC_MSI_IRQ`, and verify symbol resolution for `vfio_cdx_set_irqs_ioctl()` and `vfio_cdx_irqs_cleanup()`.
