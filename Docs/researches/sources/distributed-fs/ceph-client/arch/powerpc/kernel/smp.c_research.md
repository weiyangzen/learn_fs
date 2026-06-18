# sources/distributed-fs/ceph-client/arch/powerpc/kernel/smp.c

## Purpose
Implements common PowerPC SMP support: IPI dispatch, NMI-style IPIs, crash/stop IPIs, CPU bring-up and hotplug, per-CPU topology masks, big-core/thread-group parsing, scheduler topology, and secondary CPU initialization.

## Important APIs, Types, and Functions
- Global topology state includes `cpu_sibling_map`, `cpu_smallcore_map`, `cpu_l2_cache_map`, `cpu_core_map`, `cpu_coregroup_map`, `has_big_cores`, `coregroup_enabled`, and `shared_caches`.
- `struct smp_ops_t *smp_ops` is the platform integration table for probing, kicking, IPI delivery, timebase handoff, CPU setup, and CPU offline.
- IPI handlers: `call_function_action()`, `reschedule_action()`, `tick_broadcast_ipi_action()`, `nmi_ipi_action()`, `smp_request_message_ipi()`, muxed `smp_ipi_demux[_relaxed]()`, and `arch_*_ipi()` send helpers.
- NMI IPI helpers: `smp_handle_nmi_ipi()`, `smp_send_nmi_ipi()`, `smp_send_safe_nmi_ipi()`.
- CPU lifecycle: `smp_prepare_cpus()`, `smp_prepare_boot_cpu()`, `__cpu_up()`, `start_secondary()`, `__cpu_disable()`, `__cpu_die()`, `arch_cpu_idle_dead()`, and generic hotplug state helpers.
- Topology helpers: `parse_thread_groups()`, `init_thread_group_cache_map()`, `cpu_die_mask()`, `cpu_die_id()`, `cpu_to_core_id()`, `add_cpu_to_masks()`, `remove_cpu_from_masks()`, and `build_sched_topology()`.

## Control Flow and State
Early boot initializes per-CPU masks, boot CPU data, NUMA mappings, optional chip lookup tables, and platform probing. `__cpu_up()` prepares the idle thread, invokes platform preparation and kick, then waits for `cpu_callin_map` and `cpu_online()`. The secondary runs `start_secondary()`, sets up MM context, decrementer, platform CPU setup, timebase sync, NUMA state, topology masks, ftrace enablement, and then enters the CPU hotplug idle state. Hotplug disable removes a CPU from online state, migrates IRQs, drains pending interrupts, removes topology masks, and calls platform death/offline operations.

## State and Persistence Behavior
Persistent state is mostly per-CPU masks, `cpu_callin_map`, `current_set`, `secondary_current`, optional `cpu_state`, systemcfg processor count, PACA current/kstack on PPC64, and scheduler topology. The NMI IPI path uses a global atomic lock, pending mask, busy flag, and callback pointer. Muxed IPIs use per-CPU byte slots in `ipi_message.messages`.

## Dependencies and Integration Points
Integrates with `linux/smp`, scheduler domains, CPU hotplug, interrupt controllers, KVM HV, crash dump/kexec, debugger, NUMA, VDSO getcpu, time/decrementer init, ftrace, firmware/device tree CPU properties, and platform-specific `smp_ops`.

## Risks
CPU bring-up and hotplug are race-prone: incorrect barriers around `cpu_callin_map`, `secondary_current`, or PACA updates can leave CPUs stuck or using the wrong stack/current. NMI IPIs are not truly non-maskable on all platforms and timeouts can race with late handlers. Topology construction depends on firmware properties; bad thread-group/cache data can degrade scheduling or produce inconsistent masks. Crash-stop paths deliberately spin CPUs forever.

## Test Signals
Boot with SMT on/off limits, CPU hotplug loops, crash/kdump stop paths, debugger backtraces, muxed and direct IPI controllers, KVM HV active mode, pseries shared processor topology, big-core systems with `ibm,thread-groups`, NUMA CPU maps, and scheduler domain dumps.
