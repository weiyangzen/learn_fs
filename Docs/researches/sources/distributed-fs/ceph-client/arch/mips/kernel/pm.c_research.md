# sources/distributed-fs/ceph-client/arch/mips/kernel/pm.c

## Purpose
Registers CPU power-management notifiers that save and restore generic MIPS CPU context around CPU PM entry/exit events.

## Important APIs, Types, and Functions
- `mips_static_suspend_state` is the global suspend-state storage used by macros in `asm/pm.h`.
- `mips_cpu_save()` saves live FPU state through `lose_fpu(1)` and DSP state through `save_dsp(current)`.
- `mips_cpu_restore()` restores ASID, DSP, UserLocal, and hardware watch registers.
- `mips_pm_notifier()` handles `CPU_PM_ENTER`, `CPU_PM_ENTER_FAILED`, and `CPU_PM_EXIT`.
- `mips_pm_init()` registers the notifier with `cpu_pm_register_notifier()`.

## Control Flow
At `arch_initcall`, the notifier is registered. Before CPU PM entry, `mips_cpu_save()` forces live architectural extension state into the task context. On failed entry or exit, `mips_cpu_restore()` rewrites CP0 EntryHi ASID for the current mm, restores DSP, restores TLS/UserLocal if supported, and reloads watch registers.

## State and Persistence
State is transient CPU/task context, persisted only across a CPU low-power transition. No filesystem persistence exists.

## Dependencies and Integration Points
Integrates with the generic CPU PM notifier chain, MIPS FPU/DSP/watch helpers, MMU ASID management, and UserLocal TLS support. CPS PM power gating uses these lower-level save/restore guarantees.

## Risks
Missing a register class here causes state loss after CPU PM. Restore only writes ASID for tasks with `current->mm`; kernel-thread behavior relies on that distinction. Watch register restore must match ptrace watchpoint state.

## Test Signals
Suspend/resume and CPU idle transitions should preserve FPU/DSP calculations, TLS, watchpoints, and address-space correctness. CPU PM notifier registration failures should be visible during init.
