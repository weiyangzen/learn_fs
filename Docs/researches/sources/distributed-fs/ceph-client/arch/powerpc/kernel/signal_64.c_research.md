# sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal_64.c

## Purpose
Implements 64-bit PowerPC signal delivery, `rt_sigreturn`, and `swapcontext` handling. The file builds/restores user `ucontext`/`sigcontext` frames, including FP, AltiVec/VMX, VSX, endian state, signal masks, alternate stack state, and the special two-context layout needed when a signal interrupts transactional memory.

## Important APIs, Types, and Functions
- `struct rt_sigframe` is the ABI-visible stack frame: `ucontext` first for `sys_rt_sigreturn`, optional transactional `ucontext`, trampoline words, `siginfo`, and the ELFv2 redzone gap.
- `get_min_sigframe_size_64()` reports minimum stack usage to common signal code.
- `prepare_setup_sigcontext()` flushes lazy FP/VMX/VSX state into `thread_struct` before copying to userspace.
- `__unsafe_setup_sigcontext()` writes a normal `sigcontext`, including GPRs, FPRs, VMX/VRSAVE, VSX low halves, `signal`, `handler`, and optional old mask.
- `setup_tm_sigcontexts()` and `restore_tm_sigcontexts()` save/restore checkpointed and transactional register state for TM-aware signal frames.
- `setup_trampoline()` emits an on-stack fallback `bctrl; addi r1; li r0; sc` trampoline when no VDSO signal trampoline exists.
- `SYSCALL_DEFINE3(swapcontext)` saves the old user context and restores a new one, validating whether VSX state is present in the supplied size.
- `SYSCALL_DEFINE0(rt_sigreturn)` restores state from the user frame, including TM cleanup/recheckpointing, altstack restore, and `_TIF_RESTOREALL`.
- `handle_rt_signal64()` allocates and fills the signal frame, sets the return address to VDSO or stack trampoline, and rewrites `pt_regs` so userspace enters the handler.

## Control Flow and State
Signal delivery begins with `get_sigframe()`, optional `prepare_setup_sigcontext()`, an unsafe user write window to populate `rt_sigframe`, a later `copy_siginfo_to_user()`, and finally register edits that arrange handler arguments and the return path. Return flow begins at `rt_sigreturn`, reads `uc_sigmask`, handles any suspended TM state, selects normal or TM restore, restores altstack state, and marks the thread to restore all user registers. `swapcontext` has a two-phase flow: write old context first, then fault-in/read the new context and kill with `SIGSEGV` if a late partial restore fault corrupts register state.

## State and Persistence Behavior
The code persists architectural register state into user memory and restores from it later. It mutates `current->blocked`, `current->restart_block`, `thread_struct` FP/VMX/VSX/TM fields, `pt_regs`, VRSAVE, and `_TIF_RESTOREALL`. TM restore disables preemption around MSR[TS] recheckpointing because page faults or rescheduling with transactional state half-restored can cause a TM bad thing.

## Dependencies and Integration Points
Depends on common signal helpers in `signal.h`, `uaccess`, VDSO symbols, `asm/switch_to.h`, `asm/tm.h`, FP/VMX/VSX save helpers, and syscall table wiring. It is tightly coupled to PowerPC ABI stack layout, ELFv1 function descriptors versus ELFv2 entry points, MSR bits, and the transactional memory assembly in `tm.S`.

## Risks
User-provided frames are trusted only through explicit `access_ok`, `fault_in_readable`, and unsafe access windows; any missing check can corrupt kernel return state. TM paths are fragile because no user access may occur after MSR[TS] is restored. ABI regressions in frame layout, VSX sizing, endian MSR handling, or handler descriptor setup would break signal delivery, debuggers, runtimes, and checkpoint/restore. Trampoline patching requires cache flushing and is sensitive on no-VDSO systems.

## Test Signals
Exercise `rt_sigreturn`, nested signals, `sigaltstack`, VDSO and no-VDSO paths, ELFv1/ELFv2 handlers, `swapcontext` with old and new context sizes, 32-byte VSX extensions, endian switching, FP/VMX/VSX register preservation, bad user frames, and TM-active signals followed by normal return, modified context return, and invalid reserved TM modes.
