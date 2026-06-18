# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch/x86/include/asm/irq_vectors.h

## Purpose
This vendored x86 kernel header defines interrupt vector constants used by perf trace beauty generation/formatting for x86 IRQ vector names and ranges.

## Important APIs, Types, And Functions
The file is macro-only. Important constants include `NMI_VECTOR`, `FIRST_EXTERNAL_VECTOR`, `IA32_SYSCALL_VECTOR`, `ISA_IRQ_VECTOR(irq)`, APIC vectors from `SPURIOUS_APIC_VECTOR` down through posted interrupt and timer vectors, `NR_VECTORS`, `FIRST_SYSTEM_VECTOR`, `NR_EXTERNAL_VECTORS`, `NR_SYSTEM_VECTORS`, `NR_IRQS_LEGACY`, `CPU_VECTOR_LIMIT`, `IO_APIC_VECTOR_LIMIT`, and `NR_IRQS`.

## Control Flow
There is no runtime control flow. Preprocessor conditionals validate `SPURIOUS_APIC_VECTOR`, select `FIRST_SYSTEM_VECTOR` based on `CONFIG_X86_LOCAL_APIC`, and size `NR_IRQS` based on `CONFIG_X86_IO_APIC` and `CONFIG_PCI_MSI`.

## State, Dependencies, And Integration
The header depends on `linux/threads.h`, `NR_CPUS`, `MAX_IO_APICS`, and kernel config macros. In perf's copy, it provides stable source constants for generated or direct x86 vector beautifiers.

## Risks And Test Signals
The risk is drift from upstream kernel UAPI/internal x86 vector definitions, causing perf trace to print stale names. Build failures or mismatched generated tables are the main signals; runtime signals are incorrect x86 IRQ vector labels.
