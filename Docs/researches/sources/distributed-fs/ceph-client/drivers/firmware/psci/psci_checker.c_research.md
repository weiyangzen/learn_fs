# sources/distributed-fs/ceph-client/drivers/firmware/psci/psci_checker.c

## Purpose
`psci_checker.c` is a late-init validation tool for PSCI CPU hotplug and suspend paths. It assumes PSCI is the active CPU enable method, then exercises CPU off/on sequences and cpuidle suspend states before userspace starts.

## Important APIs, Types, And Functions
- Global test state: `nb_available_cpus`, `tos_resident_cpu`, `nb_active_threads`, and two completions coordinating suspend test threads.
- PSCI validation: `psci_ops_check()` verifies `psci_ops.cpu_off`, `cpu_on`, and `cpu_suspend`; it also records the Trusted OS resident CPU when firmware reports a UP TOS.
- Hotplug tests: `down_and_up_cpus()`, `alloc_init_cpu_groups()`, `free_cpu_groups()`, and `hotplug_tests()`.
- Suspend tests: `suspend_cpu()`, `suspend_test_thread()`, and `suspend_tests()`.
- Entry point: `late_initcall(psci_checker)`.

## Control Flow
`psci_checker()` captures the number of online CPUs, validates PSCI operations, then first runs hotplug tests. The hotplug lane attempts to offline and online all CPUs, checks expected refusal for the last online CPU, and expects `-EPERM` when trying to offline the Trusted OS resident CPU. It repeats off/on testing by topology core groups.

The suspend lane pauses idle, creates one high-priority kthread per CPU with cpuidle support, then releases all threads through `suspend_threads_started`. Each thread loops through all cpuidle states except state 0 for ten cycles, arms a timer for wakeup, disables IRQs, invokes the cpuidle state's `enter()` callback through `suspend_cpu()`, and records successful, shallow, or failed entries. The main thread waits for all workers and then parks/stops them to collect return status.

## State And Persistence
All state is transient test state. The checker modifies live CPU topology during boot and pauses cpuidle while running suspend tests. It does not persist results outside kernel logs, but failed hotplug recovery can leave CPUs offline if firmware or the kernel cannot re-add them; the code warns if the offline mask is non-empty or the online CPU count differs from the initial count.

## Dependencies And Integration Points
The checker depends on PSCI global operations from `psci.c`, CPU hotplug (`remove_cpu()` and `add_cpu()`), cpuidle driver/device registration, topology core masks, scheduler priorities, timers, tick broadcast handling, and architecture idle hooks. It is intended for controlled validation and conflicts with concurrent hotplug/torture activity.

## Risks
The test is intrusive: it offlines CPUs and enters low-power states during late init. It assumes no other actor is using hotplug before userspace starts. It also assumes DT enable-method data is sensible on arm64 because there is no generic architecture check for PSCI usage. Missing or buggy cpuidle broadcast support can cause fallback to WFI and shallow-state counts.

## Test Signals
Kernel logs report start, per-group hotplug attempts, suspend cycles, per-CPU suspend results, and pass/error counts. Expected negative test signals are `-EBUSY` for the last online CPU and `-EPERM` for a TOS-resident CPU. Any positive error count, OOM, unavailable cpuidle devices, timeout, or CPU-count warning indicates firmware, topology, or kernel integration trouble.
