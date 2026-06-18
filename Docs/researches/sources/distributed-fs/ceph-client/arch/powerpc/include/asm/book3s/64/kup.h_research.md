# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/kup.h

Purpose: implements 64-bit Book3S Kernel User Access/Execute Protection using AMR/IAMR registers and PowerPC protection-key features.

Important APIs/types/functions: defines `AMR_KUAP_BLOCK_READ`, `AMR_KUAP_BLOCK_WRITE`, `AMR_KUEP_BLOCKED`, `AMR_KUAP_BLOCKED`, assembly macros `kuap_user_restore`, `kuap_kernel_restore`, `kuap_check_amr`, `kuap_save_amr_and_lock`, static key `uaccess_flush_key`, defaults `default_uamor/default_amr/default_iamr`, and C helpers for AMR/IAMR restore, `get_kuap()`, `set_kuap()`, `allow_user_access()`, `prevent_user_access()`, `prevent_user_access_return()`, and `restore_user_access()`.

Control flow: exception entry assembly saves AMR/IAMR and blocks user access depending on pkey/KUAP/KUEP features and whether the exception came from user or kernel. C uaccess helpers build an AMR value for read, write, or read/write access and use `isync; mtspr; isync` around AMR writes.

State and persistence: state is in AMR/IAMR SPRs, saved `pt_regs` fields, per-thread user AMR/IAMR, and read-only default register values. Optional flushing is controlled by `uaccess_flush_key`.

Dependencies and integration points: depends on SPR definitions, MMU feature tests, pkeys, ptrace registers, exception entry stack offsets, and uaccess flushing. It integrates with all kernel user-memory access on Book3S64.

Risks: missing context synchronization around AMR writes can expose user memory or create spurious faults. Non-nesting design means callers must pair allow/prevent carefully. Debug checks depend on `CONFIG_PPC_KUAP_DEBUG`.

Test signals: KUAP/KUEP debug builds, uaccess copy tests, pkey tests, interrupt entry/return tests from user and kernel, fault injection for blocked access, and static-key flush path tests.
