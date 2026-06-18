# sources/distributed-fs/ceph-client/arch/x86/kernel/head32.c

## Purpose
Prepares 32-bit x86 C boot flow after early assembly: sets early platform hooks, installs early IDT, loads microcode, sanitizes boot parameters, and builds early page tables.

## Important APIs And State
Defines `i386_start_kernel()`, `mk_early_pgtbl_32()`, and helper `init_map()`. With `CONFIG_MICROCODE_INITRD32`, tracks `initrd_start_early`, `initrd_pl2p_start`, and `initrd_pl2p_end` so temporary initrd mappings can be removed after microcode loading.

## Control Flow
`i386_start_kernel()` installs early handlers, loads BSP microcode, zaps early initrd mappings, initializes CR4 shadow, sanitizes boot params, runs early platform quirks, selects subarchitecture setup, then calls `start_kernel()`. `mk_early_pgtbl_32()` creates identity and PAGE_OFFSET mappings for the kernel and lowmem page tables, records `max_pfn_mapped` and `_brk_end`, and optionally maps the initrd early enough for 32-bit microcode loading.

## Dependencies And Integration Points
Depends on boot params from assembly, IDT setup, microcode loader, x86 platform init hooks, IO-APIC/APIC setup callbacks, memblock/brk space, PAE vs non-PAE page table formats, and subarch setup.

## Risks And Test Signals
Risks include early mapping limits, incorrect physical/virtual pointer writes before paging is fully stable, leaked initrd mappings, and wrong subarch resource callbacks. Test signals include 32-bit boot across PAE/non-PAE, microcode-in-initrd boot, kexec boot params, early page faults, and successful transition to `start_kernel()`.
