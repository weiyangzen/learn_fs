# sources/distributed-fs/ceph-client/arch/arm64/mm/gcs.c

Purpose: implements ARM64 Guarded Control Stack user shadow-stack allocation, syscall mapping, per-task mode programming, cleanup, and prctl-style status/lock operations.

Important APIs/types/functions: `alloc_gcs`, `gcs_size`, `gcs_alloc_thread_stack`, `SYSCALL_DEFINE3(map_shadow_stack)`, `gcs_set_el0_mode`, `gcs_free`, `arch_set_shadow_stack_status`, `arch_get_shadow_stack_status`, and `arch_lock_shadow_stack_status`.

Control flow: thread clone allocation checks system support and task mode, preserves current GCSPR for vfork/non-VM-sharing clones, otherwise allocates a shadow stack sized from clone stack size or defaults. `map_shadow_stack` validates flags, alignment, and overflow, maps shadow-stack VM memory, optionally writes a cap token and marker near the end, and orders it with `gcsb_dsync`. Status setting validates support, compat mode, unknown bits, and locked bits, allocates a stack on first enable for current task, writes GCSPR_EL0, stores mode flags, and programs GCSCRE0_EL1 for enable/write/push permissions.

State and persistence: stores per-task `gcs_base`, `gcs_size`, `gcspr_el0`, `gcs_el0_mode`, and locked flags, and maps/unmaps shadow-stack VMAs. No disk persistence.

Dependencies/integration: ARM64 GCS CPU feature, `vm_mmap_shadow_stack`, `vm_munmap`, clone/prctl/syscall paths, user access helpers for cap token writes, system registers `SYS_GCSPR_EL0` and `SYS_GCSCRE0_EL1`, and compat-thread checks.

Risks: re-enabling after disable is intentionally rejected when old stack state remains. Token placement must avoid overflow and wrong address writes. Only current task can allocate on enable, so remote task changes can return `-EBUSY`. Compat tasks are unsupported. Freeing requires the task mm to match current mm.

Test signals: `map_shadow_stack` flag/alignment/overflow validation, cap token and marker placement, first enable allocation, disable/re-enable rejection, clone with CLONE_VM vs vfork behavior, locked status bits, compat rejection, GCS fault handling integration, and cleanup on thread exit.
