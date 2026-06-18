## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_ops.c

Purpose: implements the mediated VFIO device operations for vfio-ccw. It allocates per-mdev state, exposes VFIO regions and IRQs, handles reset/open/close/read/write/ioctl, and reacts to IOMMU invalidations.

Important APIs/types/functions: `vfio_ccw_dev_ops` supplies VFIO callbacks. Main functions include `vfio_ccw_mdev_init_dev()`, `probe/remove`, `open_device/close_device`, region `read/write`, `vfio_ccw_mdev_ioctl()`, `vfio_ccw_mdev_set_irqs()`, `vfio_ccw_register_dev_region()`, `vfio_ccw_unregister_dev_regions()`, `vfio_ccw_dma_unmap()`, and request notification.

Control flow: probe allocates a `vfio_ccw_private` and registers an emulated-IOMMU VFIO device. Init allocates `guest_cp` and DMA-capable usercopy regions. Open registers async/SCHIB/CRW extra regions and sends FSM OPEN. Reads and writes decode offsets with `VFIO_CCW_OFFSET_TO_INDEX`; config-region writes copy user data under `io_mutex` and trigger the FSM I/O request. Ioctls report device/region/IRQ info, set eventfds, or reset through close/open. DMA unmap checks whether the active CP pins the invalidated IOVA and resets if necessary.

State and persistence: per-device persistent state includes VFIO eventfd contexts, allocated regions, dynamic region array, FSM state, CRW list, active CP, and work items. Dynamic regions exist only while the device is open.

Dependencies and integration: integrates mdev, VFIO core, VFIO iommufd emulated callbacks, nospec index masking, eventfd, region registration helpers, and the vfio-ccw FSM.

Risks and test signals: risks include eventfd lifetime leaks, region-index bounds, write concurrency returning `-EAGAIN`, dynamic region release ordering, and reset on DMA invalidation while I/O is active. Test VFIO GET_INFO/GET_REGION_INFO/SET_IRQS/RESET, concurrent config writes, eventfd enable/disable/signal forms, open failure unwind, and iommufd attach/detach.
