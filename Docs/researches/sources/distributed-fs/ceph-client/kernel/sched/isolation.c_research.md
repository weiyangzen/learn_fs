# sources/distributed-fs/ceph-client/kernel/sched/isolation.c

## Purpose
Manages housekeeping CPU masks for CPU isolation. It parses `nohz_full=` and `isolcpus=` boot parameters, maintains which CPUs may run general kernel housekeeping work, and lets subsystems route work away from isolated CPUs.

## APIs, Control Flow, and State
Public helpers include `housekeeping_enabled()`, `housekeeping_cpumask()`, `housekeeping_any_cpu()`, `housekeeping_affine()`, `housekeeping_test_cpu()`, `housekeeping_update()`, and `housekeeping_init()`. The backing state is a static `struct housekeeping` containing RCU-protected cpumasks indexed by `enum hk_type` and an enabled bitmask. `housekeeping_overridden` is a static key exported for fast callers that need to skip isolation logic when no override exists.

Boot setup flows through `housekeeping_nohz_full_setup()` and `housekeeping_isolcpus_setup()`, which parse CPU lists and flags for domain isolation, managed IRQ isolation, and kernel-noise/nohz isolation. `housekeeping_setup()` builds the inverse housekeeping mask from the user-provided isolated mask, ensures at least one present housekeeping CPU remains, validates consistency between `nohz_full=` and `isolcpus=`, stores boot-time memblock cpumasks, and invokes `tick_nohz_full_setup()` for kernel-noise isolation. `housekeeping_init()` later converts memblock cpumasks to kmalloc-backed masks. `housekeeping_update()` dynamically updates the domain housekeeping mask, synchronizes RCU, and notifies PCI, memcg, vmstat, unbound workqueue, timer migration, and kthread housekeeping users.

## Dependencies and Integration Points
Depends on cpumasks, RCU, static keys, lockdep, cpusets, CPU hotplug locking, bootmem/memblock allocation, workqueues, timers, PCI, memcg, vmstat, and nohz full. It integrates with scheduler domain construction, unbound workqueue affinity, timer migration isolation, kthread placement, managed interrupts, and cgroup/cpuset partition updates.

## Risks and Test Signals
Risks include leaving no online housekeeping CPU, mismatched `nohz_full` and `isolcpus` masks, unsafe RCU cpumask replacement, lockdep coverage gaps for domain masks, stale subsystem affinity after updates, and timer/workqueue work running on isolated CPUs. Test signals include boot-parameter parsing tests, NO_HZ_FULL workloads, cpuset partition updates under hotplug, workqueue/kthread affinity inspection, timer migration tests, managed IRQ affinity checks, and lockdep/RCU testing around `housekeeping_update()`.
