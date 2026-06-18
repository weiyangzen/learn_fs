# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/kup.h

Purpose: implements 32-bit Book3S Kernel User Access Protection (KUAP) using segment register supervisor-key bits.

Important APIs/types/functions: defines `KUAP_NONE`, `kuap_lock_one()`, `kuap_unlock_one()`, `uaccess_begin_32s()`, `uaccess_end_32s()`, `__kuap_save_and_lock()`, `kuap_user_restore()`, `__kuap_kernel_restore()`, `__kuap_get_and_assert_locked()`, `allow_user_access()`, `prevent_user_access()`, `prevent_user_access_return()`, `restore_user_access()`, and `__bad_kuap_fault()`.

Control flow: access enable/disable paths are compile-time gated on `CONFIG_PPC_KUAP` and runtime-patched by `MMU_FTR_KUAP`. Write access records one unlocked user segment in `current->thread.kuap`, clears or sets `SR_KS` through `mtsr/mtsrin`, and uses `isync` after segment updates.

State and persistence: per-thread KUAP state is in `current->thread.kuap` and saved/restored through `pt_regs->kuap` on exceptions. Hardware state is in segment registers.

Dependencies and integration points: depends on Book3S 32 hash segment definitions, `current`, `pt_regs`, `fix_alignment()`, `regs_add_return_ip()`, and single-step emulation. It integrates with uaccess, exceptions, and page-fault diagnostics.

Risks: only write access is controlled here. Unaligned writes crossing segments require special fault handling; incorrect restore can leave user memory writable from kernel. Debug assertions are config-dependent.

Test signals: KUAP debug builds, uaccess copy tests, exception-entry/return tests, unaligned store fault tests crossing segment boundaries, and fault injection for missing `allow_user_access()`.
