<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher.c

## Purpose
Core big.LITTLE switcher for ARM MCPM systems. It exposes a logical CPU migration mechanism that swaps a running logical CPU between paired physical CPUs in different clusters while hiding one CPU of each pair from normal scheduling.

## Important APIs/types/functions
- Exported API: `bL_switch_request_cb()`, `bL_switcher_register_notifier()`, `bL_switcher_unregister_notifier()`, `bL_switcher_trace_trigger()`, `bL_switcher_get_enabled()`, and `bL_switcher_put_enabled()`.
- Switch path: `bL_switch_to()`, `bL_switchpoint()`, and `bL_do_switch()`.
- Worker state: `struct bL_thread`, `bL_threads[]`, `bL_switcher_cpu_pairing[]`, `bL_gic_id[][]`, `bL_switcher_active`, original cluster tracking, and removed logical CPU mask.
- Sysfs under `/sys/kernel/bL_switcher`: `active` and `trace_trigger`.
- Init and CPU hotplug integration: `late_initcall(bL_switcher_init)`, `cpuhp_setup_state_nocalls()`, and `core_param(no_bL_switcher, ...)`.

## Control flow
Initialization requires MCPM availability, installs CPU hotplug veto callbacks, optionally enables the switcher, and creates sysfs. Enable flow notifies listeners, pairs online CPUs across two clusters, offlines unpaired logical CPUs, records GIC IDs, emits trace markers, and starts one FIFO switcher kthread per visible CPU. A switch request records the wanted cluster under a per-thread spinlock and wakes the worker. The worker calls `bL_switch_to()`, which powers up the inbound CPU through MCPM, gates entry vectors, migrates GIC target state, suspends local ticks, enters CPU PM, swaps `cpu_logical_map()` entries, runs `cpu_suspend()` through a stack-isolated switchpoint, resumes on the inbound CPU, and handshakes with the outbound CPU so it can power down.

## State and persistence behavior
Persistent in-kernel state is global: active flag, pairing table, original clusters, GIC IDs, per-CPU switcher threads, and removed CPU mask. Runtime synchronization uses completions, wait queues, spinlocks, mutexes, CPU hotplug locking, CPU PM callbacks, SGIs, WFE/SEV handshakes, and MCPM entry vectors. No on-disk state exists.

## Dependencies and integration points
Depends on MCPM (`asm/mcpm.h`), CPU suspend/resume, GIC migration helpers, CPU hotplug/device online-offline, clock/tick suspend, PM notifiers, power tracepoints, sysfs, kthreads, and logical MPIDR mappings. Consumers issue `bL_switch_request()` wrappers and may subscribe to activation notifications.

## Risks and edge cases
Only dual-cluster systems are supported. The switch path is fragile: interrupts/FIQs are disabled, CPU logical maps are rewritten, and a failed CPU PM entry triggers panic. CPU hotplug is vetoed for removed or unpaired CPUs while active. The source contains a duplicated `cpu_pm_enter()` call in the critical path, which is a high-risk signal for unmatched PM nesting unless intentional in this tree. Pairing logic intentionally odd-pairs CPUs, so users must not assume physical/logical adjacency. Sysfs writes can enable/disable the mechanism at runtime.

## Test signals
Boot an MCPM big.LITTLE platform, verify `/sys/kernel/bL_switcher/active`, exercise switch requests with callbacks, trace `power_cpu_migrate` events, run CPU hotplug online/offline attempts, and run suspend/resume. Build coverage requires `CONFIG_MCPM`, `CONFIG_BL_SWITCHER`, GIC, CPU suspend, and hotplug combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/bL_switcher.c -->
