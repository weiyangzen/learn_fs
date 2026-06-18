# sources/distributed-fs/ceph-client/arch/x86/kernel/head_64.S

## Purpose
Provides 64-bit x86 assembly startup for boot CPU, secondary CPUs, early IDT handlers, SEV/SME support, CR3/GDT/GS setup, and static initial page table definitions.

## Important Labels And State
Defines `startup_64`, `secondary_startup_64`, `secondary_startup_64_no_verify`, `common_startup_64`, optional `soft_restart_cpu`, `vc_boot_ghcb`, `early_idt_handler_array`, `early_idt_handler_common`, optional `vc_no_ghcb`, `initial_code`, `initial_vc_handler`, `trampoline_lock`, `early_top_pgt`, `early_dynamic_pgts`, `init_top_pgt`, `level4_kernel_pgt`, `level3_kernel_pgt`, `level2_kernel_pgt`, fixmap tables, `smpboot_control`, and exported `phys_base`.

## Control Flow And State
Boot CPU entry preserves `boot_params`, sets stack and GSBASE, loads temporary GDT/IDT, switches to kernel CS, enables SME/SEV if configured, verifies CPU, computes physical relocation delta, fixes page tables and encryption mask, switches CR3 to `early_top_pgt`, then jumps to `common_startup_64`. Secondary startup verifies CPU unless SEV-ES no-verify path, switches to `init_top_pgt`, preserves CR4 bits needed for PAE/LA57/MCE, resolves CPU number from APIC ID or `smpboot_control`, sets per-CPU stack and GSBASE, loads GDT, calls `early_setup_idt()`, enables EFER SCE/NX, sets CR0, and calls `initial_code`.

## Dependencies And Integration Points
Depends on compressed boot handoff, trampoline code, APIC/x2APIC, per-CPU offsets, SME/SEV/TDX helpers, restore_regs entry code, verify_cpu, initial page table constants, PTI layout, and `head64.c`.

## Risks And Test Signals
Risks include relocation/encryption mask mistakes, bad CR3 switch, stale real-mode stacks, APIC ID lookup failure, unsafe early #VC/#VE handling, and table alignment. Tests include direct 64-bit boot, compressed boot, SMP/parallel AP startup, CPU hotplug/soft restart, LA57, PTI, SEV/SEV-ES/SNP, TDX, and NX/EFER setup.
