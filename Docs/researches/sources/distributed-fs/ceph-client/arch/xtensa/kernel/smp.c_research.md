# sources/distributed-fs/ceph-client/arch/xtensa/kernel/smp.c

Purpose: Provides Xtensa SMP bring-up, CPU hotplug, IPI delivery, IPI accounting, and SMP-wide TLB/cache maintenance wrappers.

Important APIs, types, and functions: `ipi_init()`, `smp_init_cpus()`, `smp_prepare_boot_cpu()`, `secondary_start_kernel()`, `boot_secondary()`, `__cpu_up()`, hotplug methods, `ipi_interrupt()`, `show_ipi_list()`, and exported `flush_icache_range()`.

Control flow: CPU discovery reads `SYSCFGID`; secondary boot writes `start_info.stack`, unstalls the target core through `MPSCORE`, handshakes via `cpu_start_ccount` and `cpu_running`, then the secondary initializes MMU/traps/IRQ/timer and enters idle. IPIs are sent by writing CPU bitmasks to `MIPISET(msg_id)` and drained by reading/clearing `MIPICAUSE(cpu)`. Flush routines wrap local TLB/cache operations in `on_each_cpu()`.

State and persistence: Maintains possible/present/online CPU masks, per-CPU ASID caches, per-CPU IPI counters, boot handshake globals, hotplug `cpu_start_id`, and per-mm CPU masks during teardown.

Dependencies and integration: Requires `S32C1I` for SMP, MX core registers, generic CPU hotplug, scheduler IPIs, `generic_smp_call_function_interrupt`, IRQ mapping, local cache/TLB helpers, and platform secondary IRQ/timer hooks.

Risks: Boot/hotplug handshakes depend on explicit barriers and cross-CPU cache invalidation; timeouts report `-EIO` but may leave a stalled core; IPI bitmask construction assumes CPU index fits an `unsigned long`; global flushes can be expensive; stopping an IPI target calls `machine_halt()`.

Test signals: Boot all cores, online/offline cycles, call-function and reschedule IPIs, `/proc/interrupts` IPI counts, TLB/cache shootdowns under mmap stress, and failure paths for missing IPI IRQ mapping or secondary boot timeout.
