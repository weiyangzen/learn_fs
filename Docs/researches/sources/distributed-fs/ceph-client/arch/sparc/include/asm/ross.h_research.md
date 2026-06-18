# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ross.h

Purpose: Ross/hyperSPARC CPU control and cache helper header defining ICR bits and inline ASI sequences for I-cache/D-cache/tag/cache-page operations.

Important APIs/types/functions: functions/helpers `get_ross_icr`, `put_ross_icr`, `hyper_flush_whole_icache`, `hyper_clear_all_tags`, `hyper_flush_unconditional_combined`, `hyper_flush_cache_user`, `hyper_flush_cache_page`; macros/constants `_SPARC_ROSS_H`, `HYPERSPARC_CWENABLE`, `HYPERSPARC_SBENABLE`, `HYPERSPARC_WBENABLE`, `HYPERSPARC_MIDMASK`, `HYPERSPARC_BMODE`, `HYPERSPARC_ACENABLE`, `HYPERSPARC_CSIZE`, `HYPERSPARC_MRFLCT`, `HYPERSPARC_CMODE`, `HYPERSPARC_CENABLE`, `HYPERSPARC_NFAULT`, `HYPERSPARC_MENABLE`, `HYPERSPARC_ICCR_FTD`, `HYPERSPARC_ICCR_ICE`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_ROSS_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is CPU cache-control/tag registers and cache contents; helpers invalidate or flush physical cache structures through alternate spaces.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`, `asm/page.h`. Integration points include memory-management, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: hyperSPARC boot, cache flush correctness, copy-on-write aliasing, and cache-control register programming are the test signals.
