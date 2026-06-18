# sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil_64.c

Purpose: supports sparc64 signal-frame save and restore for floating-point/vector-visible FPU state and register-window spill buffers.

Important APIs/types/functions: `save_fpu_state()`, `restore_fpu_state()`, `save_rwin_state()`, and `restore_rwin_state()` operate on `__siginfo_fpu_t`, `__siginfo_rwin_t`, `pt_regs`, `thread_info->fpregs`, `fpsaved`, `xfsr`, `gsr`, `reg_window`, and `rwbuf_stkptrs`.

Control flow: signal delivery copies only the lower and/or upper FP register halves indicated by `FPRS_DL`/`FPRS_DU`, then stores FSR, GSR, and FPRS. Signal return validates 8-byte alignment, disables live FPU ownership with `fprs_write(0)`, clears `TSTATE_PEF`, copies requested register halves back, and marks the saved FPRS bits. Register windows are copied by `wsaved` count and then forced back to user stack via `set_thread_wsaved()` and `synchronize_user_stack()`.

State and persistence: all state is per-current-thread architectural context; no filesystem persistence exists. Bad user pointers or still-unsynchronized windows produce `-EFAULT`.

Dependencies and integration points: depends on sparc64 signal layout, `thread_info`, user-copy helpers, FPU macros, register-window stack synchronization, and signal return code.

Risks: alignment and `wsaved <= NSWINS` checks protect ABI parsing. Partial FP saves must match FPRS bits or signal frames expose stale/corrupt state. Register-window restore is fragile because unsynchronized windows indicate user stack failure.

Test signals: signal delivery/return across FP users, vector/GSR users, alternate stacks, invalid/misaligned signal frames, forced register-window spills, and faults during user copies.
