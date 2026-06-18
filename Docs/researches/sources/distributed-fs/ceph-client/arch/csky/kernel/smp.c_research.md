# sources/distributed-fs/ceph-client/arch/csky/kernel/smp.c

Purpose: SMP CPU bring-up, IPI dispatch, cache/TLB broadcast, and hotplug integration.

Important APIs/types/functions: functions: `handle_ipi`, `set_send_ipi`, `send_ipi_message`, `arch_show_interrupts`, `arch_send_call_function_ipi_mask`, `arch_send_call_function_single_ipi`, `ipi_stop`, `smp_send_stop`, `arch_smp_send_reschedule`, `arch_irq_work_raise`, `smp_prepare_cpus`, `setup_smp_ipi`, `setup_smp`, `for_each_of_cpu_node`, `__cpu_up`, `smp_cpus_done`, `csky_start_secondary`, `__cpu_disable`; types: `ipi_message_type`, `ipi_data_struct`, `device_node`, `mm_struct`

Control flow: Runtime flow is organized around `handle_ipi`, `set_send_ipi`, `send_ipi_message`, `arch_show_interrupts`, `arch_send_call_function_ipi_mask`, `arch_send_call_function_single_ipi`, called by generic kernel subsystems through architecture hooks.

State and persistence: Maintains globals, per-CPU state, MMU/PMU registers, and CPU hotplug state; synchronization with interrupts and cross-CPU callbacks is central.

Dependencies and integration: Depends on `linux/module.h`, `linux/init.h`, `linux/kernel.h`, `linux/mm.h`, `linux/sched.h`, `linux/kernel_stat.h`, `linux/notifier.h`, `linux/cpu.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
