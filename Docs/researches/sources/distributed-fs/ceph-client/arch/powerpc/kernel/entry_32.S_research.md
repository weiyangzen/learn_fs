<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/entry_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/entry_32.S

## Purpose
`entry_32.S` implements 32-bit PowerPC syscall entry/return, fork thread entry, fast exception return, normal interrupt return, KUEP segment locking, and BookE critical/debug/machine-check return paths. It is the low-level bridge between saved exception frames and C interrupt/syscall handlers.

## Important APIs, Types, And Functions
Important entry symbols include `prepare_transfer_to_handler`, `__kuep_lock`, local `__kuep_unlock`, `transfer_to_syscall`, `ret_from_syscall`, `syscall_exit_finish`, `ret_from_fork`, `ret_from_kernel_user_thread`, `start_kernel_thread`, `fast_exception_return`, `interrupt_return`, `ret_from_crit_exc`, `ret_from_debug_exc`, and `ret_from_mcheck_exc`. It calls C helpers such as `system_call_exception`, `syscall_exit_prepare`, `schedule_tail`, `interrupt_exit_user_prepare`, `interrupt_exit_kernel_prepare`, and `unrecoverable_exception`.

## Control Flow
Syscall entry saves GPRs and frame metadata, locks user execute permission when configured, calls the C syscall handler, runs syscall exit preparation, handles 44x I-cache flushing, unlocks KUEP, restores registers, and returns with `rfi`. Interrupt return chooses user or kernel exit preparation based on MSR_PR, clears reservations and stack markers, optionally restores nonvolatile registers, emulates delayed `stwu` stack stores for kernel returns, and executes `rfi`. BookE special returns restore xSRR/MMU state and return with `rfci`, `rfdi`, or `rfmci`. Napping/sleeping flags redirect interrupted low-power returns.

## State And Persistence
State is CPU register, SPR, stack frame, thread flag, and segment register state. It persists only as live execution context.

## Dependencies And Integration Points
It depends on exact `pt_regs`/thread-info offsets, KUEP/KUAP helpers, BookE SPR layouts, feature fixup sections, syscall and interrupt C code, stack unwinder marker conventions, and CPU-specific errata macros.

## Risks
Register restore order is extremely fragile. KUEP unlock/lock mistakes can expose user mappings in kernel or break user return. TLB misses between SRR writes and `rfi` are avoided by alignment; moving code can violate that. BookE special interrupt returns must restore the right SPR sets.

## Test Signals
Signals include syscall ABI tests, fork/kernel-thread startup, interrupt/preemption stress, KUEP/KUAP tests, stack unwinder reliability, 44x I-cache flush paths, BookE critical/debug/machine-check return testing, and membarrier sync-core assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/entry_32.S -->
