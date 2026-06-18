# sources/distributed-fs/ceph-client/arch/powerpc/kernel/head_32.h

## Purpose

`head_32.h` defines shared 32-bit PowerPC exception-entry macros used by 32-bit head assembly files. It constructs the physical-mode exception prolog, switches to virtual execution, builds `pt_regs`, handles syscall entry, supports KVM vector hooks on Book3S, and provides a VMAP stack overflow emergency path.

## Important APIs, entry points, and macros

The main macros are `EXCEPTION_PROLOG`, `EXCEPTION_PROLOG_0`, `EXCEPTION_PROLOG_1`, `EXCEPTION_PROLOG_2`, `COMMON_EXCEPTION_PROLOG_END`, `prepare_transfer_to_handler`, `SYSCALL_ENTRY`, `START_EXCEPTION`, `EXCEPTION`, and `vmap_stack_overflow_exception`. They are not C APIs; they are included by 32-bit PowerPC assembly files to generate vector-specific handlers. The macros rely on SPR scratch registers, `SPRN_SPRG_THREAD`, SRR0/SRR1, DAR/DSISR, and stack layout offsets.

## Control flow

`EXCEPTION_PROLOG_0` saves scratch GPRs in SPRGs, loads the physical thread pointer, optionally saves DAR/DSISR, saves SRR0/SRR1 into the thread area, captures CR, and determines user versus kernel mode from `MSR_PR`. `EXCEPTION_PROLOG_1` saves the original stack pointer, chooses the interrupted kernel stack or the current task's kernel stack for user exceptions, and checks for VMAP stack overflow when configured. `EXCEPTION_PROLOG_2` programs SRR0/SRR1 to return to a virtual-mode continuation, executes `rfi`, then saves registers into the new interrupt frame and enables recoverable kernel MSR state.

`COMMON_EXCEPTION_PROLOG_END` marks the frame, stores trap number, saves volatile and nonvolatile registers, records NIP/MSR/CTR/XER, sets `r2` to current task, and passes a `pt_regs` pointer in `r3`. `prepare_transfer_to_handler` invokes 32-bit Book3S transfer preparation and optional KUEP locking for user-originated exceptions. `SYSCALL_ENTRY` is a syscall-specific fast path that builds only the needed frame state before branching to `transfer_to_syscall`.

## State and persistence behavior

The macros use physical `thread_struct` storage for SRR0/SRR1 and optional DAR/DSISR before translation is restored, then store the canonical state in the interrupt frame on the kernel stack. SPRG scratch registers temporarily hold original GPRs and stack pointer. For VMAP stack overflow, the code switches to per-CPU `emergency_ctx` storage before building the frame.

## Dependencies and integration points

Dependencies include `asm/ptrace.h` for `STACK_FRAME_REGS_MARKER`, thread and stack offsets, `SAVE_GPRS`/`SAVE_NVGPRS`, KVM `DO_KVM` hooks on Book3S, KUEP helpers, 8xx special handling, and the surrounding head files that define concrete vectors. Generated paths dispatch to C handlers and then branch to `interrupt_return`; syscall paths branch to `transfer_to_syscall`.

## Risks and invariants

The code runs with address translation off at entry, so physical versus virtual address transitions must remain exact. Register ordering matters because only scratch SPRs are available before a stack is selected. The VMAP overflow check relies on stack alignment bits in CR fields. `EXCEPTION_PROLOG_2` must set a recoverable MSR at the correct point; enabling exceptions too early or too late can break machine-check and page-fault behavior. Any change to `pt_regs` offsets must be reflected in assembly offsets.

## Test signals

Signals include booting 32-bit Book3S/BookE/8xx configurations, syscall ABI tests, page fault and alignment exception tests, KVM Book3S interrupt handling, VMAP stack overflow diagnostics, KUEP behavior on user transitions, and interrupt-return stress under preemption and SMP.
