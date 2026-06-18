# sources/distributed-fs/ceph-client/arch/arm/kernel/smp.c

Purpose: implements ARM SMP operations glue: secondary CPU boot, CPU hotplug shutdown, per-CPU info, IPI routing/handling, CPU stop/panic behavior, cpufreq loop calibration updates, and NMI-style backtraces.

Important APIs/types/functions: `smp_set_ops`, `__cpu_up`, `smp_init_cpus`, `platform_can_secondary_boot`, hotplug hooks `__cpu_disable`, `arch_cpu_idle_dead`, `arch_cpuhp_cleanup_dead_cpu`, `secondary_start_kernel`, `smp_prepare_*`, IPI senders/handlers, `set_smp_ipi_range`, `smp_send_stop`, `panic_smp_self_stop`, and `arch_trigger_cpumask_backtrace`.

Control flow: boot CPU selects `smp_ops`; `__cpu_up` fills `secondary_data`, calls platform boot, and waits for `cpu_running`. Secondaries switch MMU context, initialize CPU stacks/proc state, run platform secondary init, set up IPIs, calibrate delay, publish online state, and enter idle. Hotplug disables platform CPU, migrates IRQs, flushes caches/TLBs, reports death, and calls platform die. IPI handler dispatches wakeup, timer, reschedule, call function, stop, irq_work, completion, and backtrace.

State and persistence: global `secondary_data`, `smp_ops`, `ipi_desc[]`, `ipi_irq_base`, per-CPU completions, per-CPU `cpu_data`, and cpufreq loop references.

Dependencies and integration: platform/PSCI SMP ops, scheduler, IRQ core, clock events, cpufreq, topology, MMU/TLB/cache, panic, tracepoints, and NMI backtrace.

Risks: secondary boot ordering and cache synchronization are fragile; IPIs must stay within secure-firmware usable SGIs; hotplug must not return to invalid stacks. Test signals include SMP boot, CPU hotplug, IPI statistics, panic stop, cpufreq calibration, and backtrace IPIs.
