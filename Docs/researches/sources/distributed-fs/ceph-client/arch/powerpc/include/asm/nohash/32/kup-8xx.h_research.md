# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/kup-8xx.h

Purpose: implements 8xx kernel user access protection (KUAP) helpers using the MD_AP special-purpose register.

Important APIs/types/functions: when `CONFIG_PPC_KUAP` is enabled, helpers include `__kuap_save_and_lock`, `kuap_user_restore`, `__kuap_kernel_restore`, optional debug `__kuap_get_and_assert_locked`, `uaccess_begin_8xx`, `uaccess_end_8xx`, `allow_user_access`, `prevent_user_access`, `prevent_user_access_return`, `restore_user_access`, and `__bad_kuap_fault`.

Control flow: exception entry saves current MD_AP and locks user access; explicit uaccess windows write MD_AP to allow or prevent access; fault handling checks saved KUAP bits to classify protection faults.

State and persistence: KUAP state is the hardware `SPRN_MD_AP` register plus saved `regs->kuap` in exception frames.

Dependencies and integration points: depends on bug/WARN helpers, MMU feature patching, `asm/reg.h`, 8xx MD_AP constants, and user access/fault code.

Risks: incorrect MD_AP writes can leave user memory accessible in kernel or block legitimate copy_to/from_user. Debug assertions only check upper access-protection bits. Inline assembly is patched by MMU feature bits and must match register constraints.

Test signals: KUAP selftests, copy_to/from_user under enabled/disabled windows, bad user access fault tests, debug assertion coverage, and 8xx builds without KUAP.
