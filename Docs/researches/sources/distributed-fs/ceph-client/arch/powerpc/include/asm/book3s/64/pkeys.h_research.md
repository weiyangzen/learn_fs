# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/pkeys.h

Purpose: exposes Book3S64 memory protection key conversion helpers for page-table code.

Important APIs/types/functions: includes hash pkey support and defines `vmflag_to_pte_pkey_bits()` plus `pte_to_pkey_bits()` style helpers that return no pkey bits when `MMU_FTR_PKEY` is absent and currently BUG for radix pkey conversion in the visible path.

Control flow: inline helpers first test `mmu_has_feature(MMU_FTR_PKEY)`, then route to hash helpers when hash mode is active.

State and persistence: pkey allocation state lives in `mm_context_t`; this header only maps it to/from PTE bits.

Dependencies and integration points: depends on `hash-pkey.h`, MMU feature detection, radix/hash mode checks, and VM flags. It integrates with `mprotect`, `pkey_mprotect`, PTE construction, and access checks.

Risks: radix pkey behavior must not accidentally enter hash-only helpers. Incorrect bit extraction can break isolation by granting or denying access.

Test signals: pkey selftests on hash systems, build checks with and without `CONFIG_PPC_MEM_KEYS`, and negative coverage for unsupported radix pkey paths.
