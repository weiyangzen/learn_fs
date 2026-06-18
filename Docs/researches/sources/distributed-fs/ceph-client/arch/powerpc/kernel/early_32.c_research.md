<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/early_32.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/early_32.c

## Purpose
`early_32.c` performs very early 32-bit PowerPC initialization before normal relocation assumptions are valid. It clears BSS when appropriate, identifies the CPU, applies feature fixups, and returns the relocated kernel virtual address.

## Important APIs, Types, And Functions
The file defines `notrace unsigned long __init early_init(unsigned long dt_ptr)`. It uses `reloc_offset()`, `PTRRELOC`, `kernstart_virt_addr`, `__bss_start`, `__bss_stop`, `identify_cpu()`, `mfspr(SPRN_PVR)`, and `apply_feature_fixups()`.

## Control Flow
The function computes the relocation offset, reads the relocated kernel start virtual address, zeroes BSS only if running at `KERNELBASE`, identifies the CPU from PVR with the relocation offset, applies feature-dependent code patching, and returns `kva + offset`.

## State And Persistence
State changes include BSS zeroing, initialization of `cur_cpu_spec`, and patched feature sections. These persist for the booted kernel; no external persistence is involved.

## Dependencies And Integration Points
It is part of 32-bit boot and must use relocation-safe accesses before the kernel is fully relocated. It integrates with cputable, feature fixups, and linker-provided section symbols.

## Risks
Using non-relocated static addresses here can corrupt memory during early boot. BSS clearing must not run in cases where the boot path already relies on BSS data. Feature fixups must happen after CPU identification.

## Test Signals
Successful 32-bit boot across Book3S/BookE variants, correct CPU identification, feature-patched code paths, and no early boot BSS/relocation faults are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/early_32.c -->
