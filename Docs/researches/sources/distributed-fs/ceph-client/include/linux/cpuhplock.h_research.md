<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuhplock.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuhplock.h

## Purpose

`cpuhplock.h` declares CPU hotplug locking and offlining control helpers. It gives callers read/write serialization around CPU map and hotplug state changes. The source was read as a complete 50-line file.

## Important APIs, Types, and Functions

It declares lockdep predicates `lockdep_is_cpus_held()` and `lockdep_is_cpus_write_held()`. With `CONFIG_HOTPLUG_CPU`, APIs include `cpus_write_lock()`, `cpus_write_unlock()`, `cpus_read_lock()`, `cpus_read_unlock()`, `cpus_read_trylock()`, `lockdep_assert_cpus_held()`, `cpu_hotplug_disable_offlining()`, `cpu_hotplug_disable()`, `cpu_hotplug_enable()`, `clear_tasks_mm_cpumask()`, `remove_cpu()`, `cpu_device_down()`, and `smp_shutdown_nonboot_cpus()`. Disabled builds provide no-op stubs or `-EPERM` for `remove_cpu()`. It also defines a scoped lock guard for `cpus_read_lock`.

## Control Flow

Readers take the CPU read lock before inspecting CPU masks or policy state that hotplug might change. Writers take the write lock before adding/removing CPUs or disabling hotplug. Device offline paths route through `cpu_device_down()` and `remove_cpu()`.

## State and Persistence Behavior

The actual lock and disabled/offlining counters live in implementation files. This header only declares access and a scoped cleanup helper.

## Dependencies and Integration Points

It depends on cleanup helpers and errno definitions. It integrates with CPU core, cpumask readers, cpufreq/cpuidle policy code, scheduler domains, memory-management per-task CPU masks, and system shutdown.

## Risks and Edge Cases

Missing read locks can observe transient CPU masks. Write lock misuse can deadlock hotplug callbacks. Disabled-config stubs make lock assertions no-ops, so code must still be logically correct in hotplug builds.

## Test Signals

Signals include lockdep coverage, CPU hotplug stress under cpus read/write lock users, failed `remove_cpu()` on !HOTPLUG builds, shutdown nonboot CPU paths, and scoped guard compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuhplock.h -->
