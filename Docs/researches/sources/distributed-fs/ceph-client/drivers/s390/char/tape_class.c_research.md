# sources/distributed-fs/ceph-client/drivers/s390/char/tape_class.c

Purpose: small class-device helper for s390 tape character devices under class `tape390`.

Important APIs/types/functions: exports `register_tape_dev`, `unregister_tape_dev`, `tape_class_init`, and `tape_class_exit`; uses `struct tape_class_device` from `tape_class.h`.

Control flow: registration sanitizes device and mode names, allocates a cdev, attaches file operations, adds the cdev, creates the class device, and creates a sysfs link from the physical ccw device to the logical mode. Unregister reverses link, class device, cdev, and allocation.

State and persistence: maintains per-registered tape logical device state in `struct tape_class_device`; sysfs class device and links exist only while the tape device is online.

Dependencies and integration: used by `tape_char.c` for rewinding and non-rewinding minors; depends on Linux cdev, class, device_create, and sysfs link APIs.

Risks: error unwind must not leak cdevs or class devices; names containing `/` are rewritten to `!` to keep sysfs paths valid; callers must tolerate `ERR_PTR` results.

Test signals: online/offline tape device registration, sysfs link existence/removal, cdev open path through both modes, and failure injection in cdev_add/device_create/sysfs_create_link.
