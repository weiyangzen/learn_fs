# sources/distributed-fs/ceph-client/arch/x86/kernel/relocate_kernel_64.S

## Purpose
Implements 64-bit kexec relocation, including identity-mapped control-page execution, page copying/swapping, preserve-context return, cache-incoherent handling, and optional low-level serial/MMIO exception debugging.

## APIs, Types, And Functions
Exports `relocate_kernel`, `kexec_va_control_page`, `kexec_pa_table_page`, `kexec_pa_swap_page`, debug port/MMIO data, `kexec_debug_idt`, `kexec_debug_exc_vectors`, and `kexec_control_code_size`. Local routines include `identity_mapped`, `virtual_mapped`, `swap_pages`, 8250 print helpers, nybble/qword printers, and exception handler stubs.

## Control Flow
`relocate_kernel` saves GPRs/flags, invalidates old GDT/IDT, switches to kexec page tables, saves CR state, disables PGE/LASS, records backup map, moves to the physical control-page stack, and jumps into identity-mapped code. `identity_mapped` loads a debug GDT/IDT, normalizes CR0/CR4 including CET clearing and LA57/TDX MCE preservation, optionally executes `wbinvd`, calls `swap_pages()`, then either clears registers and returns to the target start address or calls the peer kernel and swaps pages back for preserve-context. `virtual_mapped` restores saved CRs, optional kexec-jump GDT, flags, and GPRs. `swap_pages()` interprets destination, indirection, done, and source entries and copies or swaps via the swap page depending on flags.

## State And Persistence
Relocation state is in `.data..relocate_kernel`, copied with the control page. Normal kexec permanently overwrites destination pages; preserve-context swaps them back. Debug output state persists only through configured serial/MMIO addresses.

## Dependencies And Integration
Depends on kexec page-table/control-page setup, CR0/CR3/CR4 feature constraints, TDX/SME cache-incoherent flags, CET/LASS handling, objtool unwind hints, retpoline annotations, and optional kexec jump state.

## Risks And Test Signals
This is among the most fragile boot-path assembly: bad CR4 bits, LA57 mismatch, CET/LASS handling, cache flush omission under memory encryption, or page-list corruption can fail kexec silently. Test signals include normal kexec, crashkernel, preserve-context kexec jump, encrypted-memory platforms, 5-level paging, TDX guests, and serial debug exception output when enabled.
