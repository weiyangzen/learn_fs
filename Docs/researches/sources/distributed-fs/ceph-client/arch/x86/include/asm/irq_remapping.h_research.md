<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_remapping.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_remapping.h

## Purpose
Interrupt remapping interface for Intel/AMD IOMMU-backed IRQ domains and posted interrupt metadata. The header is 98 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/irqdomain.h>`; `#include <asm/hw_irq.h>`; `#include <asm/io_apic.h>`

Notable constants/macros: `#define __X86_IRQ_REMAPPING_H`; `#define intel_ack_posted_msi_irq NULL`

Notable declarations and inline helpers: `#define __X86_IRQ_REMAPPING_H`; `struct msi_msg;`; `struct irq_alloc_info;`; `enum irq_remap_cap {`; `enum {`; `struct amd_iommu_pi_data {`; `u64 vapic_addr; /* Physical address of the vCPU's vAPIC. */`; `u32 ga_tag;`; `u32 vector; /* Guest vector of the interrupt */`; `int cpu;`; `bool ga_log_intr;`; `bool is_guest_mode;`; `void *ir_data;`; `struct intel_iommu_pi_data {`; `u64 pi_desc_addr; /* Physical address of PI Descriptor */`; `extern raw_spinlock_t irq_2_ir_lock;`; `extern bool irq_remapping_cap(enum irq_remap_cap cap);`; `extern void set_irq_remapping_broken(void);`; `extern int irq_remapping_prepare(void);`; `extern int irq_remapping_enable(void);`; `extern void irq_remapping_disable(void);`; `extern int irq_remapping_reenable(int);`; `extern int irq_remap_enable_fault_handling(void);`; `extern void panic_if_irq_remap(const char *msg);`

## Control Flow
Boot enables/remaps IRQs, exposes capability checks, creates parent vector domains, and uses AMD/Intel PI data structures to target vCPU posted interrupts.

## State and Persistence
State is remapping hardware tables, irq_2_ir_lock protected mappings, enable_posted_msi, and per-interrupt PI data.

## Dependencies and Integration Points
Depends on irqdomain, hw_irq, io_apic, IOMMU drivers, MSI, KVM posted interrupts, and x2APIC/xAPIC modes.

## Risks
Risks include enabling x2APIC without remapping, stale PI descriptors, remap fault handling gaps, and fallback stubs masking missing hardware.

## Test Signals
Tests should boot with Intel/AMD IRQ remapping, x2APIC, MSI/MSI-X, KVM posted interrupts, remap fault injection, and no-remap fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_remapping.h -->
