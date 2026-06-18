# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_booke.h

## Purpose
Defines common assembler macros for BookE exception vector setup, normal/critical/debug/machine-check prologs, syscall entry, KVM interception hooks, MMU register saving, and standard storage/alignment/program/decrementer/FPU exception bodies.

## Important APIs, Types, And Functions
Major macros include `SET_IVOR`, `ALLOC_STACK_FRAME`, `THREAD_NORMSAVE`, `NORMAL_EXCEPTION_PROLOG`, `COMMON_EXCEPTION_PROLOG_END`, `prepare_transfer_to_handler`, `SYSCALL_ENTRY`, `BOOKE_LOAD_EXC_LEVEL_STACK`, `EXC_LEVEL_EXCEPTION_PROLOG`, `SAVE_xSRR`, `SAVE_MMU_REGS`, `CRITICAL_EXCEPTION_PROLOG`, `DEBUG_EXCEPTION_PROLOG`, `MCHECK_EXCEPTION_PROLOG`, `GUEST_DOORBELL_EXCEPTION`, `START_EXCEPTION`, `EXCEPTION`, `CRITICAL_EXCEPTION`, `MCHECK_EXCEPTION`, `DEBUG_DEBUG_EXCEPTION`, `DEBUG_CRIT_EXCEPTION`, `DATA_STORAGE_EXCEPTION`, `INSTRUCTION_STORAGE_EXCEPTION`, `ALIGNMENT_EXCEPTION`, `PROGRAM_EXCEPTION`, `DECREMENTER_EXCEPTION`, and `FP_UNAVAILABLE_EXCEPTION`.

## Control Flow
Vector files instantiate these macros to build aligned exception labels. Normal exceptions save scratch state in thread save slots, switch to kernel MSR, choose current or top-of-kernel stack based on MSR_PR, build a `pt_regs` frame, save volatile and nonvolatile GPRs, and call the C handler. Critical, machine-check, and debug paths use dedicated per-CPU stacks and distinct xSRR registers so they can interrupt normal exception handling. Syscall entry builds a compact frame and branches to `transfer_to_syscall`. Debug macros detect accidental single-step traps in vector entry code and clear DE/DBSR to resume the original exception safely.

## State And Persistence
The macros manipulate CPU SPRs, per-thread scratch save slots, per-CPU critical/debug/machine-check stacks, `pt_regs`, MSR bits, and KVM state transitions. They do not own durable data but define the frame layout and register-saving contract that all BookE exception return code relies on.

## Dependencies And Integration Points
Depends on `asm/ptrace.h`, `asm/kvm_asm.h`, `asm/kvm_booke_hv_asm.h`, `asm/thread_info.h`, BookE SPR definitions, stack offsets, KVM `DO_KVM` handlers, and low-level return paths such as `interrupt_return`, `ret_from_crit_exc`, `ret_from_mcheck_exc`, and `ret_from_debug_exc`. It integrates with page fault, alignment, program, timer, FPU, debug, and syscall C handlers.

## Risks And Edge Cases
Because these macros generate entry code, mistakes corrupt every BookE interrupt path. Risks include stack selection during nested critical exceptions, incomplete MMU/xSRR saving, stale ESR/DEAR values, MSR_DE single-step recursion in vector code, KVM GS/HV dispatch ordering, and differences between e500/e500mc/debug-level configurations. The `INSTRUCTION_STORAGE_EXCEPTION` explicitly zeros ESR to avoid stale store-fault state confusing page fault handling.

## Test Signals
Signals include build coverage for BookE/e500/e500mc/KVM/debug variants, boot-time vector setup, syscall smoke tests, nested machine-check or debug exception tests where available, page fault and alignment fault handling, timer/decrementer interrupts, FPU unavailable traps, and kgdb/kprobes tests that exercise debug exceptions.
