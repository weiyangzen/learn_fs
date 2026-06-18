<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_irq.c -->
# sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_irq.c

## Purpose
This file implements VFIO platform interrupt setup and `VFIO_DEVICE_SET_IRQS` handling. It bridges hardware IRQs to userspace eventfds and supports mask/unmask control through direct ioctl data or virqfd eventfd triggers.

## Important APIs, types, and functions
Exported functions are `vfio_platform_irq_init`, `vfio_platform_irq_cleanup`, and `vfio_platform_set_irqs_ioctl`. Important helpers include `vfio_platform_mask`, `vfio_platform_unmask`, `vfio_set_trigger`, `vfio_automasked_irq_handler`, and `vfio_irq_handler`. Each IRQ is represented by `struct vfio_platform_irq`.

## Control flow
Initialization counts bus IRQs, allocates an IRQ array, names each IRQ, marks level-triggered IRQs as maskable and automasked, then requests each IRQ with `IRQF_NO_AUTOEN`. SET_IRQS validation is done in VFIO core and this file dispatches action type to mask, unmask, or trigger handling. Trigger setup obtains an eventfd context, enables the IRQ, and stores it as the interrupt notification target. Level-triggered interrupts are disabled in the handler before signaling userspace.

## State and persistence behavior
Runtime state includes `trigger`, `mask`, and `unmask` eventfd/virqfd pointers, `masked` boolean, IRQ name pointer or ERR_PTR request failure, and per-IRQ spinlock. Cleanup disables virqfd objects, frees IRQs, drops eventfd contexts, frees names, and clears the IRQ array.

## Dependencies and integration points
It depends on Linux IRQ APIs, eventfd, VFIO IRQ uAPI flags, and `vfio_virqfd_enable/disable`. It is called by platform common open/close and ioctl paths.

## Risks and test signals
Risks include IRQ request failure being deferred until SET_IRQS for compatibility, race-sensitive mask/unmask locking, and eventfd lifetime management. Test signals include edge and level IRQs, trigger fd enable/disable, direct trigger with DATA_NONE/DATA_BOOL, mask/unmask virqfd paths, cleanup after eventfd close, and polling fallback when `request_irq()` returns an error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vfio/platform/vfio_platform_irq.c -->
