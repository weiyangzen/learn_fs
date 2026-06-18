# sources/distributed-fs/ceph-client/arch/powerpc/kernel/ptrace/ptrace-adv.c

## Purpose
`ptrace-adv.c` implements ptrace stepping and hardware debug support for PowerPC targets with advanced debug registers (`CONFIG_PPC_ADV_DEBUG_REGS`).

## Important APIs, Types, And Functions
It exports `user_enable_single_step()`, `user_enable_block_step()`, `user_disable_single_step()`, `ppc_gethwdinfo()`, `ptrace_get_debugreg()`, `ptrace_set_debugreg()`, `ppc_set_hwdebug()`, and `ppc_del_hwdebug()`. Internal helpers allocate and remove instruction address comparators (`set_instruction_bp()`, `del_instruction_bp()`), data address comparators (`set_dac()`, `del_dac()`), and optional DAC range mode (`set_dac_range()`).

## Control Flow
Single-step/block-step toggles DBCR0 instruction-complete or branch-taken bits and enables MSR_DE. Legacy debugreg access exposes DAC1 only. `ppc_set_hwdebug()` validates ABI version, trigger, address, mode, and condition fields, then routes execute breakpoints to IAC setup and read/write breakpoints to DAC exact or range setup. `ppc_del_hwdebug()` decodes the returned slot number and clears related DBCR, IAC, DAC, DVC, and range-mode state; if no debug events remain it clears DBCR0_IDM and MSR_DE.

## State And Persistence
All persistent debug state lives in `task->thread.debug` and `task->thread.regs->msr`; ptrace flags are stored via `TIF_SINGLESTEP`. Slot numbers returned to userspace are stable handles for later deletion.

## Dependencies And Integration Points
The file depends on BookE/embedded debug register macros such as DBCR0, DBCR1, DBCR2, IAC, DAC, and DVC helpers, plus the generic ptrace request path in `ptrace.c`. It is selected instead of `ptrace-noadv.c`.

## Risks
Slot-pair allocation for ranges is subtle: deleting the second half of a range is invalid, and exact breakpoints try to preserve pairs for future ranges. Address validation must prevent kernel-space traps. MSR_DE must stay enabled while any debug event is active and disabled only when all events are gone.

## Test Signals
Exercise single step, block step, exact execute breakpoints, IAC inclusive/exclusive ranges, DAC read/write exact breakpoints, DAC ranges and masks where configured, DVC conditions, deletion by returned slot, invalid slot deletion, and address values at or above `TASK_SIZE`.
