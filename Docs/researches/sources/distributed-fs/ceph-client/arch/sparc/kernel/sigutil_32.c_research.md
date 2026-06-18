# sources/distributed-fs/ceph-client/arch/sparc/kernel/sigutil_32.c

Purpose: implements SPARC32 signal helper routines that serialize/restore FPU state and buffered register windows for signal frames.

Important APIs/functions: implements `save_fpu_state()`, `restore_fpu_state()`, `save_rwin_state()`, and `restore_rwin_state()`. It uses external FPU save logic through `fpsave()` and shared state such as `last_task_used_math` or `TIF_USEDFPU`.

Control flow: `save_fpu_state()` forces FPU state into `current->thread`, clears live FPU ownership, copies float registers/FSR/queue depth and optional queue entries to user memory, then clears used-math state. `restore_fpu_state()` validates alignment/access, clears live FPU ownership, marks used-math, copies registers/FSR/queue depth and optional queue entries back into the thread. `save_rwin_state()` copies each buffered register window and stack pointer to the user side buffer. `restore_rwin_state()` validates count, copies windows and stack pointers back, sets `w_saved`, then calls `synchronize_user_stack()` and fails if any windows remain buffered.

State and persistence: mutates current FPU ownership flags, `thread.float_regs`, `thread.fsr`, `thread.fpqueue`, `thread.fpqdepth`, used-math state, `thread_info.reg_window`, `rwbuf_stkptrs`, and `w_saved`. User signal-frame buffers receive serialized state.

Dependencies and integration points: used by SPARC32 signal setup/return, depends on SMP versus UP FPU ownership conventions, `access_ok()`, user copy helpers, `NSWINS`, and register-window synchronization.

Risks: FPU ownership differs for SMP and UP and must clear PSR_EF/TIF state consistently. Register-window restore accepts user-provided saved windows and must bound `wsaved` to `NSWINS`. A restored window set that cannot be synchronized back to user stack is treated as `-EFAULT`.

Test signals: signal delivery to FPU-using tasks, restore of FPU queue state, SMP and UP FPU ownership transitions, signals with saved register windows, invalid FPU/window buffer alignment, overlarge `wsaved`, and faulting user copies.
