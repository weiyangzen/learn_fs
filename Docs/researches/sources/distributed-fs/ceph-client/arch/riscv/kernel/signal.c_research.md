<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/signal.c

Purpose: Implements RISC-V signal delivery and `rt_sigreturn`, including FP, vector, and Zicfiss shadow-stack extension records in the user signal frame.

Important APIs/types/functions: Defines `struct rt_sigframe`, FP save/restore helpers, vector and CFI extension save/restore helpers, `restore_sigcontext()`, `get_rt_frame_size()`, `SYSCALL_DEFINE0(rt_sigreturn)`, `setup_sigcontext()`, `setup_rt_frame()`, `handle_signal()`, `arch_do_signal_or_restart()`, `init_rt_signal_env()`, and `sigaltstack_size_valid()`.

Control flow: Signal setup chooses a frame location, copies siginfo/ucontext/mask, saves scalar registers plus optional FP/vector/shadow-stack records, points RA to vDSO `rt_sigreturn`, and redirects EPC to the handler. `rt_sigreturn` validates frame size, restores mask, registers, FP/vector/CFI state, altstack, and returns the restored `a0`. Syscall restart handling rewinds EPC before delivery and finalizes restart/no-restart on return to user mode.

State and persistence: Per-task state touched includes blocked signal mask, pt_regs, FP state, vector datap, active shadow-stack pointer, altstack, and restart block. Read-mostly sizes `riscv_v_sc_size`, `riscv_zicfiss_sc_size`, and `signal_minsigstksz` are initialized at boot.

Dependencies and integration points: Couples generic signal code with vDSO, vector context management, FP save/restore, user CFI shadow stacks, compat signal handling, and syscall restart ABI.

Risks: Signal frame extension parsing is ABI-critical; wrong magic/size validation can corrupt user state or leak kernel data. Shadow-stack token save/restore failures turn into bad frames. Dynamic vector length changes are unsupported and reflected in fixed frame sizing.

Test signals: Signal delivery/return with FP, vector, Zicfiss shadow stacks, altstack minimum sizing, syscall restart under ptrace, malformed frame fuzzing, compat signal frames, and no-MMU sigreturn code flushing.

Source read size: 589 lines, 16802 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/signal.c -->
