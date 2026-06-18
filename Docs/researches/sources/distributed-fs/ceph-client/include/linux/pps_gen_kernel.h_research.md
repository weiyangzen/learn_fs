# sources/distributed-fs/ceph-client/include/linux/pps_gen_kernel.h

Purpose: declares the kernel PPS generator API for devices that generate Pulse Per Second events.

Important APIs and types: `PPS_GEN_MAX_SOURCES` caps registered generators. `struct pps_gen_source_info` supplies whether the system clock is used, `get_time` and `enable` callbacks, plus private owner/parent device fields. `struct pps_gen_device` stores source info, enabled flag, event/sequence counters, last event, wait queue, ID, cdev, device, fasync queue, and spinlock. APIs register/unregister a source and emit generator events; `pps_gen_groups` declares sysfs attribute groups.

Control flow: a generator driver fills source info and registers it; userspace can open/control the cdev; the driver enables/disables pulse generation through callbacks and calls `pps_gen_event()` when a generator event occurs, waking waiters and async listeners.

State and persistence: runtime state includes enabled status, sequence/event counters, wait queue, async queue, cdev/device lifetime, and spinlock-protected updates. No persistent state is stored.

Dependencies and integration points: integrates with PPS generator UAPI, cdev/device core, wait queues, fasync, sysfs groups, module ownership, and optional hardware or system-clock time sources.

Risks and test signals: risks include exceeding source cap, callback owner lifetime, event sequence races, enable-state mismatch, async notification leaks, and unregister with open cdevs. Test source registration limits, enable/disable, event delivery to read/poll/fasync consumers, unregister while idle/open, and system-clock vs hardware-clock callbacks.
