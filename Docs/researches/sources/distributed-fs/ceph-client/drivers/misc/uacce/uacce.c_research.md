# sources/distributed-fs/ceph-client/drivers/misc/uacce/uacce.c

## Purpose
`uacce.c` implements the UACCE userspace accelerator framework. It registers accelerator devices as character devices with sysfs metadata, creates per-open queues, optionally binds queues to IOMMU SVA/PASID, exposes queue control ioctls, allows queue regions to be mmaped, and handles safe device removal while file descriptors remain open.

## Important APIs, Types, and Functions
Public framework APIs are `uacce_alloc()`, `uacce_register()`, and `uacce_remove()`. File operations are `uacce_fops_open()`, `uacce_fops_release()`, `uacce_fops_unl_ioctl()`, optional `uacce_fops_compat_ioctl()`, `uacce_fops_mmap()`, and `uacce_fops_poll()`. Queue helpers include `uacce_start_queue()`, `uacce_stop_queue()`, `uacce_put_queue()`, `uacce_queue_is_valid()`, `uacce_bind_queue()`, and `uacce_unbind_queue()`. Sysfs attributes expose API version, flags, available instances, algorithms, MMIO/DUS region sizes, isolation state, and isolation threshold strategy.

## Control Flow
Subsystem init registers the UACCE class and allocates a char-device major. Accelerator drivers call `uacce_alloc()` with an interface, then `uacce_register()` to add the cdev/device. Opening a device locates it by minor in an xarray, allocates a queue, locks the UACCE device, checks that the parent still exists, binds SVA if requested, calls the driver `get_queue()` hook, initializes waitqueue/mapping/mutex, and links it into the device queue list. Ioctls start or stop queues or delegate to driver-specific ioctl handlers. Mmap validates one queue file region per type and delegates MMIO/DUS mapping to the accelerator driver. Poll waits on the queue and delegates update detection. Release stops and puts the queue, unbinds SVA, unlinks it, and frees it. Removal locks out new opens, zombifies all queues, unmaps user mappings, removes the cdev/device, clears ops/parent, erases the xarray entry, and drops the final device reference.

## State and Persistence
Global state includes `uacce_devt`, `uacce_class`, and an allocating xarray of devices. Each `struct uacce_device` has a mutex, queue list, ops, parent pointer, device ID, cdev, flags, algorithms, API string, and region page counts. Each queue has state (`INIT`, `STARTED`, `ZOMBIE`), optional SVA handle and PASID, waitqueue, mmap file mapping, and per-region mappings. State is runtime-only and tied to device and file lifetimes.

## Dependencies and Integration Points
The framework depends on char devices, device classes, sysfs groups, xarray allocation, IOMMU SVA APIs, DMA/IOMMU headers, VM operations, poll, compat ioctl support, and accelerator-driver-provided `struct uacce_ops`. It integrates with the UACCE UAPI commands `UACCE_CMD_START_Q` and `UACCE_CMD_PUT_Q`.

## Risks and Edge Cases
Lock ordering is delicate: ioctl uses the device mutex to avoid mmap-lock cycles, while mmap uses the queue mutex. Removal must handle concurrent open and live file descriptors without use-after-free; it nulls `ops` and `parent` after disabling queues. `uacce_register()` leaks the allocated cdev object on `cdev_device_add()` failure unless the caller's later cleanup handles it. Sysfs visibility depends on optional ops but `isolate_strategy` is visible if either read or write hook exists, while show/store individually require their hook.

## Test Signals
Test class/major registration, device ID allocation, open/close queue lifecycle, SVA bind failures and PASID invalid handling, start/stop ioctls, delegated ioctls, mmap duplicate-region rejection and vma close cleanup, poll readiness, sysfs visibility for optional ops, concurrent remove with open fds and mmap, xarray erasure, and module unload cleanup.
