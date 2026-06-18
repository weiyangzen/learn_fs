<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_irq.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_irq.h

## Purpose
x86 hardware IRQ/vector allocation structures, vector-to-desc mapping, APIC acknowledgement hooks, and interrupt statistics. The header is 135 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/irq_vectors.h>`; `#include <linux/percpu.h>`; `#include <linux/profile.h>`; `#include <linux/smp.h>`; `#include <linux/atomic.h>`; `#include <asm/irq.h>`; `#include <asm/sections.h>`

Notable constants/macros: `#define _ASM_X86_HW_IRQ_H`; `#define trace_irq_entries_start irq_entries_start`; `#define VECTOR_UNUSED NULL`; `#define VECTOR_SHUTDOWN ((void *)-1L)`; `#define VECTOR_RETRIGGERED ((void *)-2L)`

Notable declarations and inline helpers: `#define _ASM_X86_HW_IRQ_H`; `struct irq_data;`; `struct pci_dev;`; `struct msi_desc;`; `enum irq_alloc_type {`; `struct ioapic_alloc_info {`; `int pin;`; `int node;`; `u32 is_level : 1;`; `u32 active_low : 1;`; `u32 valid : 1;`; `struct uv_alloc_info {`; `int limit;`; `int blade;`; `unsigned long offset;`; `struct irq_alloc_info {`; `enum irq_alloc_type type;`; `u32 flags;`; `u32 devid;`; `struct msi_desc *desc;`; `void *data;`; `union {`; `struct ioapic_alloc_info ioapic;`; `struct uv_alloc_info uv;`

## Control Flow
IRQ domain allocation fills irq_alloc_info, vector assignment records irq_cfg per IRQ, and entry stubs use per-CPU vector_irq arrays to dispatch vectors.

## State and Persistence
State is per-CPU vector_irq, irq_cfg mappings, irq_err_count/irq_mis_count, and vector cleanup state.

## Dependencies and Integration Points
Depends on irq_vectors.h, irqdomain hierarchy, APIC, MSI descriptors, SMP, percpu storage, and tracing symbols for entry stubs.

## Risks
Risks include vector leaks, stale vector cleanup after migration, incorrect IRQ allocation type data, and interrupt stats hiding routing bugs.

## Test Signals
Tests should exercise IO-APIC, MSI/MSI-X, CPU affinity changes, hotplug, vector exhaustion, spurious/error interrupts, and tracing entry symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_irq.h -->
