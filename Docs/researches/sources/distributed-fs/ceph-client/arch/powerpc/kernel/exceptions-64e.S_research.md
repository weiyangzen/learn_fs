# sources/distributed-fs/ceph-client/arch/powerpc/kernel/exceptions-64e.S

## Purpose

`exceptions-64e.S` is the low-level exception and early Book3E initialization implementation for 64-bit embedded PowerPC. It defines the interrupt vector base, vector stubs, common exception prologs, special-level return paths, masked interrupt replay, bad-stack handling, initial TLB construction, and IVOR setup for Book3E CPUs. It is architecture-critical code that turns hardware exception state into Linux `pt_regs` frames and then dispatches to C handlers such as `do_IRQ`, `do_page_fault`, `machine_check_exception`, `timer_interrupt`, `program_check_exception`, and facility-unavailable handlers.

## Important APIs, entry points, and macros

Key local routines include `special_reg_save`, `ret_from_level_except`, `ret_from_crit_except`, `ret_from_mc_except`, `storage_fault_common`, `alignment_more`, `bad_stack_book3e`, `initial_tlb_book3e`, `start_initialization_book3e`, `book3e_secondary_core_init`, `book3e_secondary_thread_init`, `init_core_book3e`, `init_thread_book3e`, and IVOR setup helpers such as `__setup_base_ivors`, `setup_altivec_ivors`, `setup_perfmon_ivor`, `setup_doorbell_ivors`, `setup_ehv_ivors`, and `setup_lrat_ivor`.

The main macro layer is `EXCEPTION_PROLOG`, specialized as `NORMAL_EXCEPTION_PROLOG`, `CRIT_EXCEPTION_PROLOG`, `DBG_EXCEPTION_PROLOG`, `MC_EXCEPTION_PROLOG`, and `GDBELL_EXCEPTION_PROLOG`. `EXCEPTION_COMMON_LVL` builds the register frame. `MASKABLE_EXCEPTION` generates external, decrementer, fixed-interval, and doorbell entries. `SEARCH_RESTART_TABLE` and `masked_interrupt_book3e` implement replay for interrupts taken while Linux has them soft-disabled.

## Control flow

Hardware vectors branch through `interrupt_base_book3e` stubs into named handlers. The prolog saves scratch state into PACA exception areas, chooses a normal or special stack, checks for user versus kernel mode, applies branch-target-buffer flushing when configured, and snapshots SRR, CR, LR, CTR, XER, GPRs, trap number, and soft-enable state into the interrupt frame. Synchronous storage and alignment paths collect DEAR/ESR before dispatch. Asynchronous maskable paths test `PACAIRQSOFTMASK`; if masked, they mark `PACAIRQHAPPENED`, optionally clear `MSR_EE`, search restart-table entries, and return without entering the full C handler.

Critical, debug, and machine-check levels use separate stacks and save extra SPR state including SRR, CSRR/MCSRR/DSRR-related state, MAS registers, DEAR, and ESR. Return paths restore that state and use `rfci` or `rfmci`. The debug exception has special handling to suppress single-step or branch-taken exceptions inside exception entry code, otherwise it calls `DebugException` for user-originated events; kernel debug exceptions are marked not yet implemented with a self-loop.

Early boot flow enters `start_initialization_book3e`, calls `initial_tlb_book3e` to construct a PAGE_OFFSET mapping, initializes core and thread state, and returns to common 64-bit boot code. Secondary Book3E CPUs follow similar initialization via `book3e_secondary_core_init` or `book3e_secondary_thread_init`.

## State and persistence behavior

Persistent per-CPU state is centered on PACA fields: exception scratch areas, kernel and special stacks, `PACAIRQSOFTMASK`, `PACAIRQHAPPENED`, `PACA_TRAP_SAVE`, and Book3E TLB exception frame pointers. Hardware persistent state includes IVPR/IVORs, EPCR, TCR/TSR, TLB entries, MAS registers, PID, and SRR/CSRR/MCSRR registers. The code also maintains global labels and TLB init code ranges used by platform bring-up, including the A2 no-branch TLB init window.

## Dependencies and integration points

This file depends on assembly offsets for `pt_regs`, `thread_info`, PACA layout, BookE interrupt numbers, MAS/TLB constants, CPU feature fixups, KVM BookE hooks, IRQ soft-mask definitions, and common return code from `interrupt_64.S`. It calls into Linux C handlers for page faults, IRQs, timers, watchdogs, debug, alignment, program checks, machine checks, and bad stacks. It is included through the 64-bit boot path for Book3E and is tightly coupled to `head_64.S`, `exception-64e.h`, `head_booke.h`, and nohash MMU code that patches entry branches.

## Risks and invariants

The highest risk is corrupting entry or return state before a full stack frame exists. Scratch SPR selection, PACA offsets, stack choice, and `r13` PACA restoration must remain exact. Masked interrupt replay must keep restart-table semantics and hardware masking consistent or interrupts can be lost or re-enter unsafe code. TLB initialization assumes specific firmware mappings and page size behavior; changing it can strand execution without a valid translation. Special-level exceptions note limitations around nested non-standard levels and kernel debug exceptions, making those paths sensitive to new features.

## Test signals

Useful validation signals include successful boot on Book3E 64-bit systems, secondary CPU bring-up, timer and external interrupt delivery, user and kernel page fault handling, FPU/Altivec unavailable handling, watchdog behavior, KVM guest exits where configured, bad-stack diagnostics, and machine-check recovery or panic behavior. Build coverage should include Book3E, embedded hypervisor feature sections, SMP, KVM BookE, Altivec, and watchdog configurations.
