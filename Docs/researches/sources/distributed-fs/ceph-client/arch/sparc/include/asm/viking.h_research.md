# sources/distributed-fs/ceph-client/arch/sparc/include/asm/viking.h

Purpose: Viking/MXCC CPU header defining control bits, cache/tag constants, and inline ASI helpers for I/D cache flush, branch prediction, MXCC parity, and hardware probe support.

Important APIs/types/functions: functions/helpers `viking_flush_icache`, `viking_flush_dcache`, `viking_unlock_icache`, `viking_unlock_dcache`, `viking_set_bpreg`, `viking_get_bpreg`, `viking_get_dcache_ptag`, `viking_mxcc_turn_off_parity`, `viking_hwprobe`; macros/constants `_SPARC_VIKING_H`, `VIKING_MMUENABLE`, `VIKING_NOFAULT`, `VIKING_PSO`, `VIKING_DCENABLE`, `VIKING_ICENABLE`, `VIKING_SBENABLE`, `VIKING_MMODE`, `VIKING_PCENABLE`, `VIKING_BMODE`, `VIKING_SPENABLE`, `VIKING_ACENABLE`, `VIKING_TCENABLE`, `VIKING_DPENABLE`, `VIKING_ACTION_MIX`, `VIKING_PTAG_VALID`, `VIKING_PTAG_DIRTY`, `VIKING_PTAG_SHARED`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_VIKING_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is Viking control/cache/tag/MXCC registers and cache contents manipulated through ASI operations.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`, `asm/mxcc.h`, `asm/pgtable.h`, `asm/pgtsrmmu.h`. Integration points include memory-management, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, MMU/TLB encoding regressions. Test signals: Viking boot, cache flush correctness, MXCC parity behavior, hardware probe identification, and SRMMU mapping interactions should be tested.
