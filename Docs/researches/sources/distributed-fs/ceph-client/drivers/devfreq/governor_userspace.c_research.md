<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_userspace.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_userspace.c

Purpose: implements the `userspace` governor, allowing users to request a device frequency through a governor-specific sysfs attribute.

Important APIs and control flow: `userspace_init()` allocates `struct userspace_data`, stores it in `devfreq->governor_data`, and creates a `userspace/set_freq` sysfs group. `set_freq_store()` parses an unsigned long, records it as valid under `devfreq->lock`, and calls `update_devfreq()`. `devfreq_userspace_func()` returns the stored user frequency when valid or keeps `previous_freq` before the first write. `userspace_exit()` removes the sysfs group if the kobject is still active and frees governor data.

State and persistence behavior: per-device governor state is `user_frequency` plus a valid bit. It persists while the governor is active and is discarded on governor switch/stop.

Dependencies and integration points: depends on devfreq core, sysfs, `kstrtoul`, and device profile target callbacks. i.MX bus and i.MX8M DDRC use this governor by default.

Risks and test signals: user writes are not prevalidated against OPPs; invalid values are resolved or rejected by the core/profile target path. State is lost across governor switching. Test signals include `set_freq` showing `undefined` before writes, target update after valid writes, OPP clamping/rejection for unsupported values, sysfs group creation/removal during governor switches, and cleanup after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_userspace.c -->
