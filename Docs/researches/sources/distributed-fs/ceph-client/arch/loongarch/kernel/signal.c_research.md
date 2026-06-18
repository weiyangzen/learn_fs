## sources/distributed-fs/ceph-client/arch/loongarch/kernel/signal.c

### Purpose
`signal.c` implements LoongArch signal delivery and sigreturn. It builds `rt_sigframe` records, saves/restores GPR and extended FP/LSX/LASX/LBT contexts, handles restartable syscalls around signal delivery, manages alternate stacks, and returns through the VDSO sigreturn stub.

### Important APIs, Types, And Functions
The user-visible syscall is `rt_sigreturn`; architecture entry point is `arch_do_signal_or_restart`. Internal helpers include context copy/save/restore functions for FPU, LSX, LASX, LBT, `parse_extcontext`, `setup_sigcontext`, `restore_sigcontext`, `setup_extcontext`, `get_sigframe`, `setup_rt_frame`, and `handle_signal`. Types include `struct extctx_layout`, `struct sctx_info`, `fpu_context`, `lsx_context`, `lasx_context`, and `lbt_context`.

### Control Flow
Signal delivery computes an aligned user frame, allocates extension contexts from the top downward with an end marker, writes siginfo/ucontext/sigmask, saves GPRs and live FP/SIMD/LBT state, then sets handler args in `a0..a2`, SP, RA to VDSO sigreturn, and ERA to the handler. Sigreturn validates frame access, restores blocked mask, parses extension records by magic/size, restores GPRs and optional extended state, handles pending FCSR exceptions, restores altstack, clears syscall restart flag, and returns restored `a0`.

### State, Persistence, And Dependencies
Persistent state crosses user/kernel boundary in the signal frame and thread saved contexts. The code depends on lazy FPU/SIMD/LBT ownership, user access helpers, VDSO layout, restart-block semantics, rseq signal delivery, signal stack helpers, and magic/size ABI values in `asm/sigframe.h`.

### Integration Points
Entry/exit code calls `arch_do_signal_or_restart` before returning to user mode. `lbt.S` and FPU assembly helpers perform hardware context transfer. `process.c` initializes thread FP/LBT state, and `traps.c` sets `thread.error_code` for address-error signal flags.

### Risks
Signal frame layout is ABI-sensitive. Extension parsing accepts records in user memory and must reject bad magic/size to avoid walking arbitrary memory. Lazy FP/SIMD/LBT save/restore is protected by preemption and pagefault disabling; mistakes can lose hardware state. `fcsr_pending` may force SIGFPE during sigreturn if handlers set enabled exception bits. Restart PC adjustment assumes 4-byte syscall instruction size.

### Test Signals
Run signal ABI tests for basic delivery, altstack overflow, sigreturn corruption, syscall restart variants, rseq, FP/LSX/LASX/LBT live contexts, pending FCSR exceptions, and 16-byte stack alignment. Compare signal-frame contents against ptrace/core dump register state.
