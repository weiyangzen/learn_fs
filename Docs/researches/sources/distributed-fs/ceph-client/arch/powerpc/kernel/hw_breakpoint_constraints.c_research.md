# sources/distributed-fs/ceph-client/arch/powerpc/kernel/hw_breakpoint_constraints.c

## Purpose
Provides the address, access-type, privilege, and instruction-size constraint checks used by the PowerPC hardware watchpoint exception handler.

## Important APIs, Types, And Functions
Exports `wp_check_constraints` and `wp_get_instr_detail`. Internal helpers include `dar_in_user_range`, `ea_user_range_overlaps`, `dar_in_hw_range`, `ea_hw_range_overlaps`, and `check_dawrx_constraints`. It uses `struct arch_hw_breakpoint`, `struct pt_regs`, `ppc_inst_t`, `struct instruction_op`, and instruction type/size macros from the single-step decoder.

## Control Flow
`wp_get_instr_detail` fetches the instruction at `regs->nip` with page faults disabled, decodes it, computes effective address and size, truncates 32-bit effective addresses, and normalizes cache/VMX accesses to their real access granularity. `wp_check_constraints` first treats 8xx as a single-breakpoint special case, then handles failed instruction decode, unknown instruction types, exact user-range overlap, hardware-aligned overlap, and privilege/access filters from DAWRX-style bits. Hardware-aligned but user-range-missing matches are marked as extraneous so callbacks can be suppressed when appropriate.

## State And Persistence
The file has no long-lived state. It mutates only `info->type` by setting `HW_BRK_TYPE_EXTRANEOUS_IRQ` when a hardware match is valid at DAWR granularity but not within the requested user range.

## Dependencies And Integration Points
Depends on PowerPC instruction decoding in `asm/sstep.h`, cache line size helpers, CPU feature `CPU_FTR_ARCH_31`, user instruction access helpers, and the main handler in `hw_breakpoint.c`. It encodes DAWR granularity assumptions used by perf and ptrace watchpoint delivery.

## Risks And Edge Cases
Risks include integer overlap checks near address wraparound, cache-op size normalization, VMX alignment, quadword behavior before ARCH_31, inability to fetch user instructions, and unknown decoded instruction types. If constraints are too permissive, users see false watchpoint hits; if too strict, real hardware matches are lost.

## Test Signals
Signals include watchpoint tests for read-only, write-only, read/write, user-only, kernel-only, cache operations, VMX/VSX aligned accesses, unknown or faulting instruction fetches, and DAWR granularity false-positive suppression on pre-ARCH_31 and ARCH_31 CPUs.
