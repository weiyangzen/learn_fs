# sources/distributed-fs/ceph-client/drivers/iio/trigger/iio-trig-sysfs.c

Purpose: Sysfs-controlled IIO trigger provider. Userspace creates numbered triggers and manually fires them by writing to per-trigger sysfs attributes.

Important APIs/types/functions: `struct iio_sysfs_trig` holds trigger, hard irq_work, numeric ID, and list link. Global `iio_sysfs_trig_list` is protected by `iio_sysfs_trig_list_mut`. Key functions are add/remove sysfs stores, `iio_sysfs_trigger_probe()`, `iio_sysfs_trigger_remove()`, `iio_sysfs_trigger_poll()`, and init/exit.

Control flow: module init registers a device on `iio_bus_type` with `add_trigger` and `remove_trigger`. Adding validates uniqueness, allocates `sysfstrig%d`, attaches `trigger_now`, registers it, lists it, and pins the module. Writing `trigger_now` queues hard irq_work, which calls `iio_trigger_poll()`. Removing unregisters the trigger, syncs irq_work, frees state, removes list entry, and drops the module reference.

State and persistence: in-memory list of created triggers; no persistence across module unload/reboot.

Dependencies/integration: SYSFS, IRQ_WORK, IIO bus/trigger core, and module reference counting.

Risks: trigger IDs are user-chosen and duplicate handling returns `-EINVAL`. Exit unregisters the control device but does not itself iterate remaining triggers, so userspace should remove triggers or lifetime ordering must guarantee cleanup. Manual module refcounting is critical to avoid unloading with active triggers.

Test signals: create/remove triggers through sysfs, fire `trigger_now` and observe buffer poll, test duplicate/remove-missing IDs, and unload after all triggers are removed.
