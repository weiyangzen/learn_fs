# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_44x.S

## Purpose

`head_44x.S` is the 32-bit PowerPC 44x/47x kernel entry and exception head. It handles initial CPU state, early relocation and dynamic memory-start calculations, stack and current-task setup, transition into `start_kernel`, BookE vector definitions, fast-path 44x and 47x TLB miss handlers, IVOR/IVPR setup, machine-check fixups, and secondary 47x CPU entry.

## Important APIs, entry points, and labels

Global entry labels include `_stext`, `_start`, `__fixup_440A_mcheck`, `init_cpu_state`, and, under SMP 47x, `start_secondary_47x`. Important internal labels include `interrupt_base`, `finish_tlb_load_44x`, `finish_tlb_load_47x`, `head_start_47x`, `clear_all_utlb_entries`, `clear_utlb_entry`, `head_start_common`, and `temp_boot_stack`. The file uses macros from `head_booke.h`, including `CRITICAL_EXCEPTION`, `MCHECK_EXCEPTION`, `DATA_STORAGE_EXCEPTION`, `INSTRUCTION_STORAGE_EXCEPTION`, `EXCEPTION`, `ALIGNMENT_EXCEPTION`, `PROGRAM_EXCEPTION`, `FP_UNAVAILABLE_EXCEPTION`, `SYSCALL_ENTRY`, `DECREMENTER_EXCEPTION`, and `DEBUG_CRIT_EXCEPTION`.

## Control flow

Boot starts at `_start`, preserves the device tree pointer in `r31`, sets CPU number zero, optionally relocates a relocatable kernel, and calls `init_cpu_state`. It then initializes current task/thread pointers in `r2` and SPRG thread state, sets the initial stack, calls `early_init`, records physical/virtual offsets for relocatable or dynamic memory-start builds, optionally runs KASAN early init, calls `machine_init` and `MMU_init`, stores Abatron debug PTE pointers, clears MCSR, and jumps via SRR0/SRR1/RFI to `start_kernel`.

`interrupt_base` defines BookE vectors. Most vectors delegate to common macros, but data and instruction TLB errors are hand-coded fast paths. For 44x, TLB miss code saves scratch registers, determines kernel versus user address, selects `swapper_pg_dir` or current `PGDIR`, sets MMUCR TID from PID, rejects KUAP faults when PID is zero, loads PTE high/low words, checks permissions, rotates `tlb_44x_index` with patched high-water marks, and branches to `finish_tlb_load_44x` to write TLB words and return with `rfi`. On bailout it restores registers and branches to `DataStorage` or `InstructionStorage`.

47x TLB paths are similar but use 47x word formats, UTLB way handling, ordering barriers for SMP, and `finish_tlb_load_47x`. `init_cpu_state` distinguishes 44x from 476-class cores using PVR, invalidates old translations while preserving the executing entry, bolts a kernel mapping, optionally maps early debug UART, configures IVORs, and sets IVPR in `head_start_common`.

## State and persistence behavior

The file persists CPU state in SPRs: PID, MMUCR, IVPR/IVORs, CCR0, MCSR, SRR0/SRR1, and TLB entries. Kernel globals updated include `kernstart_addr`, `virt_phys_offset`, `abatron_pteptrs`, and `tlb_44x_index`. Secondary 47x startup uses `secondary_current` and a small static `temp_boot_stack` until normal stacks are reachable.

## Dependencies and integration points

Dependencies include BookE head macros, 44x/47x TLB constants, page table formats, patch sites for TLB high-water marks, KASAN, machine and MMU initialization C code, early debug configuration, secondary CPU C entry `start_secondary`, and generic handlers for exceptions not satisfied by fast TLB insertion. It is the root assembly entry for 44x platform builds.

## Risks and invariants

Fast TLB miss handlers are extremely sensitive to PTE format, permission bit mapping, PID/MMUCR setup, and scratch SPR use. A wrong bailout path can corrupt interrupted state. Boot mapping assumes firmware has provided a usable initial translation, and early relocation assumes 256 MB alignment constraints. IVOR offsets must match vector labels. On 47x, clearing UTLB entries and restoring the original entry must avoid invalidating the executing mapping too early.

## Test signals

Signals include boot on 44x and 476/47x systems, early serial debug, instruction and data TLB miss stress, user versus kernel page faults, KUAP fault behavior, SMP secondary 47x bring-up, machine-check vector fixup on 440A, syscall and decrementer tests, and builds with relocatable, dynamic memory-start, KASAN, early debug, FPU, watchdog, and SMP options.
