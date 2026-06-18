# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/smemc.h

Purpose: PXA static memory controller register map and bit definitions.

Important APIs/types/functions: defines physical bases `PXA2XX_SMEMC_BASE`, `PXA3XX_SMEMC_BASE`, virtual base `SMEMC_VIRT`, register macros for SDRAM, static memory, PCMCIA, synchronous memory, memory clock, and chip-select address registers, plus bit definitions such as `MECR_NOS`, `MDCNFG_DE*`, and `MDREFR_*`.

Control flow: no functions; included by low-level C and assembly that read/write SMEMC registers.

State and persistence: names MMIO registers whose contents determine memory timing, refresh, self-refresh, PCMCIA timings, and chip-select address layout.

Dependencies and integration points: used by `smemc.c`, `sleep.S`, board files that touch `MSC0`, and PXA map code that creates the fixed virtual mapping.

Risks: macro addresses are raw hardware ABI. Any mismatch between virtual mapping and macro definitions causes bad MMIO access. Assembly inclusion constrains syntax and type usage.

Test signals: compile tests for C and assembly users, boot memory controller access, and suspend/resume memory integrity.
