# sources/distributed-fs/ceph-client/arch/arm64/kernel/signal.c

Purpose: this file implements native AArch64 signal delivery and `rt_sigreturn`. It builds and parses extensible user signal frames containing GPRs, sigmask, altstack, FPSIMD, ESR, SVE/SME, TPIDR2, ZA/ ZT, FPMR, POE, and GCS contexts, and coordinates syscall restart behavior.

Important APIs and state: key structures are `rt_sigframe`, `rt_sigframe_user_layout`, `user_access_state`, and `user_ctxs`. Public entry points include `SYSCALL_DEFINE0(rt_sigreturn)`, `arch_do_signal_or_restart()`, and `minsigstksz_setup()`. Important helpers include `setup_sigframe_layout()`, `setup_sigframe()`, `get_sigframe()`, `setup_return()`, `setup_rt_frame()`, `parse_user_sigframe()`, `restore_sigframe()`, and per-feature preserve/restore helpers.

Control flow: delivery saves/flushed FP state, computes a 16-byte-aligned frame and optional record layout, temporarily resets POE restrictions so kernel uaccess can build the frame, writes user context records, optionally copies siginfo, pushes GCS signal tokens, then updates pt_regs to enter the handler with correct arguments, SP, FP/LR, PC, BTI BTYPE, TCO clear, and SME streaming/ZA disabled. Return validates SP alignment and access, restores sigmask and GPRs, parses the context chain including `extra_context`, restores feature state in dependency order, validates GCS signal cap token, restores altstack and user-access state, and returns the restored x0.

State and persistence: signal frames persist in user memory and are ABI. The kernel also updates current task FP/SVE/SME/GCS/POE/FPMR/TLS state. `signal_minsigstksz` is computed from the largest supported frame layout after cpufeatures are known.

Dependencies and integration: integrates with generic signal, compat signal32, rseq, syscall restart, ptrace register validation, VDSO sigtramp, FPSIMD/SVE/SME, GCS, POE/pkeys, BTI, MTE TCO, and altstack handling.

Risks: signal frames are security-sensitive user input on sigreturn; duplicate/unknown/misaligned records are rejected. Feature restore order matters, e.g. ZA before ZT and GCS cap validation after context restore. Once `setup_return()` mutates registers, later failures must be avoided. Frame growth is capped by `SIGFRAME_MAXSZ`.

Test signals: signal ABI selftests for SVE/SME/ZA/ ZT/FPMR/POE/GCS, invalid sigreturn frames, altstack, syscall restart, single-step into handlers, BTI-protected handlers, and `AT_MINSIGSTKSZ` sizing.
