# sources/distributed-fs/ceph-client/arch/x86/include/asm/uaccess_64.h

Purpose: 64-bit x86 raw user-copy, address-validation, tagged-address masking, and clear-user implementation.

Important APIs/types/functions: `USER_PTR_MAX`, `__untagged_addr()`, `untagged_addr()`, `untagged_addr_remote()`, `valid_user_address()`, `mask_user_address()`, `masked_user_access_begin()`, `__access_ok()`, `rep_movs_alternative()`, `copy_user_generic()`, `raw_copy_from_user()`, `raw_copy_to_user()`, `copy_to_nontemporal()`, `copy_user_flushcache()`, `copy_from_user_inatomic_nontemporal()`, `copy_from_user_flushcache()`, `rep_stos_alternative()`, `__clear_user()`, and `clear_user()`.

Control flow: access checks compare pointers/ranges against runtime-constant `USER_PTR_MAX`, with special handling for small constant sizes. LAM-enabled builds mask tag bits via alternative instructions and per-CPU `tlbstate_untag_mask`. Copies open SMAP, execute `rep movsb` or call `rep_movs_alternative` if FSRM is absent, and use exception-table fixups to return residual length. Clear-user similarly uses `rep stosb` or an alternative routine.

State/persistence: reads runtime constants, per-CPU tag masks, CPU feature alternatives, and KASAN instrumentation state. It does not persist data beyond destination writes and residual return values.

Dependencies/integration: depends on lockdep, KASAN, alternatives, cpufeatures, page/percpu, runtime constants, SMAP, exception tables, and cache-flush/nontemporal copy implementations. Integrated by generic copy_to/from_user and memory-management code.

Risks/test signals: risks include range overflow, incorrect LAM/tag masking, missing SMAP close on exception, wrong residual count, and cache/nontemporal copy corruption. Test x86_64 usercopy, LAM/address masking, KASAN, FSRM/FSRS alternatives, machine-check tolerant copy users, page-boundary faults, and `clear_user` partial fault behavior.
