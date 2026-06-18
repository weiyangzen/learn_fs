# sources/distributed-fs/ceph-client/arch/x86/kernel/step.c

## Purpose
`step.c` implements x86 ptrace single-step and block-step control, including TF/BTF management, syscall-exit traps, LDT/vm86 linear IP conversion, and bookkeeping for debugger-forced TF.

## Important APIs, Types, And Functions
Public functions are `convert_ip_to_linear()`, `set_task_blockstep()`, `user_enable_single_step()`, `user_enable_block_step()`, and `user_disable_single_step()`. Internals include `is_setting_trap_flag()`, `enable_single_step()`, and `enable_step()`.

## Control Flow
Linear IP conversion handles vm86 and LDT segment bases, including 16-bit code. Enabling step sets `TIF_SINGLESTEP`, syscall exit trap work, and TF, then inspects the next instruction to avoid claiming TF ownership across `popf`/`iret`. Block-step sets `DEBUGCTLMSR_BTF` and `TIF_BLOCKSTEP`. Disable clears BTF, single-step work, and TF only if `TIF_FORCED_TF` says the kernel set it.

## State, Persistence, Dependencies, Integration
State lives in `pt_regs->flags`, `TIF_SINGLESTEP`, `TIF_FORCED_TF`, `TIF_BLOCKSTEP`, syscall work flags, and `MSR_IA32_DEBUGCTLMSR`. Dependencies include ptrace freeze discipline, debug registers, LDT locking, `access_process_vm()`, and syscall exit work. `traps.c` consumes generated #DB events.

## Risks And Test Signals
Misclassifying user TF corrupts user-visible flags. Block-step MSR changes are safe only for current or frozen tasks. Test ptrace single/block step across ordinary instructions, syscalls/sysenter, signal delivery, `popf`/`iret`, vm86, LDT 16-bit code, user-owned TF, and ptrace races.
