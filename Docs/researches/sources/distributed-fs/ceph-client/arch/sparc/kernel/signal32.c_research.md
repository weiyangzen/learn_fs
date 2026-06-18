# sources/distributed-fs/ceph-client/arch/sparc/kernel/signal32.c

Purpose: implements 32-bit compat signal handling on SPARC64, including old and RT signal frames, sigreturn paths, V8PLUS extra register state, FPU/register-window save areas, syscall restart, altstack compatibility, and siginfo ABI assertions.

Important APIs/functions: entry points are `do_sigreturn32()`, `do_rt_sigreturn32()`, `do_signal32()`, and `do_sys32_sigstack()`. Helpers include `invalid_frame_pointer()`, `get_sigframe()`, `flush_signal_insns()`, `setup_frame32()`, `setup_rt_frame32()`, `handle_signal32()`, and `syscall_restart32()`.

Control flow: sigreturn validates aligned 32-bit frame pointers, frame FP, PC/NPC alignment, restores Y/PSR-derived condition codes, G/I registers, optional V8PLUS upper halves and ASI, optional FPU and register-window state, signal mask, and altstack for RT frames, then clears syscall restart state. Signal delivery synchronizes user windows, saves/clears FPU, sizes a frame with optional FPU and saved windows, selects altstack, writes register state plus V8PLUS extras, saves FPU/windows, copies siginfo/mask/stack, copies or reconstructs the register-window save area, sets handler arguments, and installs either user restorer or a two-instruction sigreturn trampoline with explicit I-cache flush.

State and persistence: mutates current `pt_regs`, current blocked signal mask, compat altstack fields, FPU saved state, thread saved-window buffer, and user signal-frame memory. State is per-task ABI state only.

Dependencies and integration points: depends on compat signal types, `psrcompat`, `save_fpu_state()`/`restore_fpu_state()`, `save_rwin_state()`/`restore_rwin_state()`, SPARC64 register-window synchronization, page table walking for instruction flush, generic signal selection, and syscall restart conventions using `%g6`.

Risks: frame layout is userspace ABI and protected by static assertions for siginfo offsets. Manual I-cache flushing walks page tables with interrupts disabled to avoid teardown races. V8PLUS upper register reconstruction uses 32-bit indexing into 64-bit regs and is easy to regress. Bad frame validation must reliably force `SIGSEGV`.

Test signals: 32-bit compat signal and RT signal delivery, SA_SIGINFO and non-SA_SIGINFO handlers, user-provided and kernel trampolines, sigaltstack and old sigstack, syscall restart cases, V8PLUS register preservation, FPU and saved-window preservation, and malformed frame fault tests.
