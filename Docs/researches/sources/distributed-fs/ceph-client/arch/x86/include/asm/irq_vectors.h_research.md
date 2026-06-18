<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_vectors.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_vectors.h

## Purpose
x86 interrupt vector number map and NR_IRQS sizing policy for exceptions, external IRQs, APIC system vectors, Hyper-V, KVM, posted MSI, and legacy IRQs. The header is 148 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/threads.h>`

Notable constants/macros: `#define _ASM_X86_IRQ_VECTORS_H`; `#define NMI_VECTOR 0x02`; `#define FIRST_EXTERNAL_VECTOR 0x20`; `#define IA32_SYSCALL_VECTOR 0x80`; `#define ISA_IRQ_VECTOR(irq) (((FIRST_EXTERNAL_VECTOR + 16) & ~15) + irq)`; `#define SPURIOUS_APIC_VECTOR 0xff`; `#define ERROR_APIC_VECTOR 0xfe`; `#define RESCHEDULE_VECTOR 0xfd`; `#define CALL_FUNCTION_VECTOR 0xfc`; `#define CALL_FUNCTION_SINGLE_VECTOR 0xfb`; `#define THERMAL_APIC_VECTOR 0xfa`; `#define THRESHOLD_APIC_VECTOR 0xf9`; `#define REBOOT_VECTOR 0xf8`; `#define X86_PLATFORM_IPI_VECTOR 0xf7`; `#define IRQ_WORK_VECTOR 0xf6`; `#define PERF_GUEST_MEDIATED_PMI_VECTOR 0xf5`; `#define DEFERRED_ERROR_VECTOR 0xf4`; `#define HYPERVISOR_CALLBACK_VECTOR 0xf3`

Notable declarations and inline helpers: `#define _ASM_X86_IRQ_VECTORS_H`; `#define NMI_VECTOR 0x02`; `#define FIRST_EXTERNAL_VECTOR 0x20`; `#define IA32_SYSCALL_VECTOR 0x80`; `#define ISA_IRQ_VECTOR(irq) (((FIRST_EXTERNAL_VECTOR + 16) & ~15) + irq)`; `#define SPURIOUS_APIC_VECTOR 0xff`; `#define ERROR_APIC_VECTOR 0xfe`; `#define RESCHEDULE_VECTOR 0xfd`; `#define CALL_FUNCTION_VECTOR 0xfc`; `#define CALL_FUNCTION_SINGLE_VECTOR 0xfb`; `#define THERMAL_APIC_VECTOR 0xfa`; `#define THRESHOLD_APIC_VECTOR 0xf9`; `#define REBOOT_VECTOR 0xf8`; `#define X86_PLATFORM_IPI_VECTOR 0xf7`; `#define IRQ_WORK_VECTOR 0xf6`; `#define PERF_GUEST_MEDIATED_PMI_VECTOR 0xf5`; `#define DEFERRED_ERROR_VECTOR 0xf4`; `#define HYPERVISOR_CALLBACK_VECTOR 0xf3`; `#define POSTED_INTR_VECTOR 0xf2`; `#define POSTED_INTR_WAKEUP_VECTOR 0xf1`; `#define POSTED_INTR_NESTED_VECTOR 0xf0`; `#define MANAGED_IRQ_SHUTDOWN_VECTOR 0xef`; `#define HYPERV_REENLIGHTENMENT_VECTOR 0xee`; `#define HYPERV_STIMER0_VECTOR 0xed`

## Control Flow
No runtime flow; constants partition 0..255 vectors into exception, external, and reserved system-vector ranges and size IRQ space by IO-APIC/CPU limits.

## State and Persistence
State is absent but the constants form a binary contract for IDT entries, APIC routing, and IRQ allocation.

## Dependencies and Integration Points
Depends on CONFIG_* vector users, NR_CPUS, MAX_IO_APICS, SMP, IO-APIC, Hyper-V, KVM, and local APIC support.

## Risks
Risks include vector collisions, insufficient NR_IRQS sizing, and config-dependent FIRST_SYSTEM_VECTOR shifts breaking entry declarations.

## Test Signals
Tests should compile vector-heavy configs, boot SMP/APIC systems, allocate many MSI vectors, exercise Hyper-V/KVM posted vectors, and verify no overlap assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_vectors.h -->
