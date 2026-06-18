<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/resctrl.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/resctrl.h

Purpose: supplies x86 resource-control integration for Intel/AMD cache allocation and monitoring. Important APIs/types are `resctrl_pqr_state`, per-CPU `pqr_state`, capability booleans, static keys, `resctrl_arch_enable_alloc/mon()`, `resctrl_arch_disable_alloc/mon()`, `resctrl_arch_sched_in()`, CLOSID/RMID setters/matchers, RMID index encoding, monitor context stubs, and `resctrl_cpu_detect()`.

Control flow: mount/configuration paths enable static keys; scheduler context switch calls `resctrl_arch_sched_in()`, which chooses task-specific or per-CPU default CLOSID/RMID, compares against cached MSR state, and writes `MSR_IA32_PQR_ASSOC` only when values change. Monitoring values are rounded to hardware scale.

State and persistence: per-CPU PQR state caches current/default CLOSID and RMID; task fields store assigned IDs. Resource assignments are runtime kernel state, usually managed through resctrl filesystem policy. Dependencies include MSR writes, static branches, scheduler, `task_struct` CLOSID/RMID fields, and CPU detection fields in `boot_cpu_data`.

Risks: scheduler hot-path overhead, stale cached PQR values, incorrect ID fallback, and wrong scaling for occupancy. Test signals include resctrl mount/unmount, task and CPU group assignment, context-switch MSR tracing, monitoring values, CLOSID/RMID matching, and no-op builds without `CONFIG_X86_CPU_RESCTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/resctrl.h -->
