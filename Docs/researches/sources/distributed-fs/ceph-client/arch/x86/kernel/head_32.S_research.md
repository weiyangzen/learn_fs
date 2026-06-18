# sources/distributed-fs/ceph-client/arch/x86/kernel/head_32.S

## Purpose
Provides the 32-bit x86 assembly boot entry for BSP and APs, establishes initial GDT/segments, copies boot parameters, creates early page tables, enables paging, detects basic CPU properties, and supplies early exception/IRQ handlers.

## Important Labels And State
Defines `startup_32`, `startup_32_smp`, `early_idt_handler_array`, `early_idt_handler_common`, `early_ignore_irq`, `early_recursion_flag`, `initial_code`, early page tables (`initial_pg_pmd` or `initial_page_table`, `initial_pg_fixmap`, `swapper_pg_dir`), `initial_stack`, `boot_gdt_descr`, `early_gdt_descr`, and `boot_gdt`.

## Control Flow And Persistence
BSP entry loads a temporary GDT, normalizes segments and stack, clears BSS, copies boot params and command line, saves OLPC page directory if configured, calls `mk_early_pgtbl_32()`, initializes fixmap mapping, then joins `.Ldefault_entry`. SMP entry reuses boot GDT assumptions. Common path configures CR0/CR4, detects CPUID and NX under PAE, enables paging, switches to virtual stack, records CPU vendor/model/caps, loads kernel GDT, sets percpu segment, clears LDT, and calls `initial_code`. Early IDT stubs create uniform trap frames and call `early_fixup_exception()`.

## Dependencies And Integration Points
Depends on boot protocol register conventions, `verify_cpu.S`, early page tables from `head32.c`, segment constants, per-CPU descriptors, printk for early ignored IRQs, Xen head inclusion, and later `i386_start_kernel()`.

## Risks And Test Signals
Risks include fragile stack/segment state, wrong PAE/NX setup, boot param copy before mappings cover memory, early exception recursion, and page table alignment/PTI layout. Tests include 32-bit BSP/AP boot, old CPUs without CPUID/CR4, PAE+NX, PTI, OLPC, kexec, early fault handling, and objtool/entry validation.
