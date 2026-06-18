<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq.h

## Purpose
Top-level x86 IRQ declarations for legacy IRQ canonicalization, IRQ stack init, IRQ fixups, backtrace IPIs, and native IRQ initialization. The header is 50 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/apicdef.h>`; `#include <asm/irq_vectors.h>`

Notable constants/macros: `#define _ASM_X86_IRQ_H`; `#define __irq_entry __invalid_section`; `#define arch_trigger_cpumask_backtrace arch_trigger_cpumask_backtrace`

Notable declarations and inline helpers: `#define _ASM_X86_IRQ_H`; `#define __irq_entry __invalid_section`; `static inline int irq_canonicalize(int irq)`; `extern int irq_init_percpu_irqstack(unsigned int cpu);`; `struct irq_desc;`; `extern void fixup_irqs(void);`; `extern void kvm_set_posted_intr_wakeup_handler(void (*handler)(void));`; `extern void (*x86_platform_ipi_callback)(void);`; `extern void native_init_IRQ(void);`; `extern void __handle_irq(struct irq_desc *desc, struct pt_regs *regs);`; `extern void init_ISA_irqs(void);`; `void arch_trigger_cpumask_backtrace(const struct cpumask *mask,`; `int exclude_cpu);`; `#define arch_trigger_cpumask_backtrace arch_trigger_cpumask_backtrace`

## Control Flow
Boot code calls native_init_IRQ()/init_ISA_irqs(), CPU bringup initializes per-CPU IRQ stacks, and runtime fixup/backtrace handlers route interrupts after CPU/hotplug changes.

## State and Persistence
State is IRQ descriptors, per-CPU IRQ stacks, platform IPI callback pointer, and posted interrupt wakeup handler.

## Dependencies and Integration Points
Depends on APIC definitions, irq_vectors.h, irq_desc, KVM posted interrupts, SMP cpumasks, and generic IRQ core.

## Risks
Risks include failing to move IRQs off offline CPUs, bad IRQ stack allocation, and platform IPI callback misuse.

## Test Signals
Tests should cover IRQ init, CPU hotplug fixup_irqs, posted interrupt wakeup, NMI/backtrace IPIs, and legacy ISA IRQ setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq.h -->
