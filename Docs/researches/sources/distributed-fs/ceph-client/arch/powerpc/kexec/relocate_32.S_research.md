# sources/distributed-fs/ceph-client/arch/powerpc/kexec/relocate_32.S

## Purpose
Implements the 32-bit PowerPC low-level kexec relocation trampoline. It runs as position-independent code from the kexec control page, establishes a safe MMU/TLB state, copies source pages to destination pages from the kexec indirection list, flushes caches, and branches to the new kernel entry point.

## Important APIs, Types, And Functions
Exports `relocate_new_kernel` and `relocate_new_kernel_size`. The entry uses register arguments `r3` for the kexec page list, `r4` for the reboot code buffer/control page, and `r5` for the new kernel start address. It consumes kexec indirection flags `IND_DESTINATION`, `IND_INDIRECTION`, `IND_DONE`, and `IND_SOURCE`. Platform-specific setup is compiled for `CONFIG_PPC_85xx`, `CONFIG_44x`, and `CONFIG_PPC_47x`.

## Control Flow
The generic path disables translation by loading `SRR0/SRR1` and returning with `rfi`. PPC85xx includes the special entry mapping sequence. PPC44x cannot simply disable the MMU, so it invalidates all but the currently executing TLB entry, installs a temporary mapping in the alternate translation space, builds 1:1 256 MiB mappings for 0-2 GiB, jumps back to the original translation space, and removes the temporary entry. PPC47x performs equivalent UTLB invalidation and 1:1 setup using 47x TLB word formats. After translation setup, the copy loop parses the indirection list, sets destination/source page pointers, copies one page at a time with `lwzu/stwu`, performs data and instruction cache maintenance, synchronizes, and calls the new kernel.

## State And Persistence
No durable state is created. The code deliberately mutates processor state: MSR, PID/MMUCR, TLB entries, stack pointer, caches, and link register. It also writes destination memory pages that become the new kernel image. Register preservation is limited to what the trampoline itself needs before the final branch.

## Dependencies And Integration Points
Depends on PPC assembly register definitions, MMU/TLB constants, kexec control page layout, platform-specific entry mapping snippets, and the generic kexec page-list format. It integrates with the C kexec loader that places this code in the reboot code buffer and with architecture reset/secondary CPU shutdown code that transfers control here.

## Risks And Edge Cases
This is highly timing- and CPU-sensitive code. A wrong TLB index, page-size decode, translation-space bit, or cache flush can corrupt the running trampoline or the new kernel. PPC44x/47x paths assume the low 2 GiB mapping coverage is sufficient. The copy loop assumes page-aligned encoded addresses and valid indirection pages. Interrupts and translation must remain in the expected state until the new kernel is entered.

## Test Signals
Signals are architecture boot tests for kexec and crash kexec on PPC85xx, PPC44x, PPC47x, and generic 32-bit Book3S/BookE systems. Important cases are kernels loaded above/below existing mappings, many indirection pages, self-overlapping copy plans, SMP shutdown before relocation, and instruction-cache correctness after relocation.
