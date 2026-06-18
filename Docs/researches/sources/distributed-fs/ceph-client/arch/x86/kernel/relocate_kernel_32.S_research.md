# sources/distributed-fs/ceph-client/arch/x86/kernel/relocate_kernel_32.S

## Purpose
Implements 32-bit kexec relocation code that runs from the control page, copies/swaps pages into the target kernel image locations, and either jumps to the new kernel or returns for preserve-context kexec jump.

## APIs, Types, And Functions
Exports assembly entry `relocate_kernel` and symbol `kexec_control_code_size`. Local routines are `identity_mapped`, `virtual_mapped`, and `swap_pages`. Data offsets in the control page save ESP, CR0, CR3, CR4, virtual/physical control data, page table, swap page, and backup map.

## Control Flow
`relocate_kernel` saves callee state and flags, records CPU control registers and stack in the control page, reads page list/start/PAE/preserve-context arguments, disables flags/interrupts, stores jump-back data, switches to the kexec page table, moves to the physical control-page stack, and returns into identity-mapped code. `identity_mapped` normalizes CR0/CR4, flushes TLB, calls `swap_pages()`, clears registers and returns to the new start address for normal kexec, or calls the peer kernel and later swaps pages back for kexec jump. `virtual_mapped` restores original CRs, stack, flags, and registers before returning.

## State And Persistence
Temporary state is stored in the high part of the control page. Page contents are permanently moved/swapped according to the indirection list. Preserve-context mode restores the original kernel mappings/state after the peer returns.

## Dependencies And Integration
Depends on kexec indirection page format, page-size constants, control-page allocation, identity mapping, x86 CR semantics, and retpoline/unret annotations.

## Risks And Test Signals
This code runs with minimal runtime services and wrong state can brick kexec. Risks include corrupt CR state, incorrect page copy order, preserve-context swap bugs, and non-relocatable code. Test signals are `kexec -e`, crashkernel boot, kexec jump where supported, objtool/annotation checks, and testing on PAE/non-PAE 32-bit configurations.
