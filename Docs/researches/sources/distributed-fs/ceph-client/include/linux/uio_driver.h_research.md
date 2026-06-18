<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uio_driver.h -->
# sources/distributed-fs/ceph-client/include/linux/uio_driver.h

Purpose: declares the Userspace I/O driver interface, allowing simple device drivers to expose memory/port regions, interrupts, and minimal callbacks through `/dev/uioX`.

Important APIs and types: `struct uio_mem` describes mappable memory regions with address, DMA address, offset, size, type, internal mapping, and DMA device. `struct uio_port` describes port I/O regions. `struct uio_device` is the core-owned runtime device with minor, event counter, async queue, waitqueue, info lock, and sysfs kobjects. `struct uio_info` is supplied by a driver and contains name/version, memory/port arrays, IRQ information, private data, IRQ handler, mmap/open/release hooks, and `irqcontrol()`. Registration APIs are `uio_register_device()`, `uio_unregister_device()`, `devm_uio_register_device()`, and `uio_event_notify()`.

Control flow: a hardware driver fills `uio_info`, registers it, optionally handles interrupts in `handler()`, and calls `uio_event_notify()` to wake/poll userspace. Userspace maps listed regions and can enable/disable IRQs through writes when `irqcontrol()` is implemented. Devm registration ties cleanup to parent device lifetime.

State and persistence: runtime state lives in `struct uio_device`: minor assignment, event count, waiters, fasync subscribers, sysfs map/port objects, and the bound `uio_info`. No persistent storage is owned.

Dependencies and integration points: integrates the device model, character device file operations, IRQ subsystem, DMA coherent memory, sysfs maps, and user drivers. Memory type constants distinguish physical, logical, virtual, IOVA, and legacy coherent DMA mappings.

Risks and test signals: risks include exporting unsafe MMIO or DMA memory to userspace, stale `uio_info` after unregister, IRQ enable races, mis-sized page-aligned mappings, and misuse of deprecated `UIO_MEM_DMA_COHERENT` in new drivers. Test registration/unregistration, mmap offsets, poll/read event counts, IRQ control, devm cleanup, and hot-unplug while userspace holds `/dev/uioX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uio_driver.h -->
