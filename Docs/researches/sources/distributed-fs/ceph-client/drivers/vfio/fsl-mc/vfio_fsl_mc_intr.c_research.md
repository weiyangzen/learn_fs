# sources/distributed-fs/ceph-client/drivers/vfio/fsl-mc/vfio_fsl_mc_intr.c

## Purpose

`vfio_fsl_mc_intr.c` implements eventfd-backed IRQ configuration for fsl-mc VFIO devices.

## Important APIs, Types, and Functions

`vfio_fsl_mc_irqs_allocate()` allocates per-IRQ metadata and fsl-mc IRQs. `vfio_set_trigger()` binds or unbinds one MC IRQ to an eventfd and Linux IRQ handler. `vfio_fsl_mc_set_irq_trigger()` validates VFIO IRQ trigger operations, populates the parent container IRQ pool, allocates device IRQs, and handles eventfd assignment or software trigger. Public functions are `vfio_fsl_mc_set_irqs_ioctl()` and `vfio_fsl_mc_irqs_cleanup()`.

## Control Flow

`VFIO_DEVICE_SET_IRQS` arrives in the main file under `vdev->igate`. For a trigger action, this file either disables one index for zero-count `DATA_NONE`, or requires `start == 0` and `count == 1`. It populates the container IRQ pool under `dev_set->lock`, lazily allocates device IRQs, then either binds an eventfd, signals an existing eventfd, or conditionally signals based on a bool byte. Cleanup unbinds every configured IRQ, frees fsl-mc IRQs, frees the metadata array, and clears it.

## State and Persistence Behavior

State resides in `vdev->mc_irqs`; each element stores flags, count, trigger, and name. fsl-mc IRQ resources live in `mc_dev->irqs` and the parent container IRQ pool. All are transient and released on close or explicit cleanup.

## Dependencies and Integration Points

It depends on eventfd, Linux IRQ APIs, fsl-mc IRQ allocation/free, parent container IRQ-pool helpers, VFIO IRQ-set validation by the caller, and `vfio_fsl_mc_private.h`.

## Risks and Edge Cases

Index validation is mostly delegated to the caller, but `vfio_fsl_mc_set_irq_trigger()` directly indexes `mc_irqs[index]`; bad validation would be serious. If `eventfd_ctx_fdget()` fails after allocating a name, the name is freed and trigger remains unset. If `request_irq()` fails, the eventfd is dropped. The container IRQ pool is populated for each setup request and cleaned in close.

## Test Signals

Test devices with zero IRQs, lazy allocation, eventfd bind/unbind, software triggers, bool triggers, invalid start/count, IRQ-pool population failure, fsl-mc IRQ allocation failure, request_irq failure, and cleanup idempotence.
