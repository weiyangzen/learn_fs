<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hardirq.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hardirq.h

## Purpose
x86 hardirq accounting declarations and per-CPU IRQ stack metadata. The header is 97 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/threads.h>`

Notable constants/macros: `#define _ASM_X86_HARDIRQ_H`; `#define __ARCH_IRQ_STAT`; `#define inc_irq_stat(member) this_cpu_inc(irq_stat.member)`; `#define arch_irq_stat_cpu arch_irq_stat_cpu`; `#define arch_irq_stat arch_irq_stat`; `#define local_softirq_pending_ref __softirq_pending`

Notable declarations and inline helpers: `#define _ASM_X86_HARDIRQ_H`; `typedef struct {`; `u8 kvm_cpu_l1tf_flush_l1d;`; `unsigned int __nmi_count; /* arch dependent */`; `unsigned int apic_timer_irqs; /* arch dependent */`; `unsigned int irq_spurious_count;`; `unsigned int icr_read_retry_count;`; `unsigned int kvm_posted_intr_ipis;`; `unsigned int kvm_posted_intr_wakeup_ipis;`; `unsigned int kvm_posted_intr_nested_ipis;`; `unsigned int perf_guest_mediated_pmis;`; `unsigned int x86_platform_ipis; /* arch dependent */`; `unsigned int apic_perf_irqs;`; `unsigned int apic_irq_work_irqs;`; `unsigned int irq_resched_count;`; `unsigned int irq_call_count;`; `unsigned int irq_tlb_count;`; `unsigned int irq_thermal_count;`; `unsigned int irq_threshold_count;`; `unsigned int irq_deferred_error_count;`; `unsigned int irq_hv_callback_count;`; `unsigned int irq_hv_reenlightenment_count;`; `unsigned int hyperv_stimer0_count;`; `unsigned int posted_msi_notification_count;`

## Control Flow
The interrupt entry code increments/decrements hardirq state through generic code while x86 uses per-CPU irq_stack_ptr and irq_count fields where configured.

## State and Persistence
State is per-CPU hardirq counters and IRQ stack pointers, consumed by entry, lockdep, RCU, and stack-switching paths.

## Dependencies and Integration Points
Depends on linux/threads, irq_cpustat, cache alignment, SMP/percpu, and x86_64 IRQ stack setup.

## Risks
Risks include counter imbalance, wrong stack pointer initialization, and RCU/lockdep seeing incorrect interrupt context.

## Test Signals
Tests should stress nested interrupts, softirq from hardirq, CPU hotplug, lockdep IRQ state checks, and 32/64-bit stack configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hardirq.h -->
