# sources/distributed-fs/ceph-client/drivers/s390/char/tape_class.h

Purpose: declares the tape class-device abstraction used by the character frontend to create logical tape devices.

Important APIs/types/functions: defines `TAPECLASS_NAME_LEN`, `struct tape_class_device`, and prototypes for `register_tape_dev`, `unregister_tape_dev`, `tape_class_init`, and `tape_class_exit`.

Control flow: callers pass the physical `struct device`, target dev_t, file operations, logical device name, and mode/link name; implementation registers a cdev and class device and returns a handle for cleanup.

State and persistence: the structure stores cdev pointer, class device pointer, and fixed-size copied names. State is runtime-only and owned by online tape devices.

Dependencies and integration: included by tape core/char frontend; depends on Linux fs, cdev, device, kdev_t, module/init headers.

Risks: fixed name buffers require bounded copies; caller must not pass stack-owned data expecting later reference because names are copied; cleanup must receive the same physical parent used to create sysfs links.

Test signals: compile compatibility with `tape_class.c`, class init/exit order during tape module load/unload, and cleanup of both rewinding and non-rewinding device handles.
