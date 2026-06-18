# sources/distributed-fs/ceph-client/arch/sparc/include/asm/upa.h

Purpose: SPARC architecture header `upa.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: functions/helpers `_upa_readb`, `_upa_readw`, `_upa_readl`, `_upa_readq`, `_upa_writeb`, `_upa_writew`, `_upa_writel`, `_upa_writeq`; macros/constants `_SPARC64_UPA_H`, `UPA_CONFIG_RESV`, `UPA_CONFIG_PCON`, `UPA_CONFIG_MID`, `UPA_CONFIG_PCAP`, `UPA_PORTID_FNP`, `UPA_PORTID_RESV`, `UPA_PORTID_ECCVALID`, `UPA_PORTID_ONEREAD`, `UPA_PORTID_PINTRDQ`, `UPA_PORTID_PREQDQ`, `UPA_PORTID_PREQRD`, `UPA_PORTID_UPACAP`, `UPA_PORTID_ID`, `upa_readb`, `upa_readw`, `upa_readl`, `upa_readq`, plus 4 more.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_UPA_H`, `defined(__KERNEL__) && !defined(__ASSEMBLER__)`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is inline assembly.

Dependencies and integration points: Includes/dependencies: `asm/asi.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes, configuration-specific build gaps. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
