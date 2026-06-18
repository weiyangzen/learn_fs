# sources/distributed-fs/ceph-client/arch/arm/kernel/suspend.c

Purpose: provides the C half of ARM CPU suspend/resume, coordinating idmap requirements, graph tracing, MMU context restoration, CPU bug checks, and physical save-slot allocation.

Important APIs/types/functions: `cpu_suspend`, `__cpu_suspend_save`, and early init `cpu_suspend_alloc_sp`. It calls low-level `__cpu_suspend` and resumes through `cpu_resume_mmu`/`cpu_do_resume`.

Control flow: `cpu_suspend` verifies idmap page tables on MMU systems, temporarily enables uaccess when TTBR0 PAN requires it, pauses function graph tracing, calls assembly suspend with the logical MPIDR, then on successful resume switches back to active mm, flushes branch predictor/TLB, and reruns CPU bug checks. Save helper stores physical idmap PGD, virtual SP, physical resume function, invokes CPU-specific suspend save, and cleans cache/outer cache for context and save pointer. Early allocation creates an MPIDR-hash-sized physical pointer array.

State and persistence: `sleep_save_sp.save_ptr_stash` and physical counterpart persist across suspend; saved context blocks survive low-power entry.

Dependencies and integration: `sleep.S`, idmap page tables, CPU proc suspend hooks, cache/outer cache ops, MPIDR hash, KASAN/vmap stack interactions, and bugs/errata checks.

Risks: missing cache clean loses resume context; idmap absence blocks suspend; tracing must be paused around non-returning finishers. Test signals include suspend/resume, CPU idle deep states, SMP resume, TTBR0 PAN configs, and repeated suspend loops.
