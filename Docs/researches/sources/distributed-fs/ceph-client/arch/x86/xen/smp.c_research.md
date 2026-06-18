<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/smp.c

## Purpose
Provides Xen-common x86 SMP interrupt and IPI plumbing shared by PV and HVM guests. It binds Xen event-channel IPIs for reschedule and function-call vectors, optionally binds debug VIRQ, maps native x86 vectors to Xen synthetic vectors, and implements the SMP send hooks used by `smp_ops`.

## Important APIs, Types, And Functions
Per-CPU IRQ holders are `xen_resched_irq`, `xen_callfunc_irq`, `xen_callfuncsingle_irq`, and `xen_debug_irq`. Public hooks are `xen_smp_intr_init`, `xen_smp_intr_free`, `xen_smp_cpus_done`, `xen_smp_send_reschedule`, `xen_smp_send_call_function_ipi`, `xen_smp_send_call_function_single_ipi`, `xen_send_IPI_mask`, `xen_send_IPI_all`, `xen_send_IPI_self`, `xen_send_IPI_mask_allbutself`, and `xen_send_IPI_allbutself`.

## Control Flow
CPU bringup calls `xen_smp_intr_init`, which allocates names and binds per-CPU Xen IPI handlers for reschedule, call-function, and single-call-function vectors; non-FIFO event mode also binds `VIRQ_DEBUG`. IPI send helpers translate APIC vectors through `xen_map_vector` and iterate online CPUs with `xen_send_IPI_one`. Function-call IPIs yield to Xen if a target vCPU is stolen so the target can run promptly.

## State And Persistence
State is per-CPU IRQ numbers and allocated name strings. Bindings persist until CPU hotplug cleanup calls `xen_smp_intr_free`.

## Dependencies And Integration Points
Depends on Xen event APIs, Linux generic SMP IPI handlers, x86 vector constants, stolen-time detection, and `smp_ops` assignments in `smp_pv.c` and `smp_hvm.c`.

## Risks And Edge Cases
Binding failures must free all partially initialized IRQs. Unsupported vectors log an error and are dropped. `xen_smp_send_call_function_ipi` iterates the original mask for stolen vCPUs, so masks must describe valid CPUs. Debug VIRQ handling differs for FIFO events.

## Test Signals
Signals include successful CPU hotplug cycles, `/proc/interrupts` Xen IPI lines, scheduler and function-call IPI counters, no leaks after offline/online, and stress tests using `smp_call_function*`, rescheduling, NMI/debug paths, and HVM/PV boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/smp.c -->
