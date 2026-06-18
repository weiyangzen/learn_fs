# sources/distributed-fs/ceph-client/drivers/vfio/cdx/intr.c

## Purpose

`intr.c` implements CDX MSI interrupt delivery for the VFIO CDX driver. It converts VFIO `VFIO_DEVICE_SET_IRQS` trigger requests into CDX MSI allocation, Linux IRQ requests, and eventfd signaling.

## Important APIs, Types, and Functions

`vfio_cdx_msi_enable()` allocates `struct vfio_cdx_irq` entries, enables MSI on the CDX device, allocates MSI domain IRQs, records virtual IRQ numbers, and stores `msi_count`. `vfio_cdx_msi_set_vector_signal()` binds or unbinds one vector to an eventfd and request_irq handler. `vfio_cdx_msi_set_block()` applies a range atomically enough to unwind previously configured entries on failure. `vfio_cdx_msi_disable()` tears down all vectors and disables MSI. The exported entry points are `vfio_cdx_set_irqs_ioctl()` and `vfio_cdx_irqs_cleanup()`.

## Control Flow

For `VFIO_IRQ_SET_DATA_EVENTFD`, the first trigger request lazily enables MSI for `cdx_dev->num_msi` vectors and then binds eventfds for the requested range. Later eventfd changes reuse the allocated vector array. A zero-count `DATA_NONE` request disables all MSI state. For `DATA_NONE` or `DATA_BOOL` trigger actions with existing vectors, the driver injects software eventfd signals rather than changing hardware configuration.

## State and Persistence Behavior

Interrupt state is held in `vdev->cdx_irqs`, per-vector `irq_no`, `trigger`, and allocated name strings, plus `vdev->msi_count`. This state lasts while the VFIO device is open or until userspace disables interrupts. Cleanup frees IRQ handlers, eventfd references, MSI domain IRQs, disables CDX MSI, frees the vector array, and resets counts.

## Dependencies and Integration Points

The file depends on the CDX bus MSI helpers (`cdx_enable_msi`, `cdx_disable_msi`), MSI domain allocation, `msi_get_virq`, Linux IRQ APIs, eventfd, and VFIO IRQ-set validation performed by `main.c`.

## Risks and Edge Cases

Range validation must avoid `start + count` overflow against `num_msi`/`msi_count`; the current code checks only normal unsigned addition. Rebinding a vector frees the previous IRQ and eventfd before acquiring the new eventfd, so a failed new bind leaves the vector disabled. `vfio_cdx_msi_disable()` calls `vfio_cdx_msi_set_block()` before testing `cdx_irqs`; with `msi_count == 0` this is harmless because count is zero.

## Test Signals

Exercise full enable, partial eventfd range bind, vector rebind, vector unbind with fd < 0, software trigger with `DATA_NONE` and `DATA_BOOL`, zero-count disable, allocation failure unwinds, IRQ handler eventfd signaling, and close-device cleanup.
