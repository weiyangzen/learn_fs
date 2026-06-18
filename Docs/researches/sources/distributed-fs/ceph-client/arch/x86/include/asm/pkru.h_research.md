# sources/distributed-fs/ceph-client/arch/x86/include/asm/pkru.h

Purpose: provides low-level helpers for reading, writing, and interpreting the x86 PKRU register used by memory protection keys.

Important APIs, types, and functions: defines `PKRU_AD_BIT`, `PKRU_WD_BIT`, `PKRU_BITS_PER_PKEY`, `init_pkru_value`, `pkru_get_init_value()`, `__pkru_allows_read()`, `__pkru_allows_write()`, `read_pkru()`, `write_pkru()`, and `pkru_write_default()`.

Control flow: read/write helpers check `X86_FEATURE_OSPKE` before executing `rdpkru`/`wrpkru`. `write_pkru()` avoids an expensive `wrpkru` if the requested value already matches. Permission helpers shift AD/WD bits by `pkey * 2`; write access requires neither access-disable nor write-disable.

State and persistence: PKRU is per-logical-processor architectural state saved/restored by context-switch/FPU paths. `init_pkru_value` is global runtime policy when pkeys are enabled.

Dependencies and integration points: depends on CPU feature detection, pkey allocation/access checks in `pgtable.h`, task state management, and user PKRU instructions.

Risks: WRPKRU changes userspace access rights and must only be executed when supported. Stale or wrong default PKRU can grant or deny access after exec/fork/signal paths. Permission helpers assume pkey values are already range-validated.

Test signals: pkeys selftests, direct `rdpkru`/`wrpkru` behavior, context-switch PKRU preservation, default PKRU after exec, OSPKE-disabled builds, and page-fault access checks for read/write-disabled pkeys.
