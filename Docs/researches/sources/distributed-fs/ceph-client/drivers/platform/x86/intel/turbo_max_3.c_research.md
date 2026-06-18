# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/turbo_max_3.c

## Purpose

This legacy Intel Turbo Boost Max Technology 3.0 driver discovers per-core favored-core priority on non-HWP Broadwell-X and Skylake-X systems and feeds the scheduler's ITMT priority mechanism.

## Important APIs, Types, And Functions

`get_oc_core_priority()` issues an overclocking mailbox favored-core read through `MSR_OC_MAILBOX`. `itmt_legacy_cpu_online()` reads each CPU's priority, calls `sched_set_itmt_core_prio()`, and schedules work to enable ITMT once distinct priorities are seen. `itmt_legacy_work_fn()` calls `sched_set_itmt_support()` outside CPU hotplug locking.

## Control Flow

`late_initcall()` matches Broadwell-X or Skylake-X and installs a dynamic CPU hotplug online callback. Each online CPU queries mailbox priority. The first time observed max priority exceeds min priority, deferred work enables scheduler ITMT support.

## State And Persistence

Static local `max_highest_perf` and `min_highest_perf` track observed priority spread. Scheduler priority state persists in scheduler data until CPU teardown or reboot. No module exit path is present because this is initcall-style built-in behavior.

## Dependencies And Integration Points

The driver depends on x86 MSR access, CPU model matching, CPU hotplug, topology/scheduler ITMT APIs, and workqueues.

## Risks

Mailbox retries are minimal; transient busy status can skip a CPU priority. Static min/max are not protected by a lock, relying on CPU hotplug serialization. No cpuhp state is removed because there is no exit. It targets only legacy non-HWP platforms.

## Test Signals

Supported CPU match, MSR mailbox success/failure logs, scheduler priority values per CPU, ITMT support enabled only after nonuniform priorities, and CPU online hotplug behavior are key signals.
