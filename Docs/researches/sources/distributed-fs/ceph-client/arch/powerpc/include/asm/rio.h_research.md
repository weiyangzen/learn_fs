<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rio.h

Purpose: Provides the Freescale RapidIO machine-check hook surface.

Important APIs/types/functions: `fsl_rio_mcheck_exception(struct pt_regs *)`, compiled as a real declaration only when `CONFIG_FSL_RIO` is enabled. Source-visible declarations include: #define ASM_PPC_RIO_H; extern int fsl_rio_mcheck_exception(struct pt_regs *);; static inline int fsl_rio_mcheck_exception(struct pt_regs *regs) {return 0; }.

Control flow: machine-check handling can delegate RapidIO faults to this hook and otherwise gets a zero-return stub. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: no state in the header; platform RapidIO code owns any error registers. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with PowerPC exception handling and Freescale RapidIO platform support.

Risks: the stub must preserve non-RIO builds while real handlers must classify machine checks without hiding unrelated CPU errors. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 18 lines, 424 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rio.h -->
