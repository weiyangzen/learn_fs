# sources/distributed-fs/ceph-client/arch/powerpc/kernel/signal.h

Purpose: private signal ABI header for PowerPC signal implementation, declaring 32/64-bit handlers and providing optimized user-copy helpers for sigsets, FPR, VSX, and transactional checkpointed state.

Important APIs/types/functions: `get_sigframe()`, `handle_signal32()`, `handle_rt_signal32()`, `handle_rt_signal64()`, `__get_user_sigset()`, `unsafe_get_user_sigset`, FPR/VSX copy declarations, `unsafe_copy_fpr_to_user()`, `unsafe_copy_vsx_to_user()`, corresponding from-user macros, TM checkpoint copy macros, and `signal_fault()`.

Control flow: the header selects helper implementations by config. With VSX, FPR/VSX helpers handle split high/low VSR layouts; with only FPU registers, direct user copies are used; without FPU support, helpers become no-ops. Unsafe macros are designed for `user_access_begin()` regions in signal frame setup/restore. On non-PPC64 builds, `handle_rt_signal64()` is a stub returning `-EFAULT`.

State and persistence: no owned state, but helpers copy between user signal frames and `task_struct.thread` FP/vector/checkpoint state.

Dependencies and integration points: tightly coupled to `signal.c`, `signal_32.c`, optional `signal_64.c`, thread-state layout, ELF register counts, VSX offset definitions, transactional-memory configs, and generic uaccess unsafe APIs.

Risks: macro mistakes are hard to type-check and can corrupt user frames. One checkpointed FPR macro uses a fixed `failed` label in one access, so call sites must have that label convention. Register count/layout definitions must match the user ABI exactly for compat tasks.

Test signals: compile matrix across VSX, FPU-only, no-FPU, TM, PPC32, PPC64, and compat configurations; signal-frame preservation tests for FP/vector/VSX/TM state; fault-injection on user frame copies.
