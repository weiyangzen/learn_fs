# sources/distributed-fs/ceph-client/include/linux/uacce.h

## Purpose
Defines the kernel interface for UACCE, exposing accelerator queues to userspace through character devices, mmap regions, ioctls, PASID/SVA binding, and sysfs attributes.

## Important APIs, Types, And Functions
Key types are `struct uacce_qfile_region`, `struct uacce_ops`, `struct uacce_interface`, `enum uacce_dev_state`, `enum uacce_q_state`, `struct uacce_queue`, and `struct uacce_device`. APIs under `CONFIG_UACCE` are `uacce_alloc()`, `uacce_register()`, and `uacce_remove()`; disabled configs return `-ENODEV`/`-EINVAL` or no-op.

## Control Flow
A driver fills a `uacce_interface` and ops, allocates/registers a `uacce_device`, then userspace opens queues. Queue lifecycle flows through `get_queue`, `start_queue`, poll/update checks, mmap/ioctl operations, `stop_queue`, and `put_queue`. Device isolation state and error threshold callbacks expose reliability controls.

## State, Persistence, And Dependencies
`uacce_device` stores algorithm/API strings, queue region page counts, parent device, VF flag, flags, device id, cdev/device, mutex, private data, and queue list. `uacce_queue` stores private queue state, waitqueue, list node, qfile regions, mutex, state, PASID, SVA handle, and mapping. Dependencies include cdev and UAPI UACCE definitions.

## Integration Points
Used by accelerator drivers needing shared virtual addressing and userspace queue access, often with IOMMU SVA/PASID support.

## Risks And Test Signals
Risks include queue state-machine races, mmap region bounds, PASID/SVA lifetime leaks, isolation threshold validation, and disabled-config caller handling. Test signals include queue open/start/stop/close, mmap fault tests, ioctl compatibility, hot-unplug with active queues, waitqueue notification, and isolation sysfs behavior.
