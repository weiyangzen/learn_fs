# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_governor_attr_set.c

Purpose: implements the generic sysfs attribute-set helper for CPUFreq governor tunables. It dispatches governor attribute show/store callbacks and reference-counts shared tunable kobjects across one or more policies.

Important APIs and control flow: `governor_show()` maps an attribute to `struct governor_attr` and calls its show method with the owning `gov_attr_set`. `governor_store()` locks `attr_set->update_lock`, rejects writes once `usage_count` has reached zero, and calls the attribute store method. `gov_attr_set_init()` initializes the policy list, mutex, usage count, and first policy node. `gov_attr_set_get()` increments usage and links another policy. `gov_attr_set_put()` removes a policy, decrements usage, destroys the mutex and drops the kobject when the last user exits.

State and persistence behavior: state is embedded in each `gov_attr_set`: a policy list, update mutex, kobject, and usage count. The usage count controls whether sysfs writes are live and when the backing kobject can be released.

Dependencies and integration points: depends on `cpufreq_governor.h` definitions, sysfs `struct sysfs_ops`, kobject lifetime rules, list management, and mutexes. It is used by demand-based governors to expose shared or per-policy tunables under either the global cpufreq kobject or a policy kobject.

Risks and test signals: risks include show callbacks not checking `usage_count`, store callbacks assuming the policy list remains stable beyond the update lock, list-node misuse by callers, and kobject release ordering bugs if `gov_attr_set_put()` is not balanced. Test signals include sysfs read/write while multiple policies share a governor, hotplug removal of one policy from a shared tunable set, final policy exit freeing the kobject exactly once, and `-EBUSY` on stores after usage teardown begins.
