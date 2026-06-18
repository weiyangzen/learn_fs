# sources/distributed-fs/ceph-client/arch/sparc/include/asm/timer_64.h

Purpose: sparc64 tick/stick timer header with tick compare bits, HyperSparc stick addresses, tick operation vector, patch descriptors, and inline `get_tick()`.

Important APIs/types/functions: types `sparc64_tick_ops`, `get_tick_patch`; functions/helpers `sparc64_get_clock_tick`, `setup_sparc64_timer`, `get_tick`; macros/constants `_SPARC64_TIMER_H`, `TICK_PRIV_BIT`, `TICKCMP_IRQ_BIT`, `HBIRD_STICKCMP_ADDR`, `HBIRD_STICK_ADDR`, `GET_TICK_NINSTR`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_TIMER_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, timekeeping paths rather than through standalone functions.

State and persistence behavior: State is architectural `%tick`/`%stick`/compare registers and the selected `sparc64_tick_ops` implementation patched during timer setup.

Dependencies and integration points: Includes/dependencies: `uapi/asm/asi.h`, `linux/types.h`, `linux/init.h`. Integration points include memory-management, timekeeping; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, ABI compatibility breaks. Test signals: Clocksource reads, timer interrupt compare programming, sun4v/hummingbird variants, and instruction patching are tests.
