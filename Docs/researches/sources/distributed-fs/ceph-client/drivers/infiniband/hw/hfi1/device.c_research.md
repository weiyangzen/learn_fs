# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/device.c

Purpose: character-device class and node management for HFI1. It allocates the major range, registers kernel-only and user-accessible device classes, creates device nodes for individual minors, and cleans them up.

Important APIs/functions: `dev_init()` allocates the chrdev region and registers `hfi1` and `hfi1_user` classes. `hfi1_cdev_init()` initializes a `struct cdev`, sets its parent/name, adds it to the device number, and creates a device node in the correct class. `hfi1_cdev_cleanup()` unregisters the device and deletes the cdev. `class_name()` returns `"hfi1"` for debugfs naming.

Control flow: module init calls `dev_init()`. Per-device or per-file setup calls `hfi1_cdev_init()` with a minor, file ops, access flag, and kobject parent. Failures unwind in order: device creation failure deletes the cdev, class registration failure unregisters the range. Cleanup unregisters classes and frees the chrdev range.

State and persistence: `hfi1_dev` stores the allocated major/minor base. The `class` devnode helper gives kernel/control nodes mode `0600`; `user_class` gives user nodes mode `0666`. Created `struct device *` pointers are stored by callers and nulled during cleanup.

Dependencies and integration: depends on Linux cdev, device, and fs APIs plus HFI1 constants such as `HFI1_NMINORS` and `DRIVER_NAME`. Other driver code uses this helper to expose user and control file operations.

Risks: node permissions are security relevant: passing `user_accessible=true` creates world-readable/writable nodes. Cleanup only calls `cdev_del()` when a device pointer exists, so callers must not manually clear `*devp` before cleanup. Class registration/unregistration ordering must remain symmetric.

Test signals: module load/unload, udev-visible node modes, failed device_create injection, repeated cdev setup/cleanup, and user-open tests for the intended minors only.
