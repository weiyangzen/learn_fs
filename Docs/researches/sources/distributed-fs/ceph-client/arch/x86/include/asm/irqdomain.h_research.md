<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irqdomain.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irqdomain.h

## Purpose
x86 IRQ domain declarations for vector, IO-APIC, HPET, and PCI MSI domains. The header is 64 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/irqdomain.h>`; `#include <asm/hw_irq.h>`

Notable constants/macros: `#define _ASM_IRQDOMAIN_H`; `#define native_create_pci_msi_domain NULL`; `#define x86_pci_msi_default_domain NULL`

Notable declarations and inline helpers: `#define _ASM_IRQDOMAIN_H`; `enum {`; `extern int x86_fwspec_is_ioapic(struct irq_fwspec *fwspec);`; `extern int x86_fwspec_is_hpet(struct irq_fwspec *fwspec);`; `extern struct irq_domain *x86_vector_domain;`; `extern void init_irq_alloc_info(struct irq_alloc_info *info,`; `extern void copy_irq_alloc_info(struct irq_alloc_info *dst,`; `struct irq_alloc_info *src);`; `struct device_node;`; `struct irq_data;`; `enum ioapic_domain_type {`; `struct ioapic_domain_cfg {`; `enum ioapic_domain_type type;`; `struct device_node *dev;`; `extern const struct irq_domain_ops mp_ioapic_irqdomain_ops;`; `extern int mp_irqdomain_alloc(struct irq_domain *domain, unsigned int virq,`; `unsigned int nr_irqs, void *arg);`; `extern void mp_irqdomain_free(struct irq_domain *domain, unsigned int virq,`; `unsigned int nr_irqs);`; `extern int mp_irqdomain_activate(struct irq_domain *domain,`; `struct irq_data *irq_data, bool reserve);`; `extern void mp_irqdomain_deactivate(struct irq_domain *domain,`; `struct irq_data *irq_data);`; `extern int mp_irqdomain_ioapic_idx(struct irq_domain *domain);`

## Control Flow
Allocation helpers initialize/copy irq_alloc_info, IO-APIC domain ops allocate/free/activate pins, and MSI domain creation installs native PCI MSI routing.

## State and Persistence
State is x86_vector_domain, x86_pci_msi_default_domain, IO-APIC domain config, and per-domain allocation metadata.

## Dependencies and Integration Points
Depends on linux/irqdomain, hw_irq allocation info, IO-APIC, HPET, PCI MSI, and hierarchical IRQ domains.

## Risks
Risks include parent-domain mismatches, incorrect fwspec classification, leaked virqs, and MSI domain absence under config variants.

## Test Signals
Tests should cover IO-APIC domain allocation, HPET IRQs, PCI MSI/MSI-X, domain activate/deactivate, ACPI fwspec parsing, and CONFIG_PCI_MSI stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irqdomain.h -->
