# sources/distributed-fs/ceph-client/arch/x86/kernel/idt.c

## Purpose
Builds and installs x86 IDT entries for early traps, default exceptions, IA32 syscall vector, APIC/SMP system vectors, normal external interrupt gates, spurious gates, and late read-only CPU-entry-area mapping.

## Important APIs And State
Defines IDT descriptor tables (`early_idts`, `def_idts`, `ia32_idt`, `apic_idts`), page-aligned `idt_table`, `idt_descr`, and `idt_setup_done`. Public functions include `load_current_idt()`, optional `idt_is_f00f_address()`, `idt_setup_early_traps()`, `idt_setup_traps()`, `idt_setup_early_pf()`, `idt_setup_apic_and_irq_gates()`, `idt_setup_early_handler()`, `idt_invalidate()`, and `idt_install_sysvec()`.

## Control Flow
Early boot can install generic early handler array entries for all exception vectors. Later trap setup installs explicit exception gates, with IST variants on 64-bit after TSS/CPU init, and IA32 syscall gates when enabled. `idt_setup_apic_and_irq_gates()` installs APIC/SMP vectors, fills remaining external vectors from `irq_entries_start`, fills remaining system vectors with spurious handlers, maps the IDT read-only into the CPU entry area, reloads it, marks backing memory RO, and freezes further sysvec installation. `idt_install_sysvec()` permits early dynamic system-vector reservation before final setup.

## Dependencies And Integration Points
Depends on descriptor helpers, trap assembly labels, APIC vector definitions, `system_vectors` bitmap, CPU entry area, set_memory RO, IA32 emulation, FRED invalidation use, and interrupt entry stubs.

## Risks And Test Signals
Risks include wrong DPL/IST/segment selection, missing system vector bitmap bits, late sysvec installation after IDT lock-down, leaking kernel IDT address, and F00F compatibility. Tests include early exception delivery, page fault transition, APIC/SMP vectors, IA32 int80, read-only IDT mapping, sysvec installation warnings, and FRED mode invalidation.
