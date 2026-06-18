# sources/distributed-fs/ceph-client/arch/arm/kernel/sleep.S

Purpose: implements low-level CPU suspend and resume assembly, preserving register state, indexing per-CPU save slots by MPIDR hash, restoring MMU state, and re-entering virtual kernel execution.

Important APIs/types/functions: `__cpu_suspend`, `cpu_resume`, `cpu_resume_arm`, `cpu_resume_mmu`, optional `cpu_resume_no_hyp`, and data object `sleep_save_sp`. Macro `compute_mpidr_hash` mirrors the C MPIDR hash algorithm.

Control flow: suspend saves callee registers, optionally switches to overflow stack, allocates CPU-specific save space, stores suspend function/argument, hashes MPIDR to select a save pointer slot, calls `__cpu_suspend_save`, then calls the platform finisher. Resume installs HYP stub if needed, enters SVC, hashes MPIDR, loads saved physical PGD/SP/resume function, enables MMU, calls `cpu_init`, unpoisons KASAN stack, and returns zero.

State and persistence: save slots under `sleep_save_sp` hold physical pointers to CPU context blocks across low-power states.

Dependencies and integration: C companion `suspend.c`, CPU proc sleep hooks, MPIDR hash from setup, idmap page tables, HYP stub, KASAN/vmap stack, and cache/TLB maintenance.

Risks: MPIDR hash mismatch resumes on wrong stack; MMU/idmap assumptions are strict; cache cleaning must make save data visible with MMU off. Test signals include suspend/resume on SMP, vmap stack/KASAN configs, HYP boot modes, and CPU hotplug/resume loops.
