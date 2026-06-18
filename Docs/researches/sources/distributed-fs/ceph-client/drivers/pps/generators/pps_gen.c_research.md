# sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen.c

Purpose: core PPS generator character-device framework. It registers `/dev/pps-genN` devices, exposes generator sysfs groups, supports enable/time ioctls, and lets hardware drivers report generator events.

Important APIs/types/functions: exported `pps_gen_register_source()`, `pps_gen_unregister_source()`, and `pps_gen_event()`. Internal paths include `pps_gen_cdev_ioctl()`, `pps_gen_register_cdev()`, `pps_gen_unregister_cdev()`, `pps_gen_device_destruct()`, and class `pps_gen_class`.

Control flow: subsystem init registers class `pps-gen` and allocates a chrdev range. A generator driver passes `pps_gen_source_info`; the core allocates a `pps_gen_device`, initializes waitqueue and spinlock, allocates an IDA id, adds a cdev, creates `pps-genN`, and stores drvdata. Open gets a device reference. `PPS_GEN_SETENABLE` calls the driver `enable()` callback then updates `enabled`; `PPS_GEN_USESYSTEMCLOCK` returns the source flag; `PPS_GEN_FETCHEVENT` blocks until `last_ev` changes, copies sequence and event to userspace. `pps_gen_event()` updates event state, wakes waiters, and signals async readers.

State/dependencies: global devt and IDA, per-generator waitqueue/spinlock/event counters/fasync queue. Depends on cdev, device class, uaccess, poll, fasync, and generator sysfs declarations.

Risks: `poll()` always reports readable rather than checking event sequence; unregister only destroys the device and relies on release for freeing; ioctl and sysfs can both call driver enable paths; event wait snapshots `last_ev` before sleeping and can miss only if driver updates incorrectly; owner field may be unset by simple generators.

Test signals: register multiple generators up to `PPS_GEN_MAX_SOURCES`, ioctl enable/time/event paths, blocking and interrupted event fetch, fasync SIGIO, open file during unregister, and class cleanup.
