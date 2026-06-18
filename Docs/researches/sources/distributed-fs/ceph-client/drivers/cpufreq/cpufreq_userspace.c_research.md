# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_userspace.c

Purpose: implements the `userspace` governor, which lets user space write an explicit target frequency through the standard `scaling_setspeed` policy attribute.

Important APIs and control flow: `cpufreq_set()` locks the governor-private mutex, rejects writes while the policy is not managed, stores the requested speed, and calls `__cpufreq_driver_target()` with relation L. `show_speed()` returns the last requested speed. Lifecycle callbacks allocate/free `struct userspace_policy`, mark management active on start with `setspeed = policy->cur`, clear it on stop, and reapply/clamp the saved target in `cpufreq_userspace_policy_limits()` when policy min/max changes.

State and persistence behavior: per-policy `userspace_policy` stores `is_managed`, `setspeed`, and a mutex. `setspeed` persists across limit callbacks while the governor is active but is reset to zero on stop and freed on exit.

Dependencies and integration points: depends on cpufreq core governor callbacks, `scaling_setspeed` dispatch in `cpufreq.c`, target-style drivers, and policy locking supplied by the core. It advertises strict-target behavior.

Risks and test signals: risks include user-requested speeds being rounded by driver/frequency-table relation semantics, writes failing during governor stop/start windows, `show_speed()` using `sprintf` rather than `sysfs_emit`, no validation before storing `setspeed` beyond target call behavior, and `BUG_ON(!policy->cur)` if started without a current frequency. Test signals include selecting userspace, reading/writing `scaling_setspeed`, clamping after min/max updates, rejection after governor stop, and correct per-policy allocation/free under hotplug.
