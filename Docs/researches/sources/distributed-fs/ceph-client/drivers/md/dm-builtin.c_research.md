# sources/distributed-fs/ceph-client/drivers/md/dm-builtin.c

## Purpose
`dm-builtin.c` contains `dm_kobject_release()`, a tiny release helper compiled into the kernel rather than into the unloadable DM module. Its purpose is to avoid executing a kobject release callback from module text after the DM module has been unloaded.

## Important APIs, Types, and Functions
The only exported function is `dm_kobject_release(struct kobject *kobj)`. It calls `complete(dm_get_completion_from_kobject(kobj))` and is exported with `EXPORT_SYMBOL`.

## Control Flow
When the last external reference to a DM kobject is dropped, the kobject core invokes this release method. The helper retrieves the completion embedded or associated by DM core and completes it, allowing `dm_sysfs_exit()` or related teardown code to finish waiting for final kobject release.

## State and Persistence
The file holds no state. It participates in teardown synchronization by completing a wait object owned by DM core. There is no persistent storage behavior.

## Dependencies and Integration Points
It includes `dm-core.h` for the completion lookup helper and integrates with DM sysfs/kobject lifetime management. The key integration constraint is link placement: this helper must stay built-in so it remains executable even if the DM module is unloaded.

## Risks and Edge Cases
Moving this function into unloadable module text reintroduces the documented race where another task drops the final kobject reference, completes teardown, gets preempted before returning, and later resumes in unloaded code. The helper also assumes the incoming kobject is one of the DM kobjects understood by `dm_get_completion_from_kobject()`.

## Test Signals
Relevant signals are clean DM device removal under concurrent sysfs/kobject reference churn, successful module unload after device teardown, and absence of use-after-free or execution-from-unloaded-module reports in KASAN/KCSAN or stress tests.
