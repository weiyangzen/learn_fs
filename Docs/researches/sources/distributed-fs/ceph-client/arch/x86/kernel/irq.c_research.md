# sources/distributed-fs/ceph-client/arch/x86/kernel/irq.c

## Purpose
Provides common x86 interrupt accounting, normal device IRQ dispatch, bad IRQ acknowledgement, platform/KVM/perf/posted-MSI system-vector handlers, `/proc/interrupts` reporting, and CPU-hotplug IRQ migration cleanup.

## Important APIs And State
Exports per-CPU `irq_stat`, `__softirq_pending`, `hardirq_stack_ptr`, and atomic `irq_err_count`. Key functions include `ack_bad_irq()`, `arch_show_interrupts()`, `arch_irq_stat_cpu()`, `arch_irq_stat()`, `common_interrupt`, `sysvec_x86_platform_ipi`, optional KVM posted-interrupt handlers and setter, posted-MSI helpers, `fixup_irqs()`, and thermal vector handling.

## Control Flow
`common_interrupt` sets irq regs, verifies RCU watching, dispatches by vector through per-CPU `vector_irq[]`, and EOIs bad vectors. Dispatch reevaluates shutdown/unused vectors under vector lock to close races with free/request IRQ. `/proc` and `/proc/stat` helpers aggregate arch counters. Posted MSI notification marks handler active, enters IRQ context, harvests PIR bits up to a bounded coalescing loop plus a final post-ON-clear pass, handles each pending vector, EOIs, and leaves IRQ context. CPU hotplug migrates off-CPU IRQs, retriggers pending vectors if possible, and clears vector slots.

## Dependencies And Integration Points
Depends on APIC EOI, vector allocator state from `irqinit.c`, generic IRQ descriptors, RCU/irq entry code, tracepoints, KVM posted interrupts, Intel posted MSI descriptors, irq remapping, thermal/MCE/perf modules, and CPU hotplug.

## Risks And Test Signals
Risks include vector shutdown races, missing APIC EOI on bad/retriggered vectors, posted-MSI lost notifications, incorrect irq context nesting, and stale counters. Tests include high-rate MSI, IRQ free/request races, CPU hotplug with pending IRQs, KVM posted interrupts, posted MSI coalescing, `/proc/interrupts` counters, thermal/perf vectors, and spurious vector handling.
