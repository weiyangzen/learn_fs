<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/smp.h

Purpose: declares Xtensa SMP per-CPU identity, secondary CPU startup state, IPI helpers, and hotplug hooks. Important APIs/macros include `raw_smp_processor_id`, `cpu_logical_map`, `struct start_info`, `start_info`, `arch_send_call_function_ipi_mask`, `arch_send_call_function_single_ipi`, `secondary_start_kernel`, `smp_init_cpus`, `secondary_init_irq`, `ipi_init`, `show_ipi_list`, and hotplug `__cpu_die`, `__cpu_disable`, `cpu_die`, `cpu_restart`.

Control flow is implemented in `kernel/smp.c` and `head.S`/`mxhead.S`; this header is the public arch interface to generic SMP code. State includes per-thread `cpu`, secondary stack start info, CPU masks, and hotplug liveness. Dependencies include `CONFIG_SMP`, `thread_info`, cpumasks, and seq output. Integration points are scheduler, IPI broadcast, CPU bringup, interrupt display, and hotplug. Risks include wrong CPU identity before thread_info setup, stale start state, and IPI/hotplug races. Test signals include SMP boot, CPU hotplug, IPI counters in `/proc/interrupts`, reschedule/call-function IPIs, and cross-CPU TLB/cache flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/smp.h -->
