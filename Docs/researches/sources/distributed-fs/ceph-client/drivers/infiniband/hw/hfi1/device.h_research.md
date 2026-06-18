# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/device.h

Purpose: public declarations for HFI1 character-device setup and cleanup.

Important APIs/types: declares `hfi1_cdev_init()`, `hfi1_cdev_cleanup()`, `class_name()`, `dev_init()`, and `dev_cleanup()`. The init helper accepts the minor number, node name, `file_operations`, cdev storage, output device pointer, user-accessible flag, and parent kobject.

Control flow: module and per-device code include this header to initialize the global device subsystem, create per-minor nodes, and tear them down on remove or error unwind.

State and persistence: no state is stored in the header. It describes ownership rules for caller-provided `struct cdev` and `struct device **`.

Dependencies and integration: relies on cdev/device types being visible from including files or previous includes. It is used by HFI1 init and debugfs naming code.

Risks: the API exposes permission choice as a boolean; wrong caller choice can expose privileged file operations. The cleanup contract requires the same `cdev` and device pointer created by `hfi1_cdev_init()`.

Test signals: compile coverage, cdev open path tests, device node permission checks, and error-unwind tests around partial initialization.
