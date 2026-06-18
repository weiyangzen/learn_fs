# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mmu.h

Purpose: defines PowerPC MMU feature bits, CPU-specific feature sets, page-size indexes, runtime feature checks, radix/hash selection helpers, and top-level MMU initialization hooks.

Important APIs/types/functions: feature bits include MMU family bits (`MMU_FTR_HPTE_TABLE`, 8xx, 44x, FSL_E, 47x, radix) and capabilities such as KUAP, KUEP, pkeys, GTSE, 68-bit VA, kernel RO, TLBIE variants, large pages, CI large pages, 1T segments, and NX DSI. `MMU_FTRS_POSSIBLE`, `MMU_FTRS_ALWAYS`, `early_mmu_has_feature`, `mmu_has_feature`, `mmu_clear_feature`, `radix_enabled`, `early_radix_enabled`, strict RWX helpers, page-size constants, and MMU init/cleanup declarations are central.

Control flow: early boot uses CPU specs and compile-time masks for feature detection. With jump-label feature checks, `mmu_has_feature()` becomes a static-branch lookup after initialization and falls back to early checks before that. Runtime code branches between radix and hash behavior with `radix_enabled()`.

State and persistence: active MMU feature state lives in `cur_cpu_spec->mmu_features` and optional `mmu_feature_keys[]`. PPC64 RMA size and partition table entries persist in platform MMU state. Page-size indexes are compile-time ABI within low-level handlers.

Dependencies and integration points: integrates CPU feature tables, jump labels, page table headers, Book3S 64 MMU, Book3S 32 hash MMU, nohash MMUs, kexec cleanup, partition table setup, and strict kernel/module RWX policy.

Risks: feature masks must match Kconfig and CPU specs; wrong `MMU_FTRS_ALWAYS` can remove needed runtime checks. Jump-label checks require constant single-bit arguments. Page-size indexes are used by assembly and must remain stable.

Test signals: boot hash, radix, 8xx, 44x, FSL BookE, and Book3S 32 configs; verify feature keys initialize; run TLB shootdown, hugepage, pkeys, KUAP/KUEP, strict RWX, and kexec MMU cleanup tests.
