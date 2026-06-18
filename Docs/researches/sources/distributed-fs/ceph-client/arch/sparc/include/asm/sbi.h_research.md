# sources/distributed-fs/ceph-client/arch/sparc/include/asm/sbi.h

Purpose: Sun4d SBI bus interface header defining SBI register layout, device-id mapping, interrupt target bits, and helpers to acquire/release/configure SBI controller registers.

Important APIs/types/functions: types `sbi_regs`; functions/helpers `acquire_sbi`, `release_sbi`, `set_sbi_tid`, `get_sbi_ctl`, `set_sbi_ctl`; macros/constants `_SPARC_SBI_H`, `SBI_CID`, `SBI_CTL`, `SBI_STATUS`, `SBI_CFG0`, `SBI_CFG1`, `SBI_CFG2`, `SBI_CFG3`, `SBI_STB0`, `SBI_STB1`, `SBI_STB2`, `SBI_STB3`, `SBI_INTR_STATE`, `SBI_INTR_TID`, `SBI_INTR_DIAG`, `SBI_CFG_BURST_MASK`, `SBI2DEVID`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_SBI_H`, `__ASSEMBLER__`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State is memory-mapped SBI registers and interrupt target/control fields, usually accessed through OBIO mappings.

Dependencies and integration points: Includes/dependencies: `asm/obio.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: sun4d interrupt routing, bus acquisition/release, CPU target programming, and register endian/offset checks are key tests.
