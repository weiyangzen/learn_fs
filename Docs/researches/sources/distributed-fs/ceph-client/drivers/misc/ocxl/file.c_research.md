# sources/distributed-fs/ceph-client/drivers/misc/ocxl/file.c

## Purpose
This file provides the OCXL userspace character-device interface under `/dev/ocxl/`. It registers AFU devices, allocates minors, opens AFU contexts, dispatches ioctls, supports mmap of per-process MMIO and IRQ trigger pages, exposes event polling/reading, and cleans up contexts on release.

## Important APIs, types, and functions
Important functions are `ocxl_file_init()`, `ocxl_file_exit()`, `ocxl_file_register_afu()`, `ocxl_file_unregister_afu()`, `afu_open()`, `afu_ioctl()`, `afu_ioctl_attach()`, `afu_ioctl_get_metadata()`, `afu_ioctl_enable_p9_wait()`, `afu_ioctl_get_features()`, `afu_mmap()`, `afu_poll()`, `afu_read()`, and `afu_release()`. Device management uses `ocxl_file_info`, `minors_idr`, `ocxl_class`, `ocxl_devnode()`, and `ocxl_afu_fops`.

## Control flow and state
Module/file init reserves 256 char-device minors and registers the `ocxl` class. AFU registration allocates a minor, creates a device named from AFU name/PCI device/index, registers sysfs, adds a cdev, and stores file-info as AFU private data. Opening an AFU fd allocates an OCXL context. Ioctls attach the context, allocate/free IRQs, bind IRQs to eventfd, return metadata/features, and optionally enable POWER9 wait/TIDR support. mmap delegates to context mapping. poll/read expose XSL fault events. release detaches the context, clears mapping, wakes event waiters, and frees the context unless detach returned `-EBUSY`.

## State and persistence behavior
State is runtime only: allocated major/minors, IDR mapping, device/cdev/sysfs objects, per-open context state, eventfd IRQ handlers, and pending XSL fault records. Device nodes exist while AFUs are registered.

## Dependencies and integration points
It depends on cdev/class/device core, IDR, poll/read/ioctl/mmap file operations, eventfd, PowerPC TIDR helpers, UAPI `misc/ocxl.h`, `context.c`, `afu_irq.c`, and sysfs helpers. It is the primary userspace integration point for AFU access.

## Risks and test signals
Risks include minor IDR lifetime, device reference handling on open/unregister races, ioctl reserved-field validation, eventfd callback replacement leaks, mmap permission correctness, blocking read wakeups on close, detach timeout leaving context alive, and sysfs/cdev unregister ordering. Test signals include AFU registration/unregistration, concurrent open while unregistering, attach metadata/feature ioctls, IRQ eventfd delivery, mmap PP MMIO and IRQ pages, fault event read/poll, nonblocking read, and release during hardware errors.
