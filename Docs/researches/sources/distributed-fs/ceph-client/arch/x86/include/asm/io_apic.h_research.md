<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io_apic.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/io_apic.h

## Purpose
IO-APIC declarations, routing-entry formats, pin/IRQ mapping, domain setup, and legacy interrupt routing hooks. The header is 218 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`; `#include <asm/mpspec.h>`; `#include <asm/apicdef.h>`; `#include <asm/irq_vectors.h>`; `#include <asm/x86_init.h>`

Notable constants/macros: `#define _ASM_X86_IO_APIC_H`; `#define IOAPIC_MAP_ALLOC 0x1`; `#define IOAPIC_MAP_CHECK 0x2`; `#define IO_APIC_IRQ(x) (((x) >= NR_IRQS_LEGACY) || ((1 << (x)) & io_apic_irqs))`; `#define io_apic_assign_pci_irqs \`; `#define IO_APIC_IRQ(x) 0`; `#define io_apic_assign_pci_irqs 0`; `#define setup_ioapic_ids_from_mpc x86_init_noop`; `#define nr_ioapics (0)`; `#define gsi_top (NR_IRQS_LEGACY)`; `#define native_io_apic_read NULL`; `#define native_restore_boot_irq_mode NULL`

Notable declarations and inline helpers: `#define _ASM_X86_IO_APIC_H`; `union IO_APIC_reg_00 {`; `u32 raw;`; `struct {`; `u32 __reserved_2 : 14,`; `union IO_APIC_reg_01 {`; `u32 version : 8,`; `union IO_APIC_reg_02 {`; `u32 __reserved_2 : 24,`; `union IO_APIC_reg_03 {`; `u32 boot_DT : 1,`; `struct IO_APIC_route_entry {`; `union {`; `u64 vector : 8,`; `u64 ir_shared_0 : 8,`; `u64 w1 : 32,`; `struct irq_alloc_info;`; `struct ioapic_domain_cfg;`; `#define IOAPIC_MAP_ALLOC 0x1`; `#define IOAPIC_MAP_CHECK 0x2`; `extern int nr_ioapics;`; `extern int mpc_ioapic_id(int ioapic);`; `extern unsigned int mpc_ioapic_addr(int ioapic);`; `extern int mp_irq_entries;`

## Control Flow
Boot code discovers IO-APICs, creates domains, maps GSI pins to vectors, configures trigger/polarity, and masks/acks/retriggers interrupts through these APIs.

## State and Persistence
State is IO-APIC MMIO registers, mp_ioapics metadata, pin-to-IRQ mappings, EOI routing, and irqdomain allocation data.

## Dependencies and Integration Points
Depends on ACPI/MPS tables, APIC/vector code, irqdomain, irq_remapping, MSI/legacy IRQ logic, and SMP CPU masks.

## Risks
Risks include wrong polarity/trigger, pin mapping conflicts, EOI delivery bugs, and interactions with interrupt remapping or PIC handoff.

## Test Signals
Tests should boot ACPI and MPS systems, exercise level/edge IRQs, IO-APIC hot paths, CPU affinity, irq remapping, suspend/resume, and no-IOAPIC fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io_apic.h -->
