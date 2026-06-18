## sources/distributed-fs/ceph-client/arch/mips/kernel/signal.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/signal.c` is the native MIPS signal delivery and return implementation. It builds traditional and realtime signal frames, saves and restores integer, DSP, FPU, MSA, and extended context state, selects ABI-specific frame builders through `struct mips_abi`, and handles signal work on return to user mode.

### Important APIs, Types, And Functions
Key frame types are `struct sigframe` and `struct rt_sigframe`. The FPU/MSA path is split between `copy_fp_to_sigcontext()`, `copy_fp_from_sigcontext()`, `save_hw_fp_context()`, `restore_hw_fp_context()`, `save_msa_extcontext()`, `restore_msa_extcontext()`, `save_extcontext()`, and `restore_extcontext()`. Exported or externally used helpers include `protected_save_fp_context()`, `protected_restore_fp_context()`, `setup_sigcontext()`, `restore_sigcontext()`, `fpcsr_pending()`, and `get_sigframe()`. Syscall entry points include legacy `sigsuspend`, legacy `sigaction`, `sys_sigreturn()`, and `sys_rt_sigreturn()`. `handle_signal()`, `do_signal()`, and `do_notify_resume()` are the runtime signal dispatch path.

### Control Flow
Signal delivery starts from `do_notify_resume()` when `_TIF_SIGPENDING` or `_TIF_NOTIFY_SIGNAL` is set. `do_signal()` either restarts an interrupted syscall or obtains a `ksignal`, then `handle_signal()` rolls back delay-slot emulation, rewrites restart state, calls `rseq_signal_deliver()`, and dispatches through the current thread ABI's `setup_frame` or `setup_rt_frame`. Frame setup chooses a user stack via `get_sigframe()`, copies siginfo/ucontext/sigmask, writes handler arguments into `$a0-$a2`, sets `$sp`, `$ra`, `$25`, and `cp0_epc`, then calls `signal_setup_done()`. Signal return validates the user frame, restores the blocked mask and altstack, calls `restore_sigcontext()`, possibly forces a pending FP signal, and jumps to `syscall_exit`.

### State, Persistence, And Dependencies
State is per-task and architectural: `current->thread.abi`, `current->thread.fpu`, FPU owner state, thread flags such as `TIF_32BIT_FPREGS`, `TIF_HYBRID_FPREGS`, MSA live flags, `current->restart_block`, saved signal masks, and user stack frame contents. Persistent user-visible ABI is the exact signal frame layout, `sigcontext` offsets, VDSO return stub offsets, syscall restart semantics, and FP/MSA extended context format. Dependencies include `asm/abi.h`, `asm/fpu.h`, `asm/msa.h`, `asm/dsp.h`, `linux/uaccess.h`, uprobes, rseq, alternate signal stacks, and the MIPS VDSO images.

### Integration Points
This file provides native ABI hooks through `mips_abi`, consumed by thread ABI selection and compat signal files. It integrates with `vdso.c` via `vdso_image` offsets, with `traps.c` through FPU/MSA state and FP exception behavior, with delay-slot emulation through `dsemul_thread_rollback()`, with uprobes through `_TIF_UPROBE`, and with generic signal core functions such as `get_signal()`, `set_current_blocked()`, and `restore_saved_sigmask()`.

### Risks
The highest risk is ABI breakage in frame size, alignment, register offsets, or VDSO return addresses. FPU/MSA save and restore races are subtle because live hardware state, preemption, EVA limitations, and task-owned context may differ. Syscall restart handling must preserve MIPS register conventions, especially `$v0`, `$a3`, and EPC rewind. Bad user pointers must reliably produce `SIGSEGV`, and extended-context parsing must reject malformed sizes or unknown magic values.

### Test Signals
Useful signals are native `sigaction`, `rt_sigaction`, alternate signal stack overflow, interrupted syscall restart with and without `SA_RESTART`, FPU and MSA register preservation across handlers, handler-created FCSR exceptions, malformed sigreturn frames, VDSO sigreturn stubs, uprobes resumption, rseq abort delivery, and 32-bit FP register model cases.
