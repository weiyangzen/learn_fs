<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/runlatch.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/runlatch.h

Purpose: Wraps POWER run-latch control for 64-bit kernels.

Important APIs/types/functions: `ppc64_runlatch_on()` and `ppc64_runlatch_off()` macros around low-level run-latch assembly helpers and MSR tracking. Source-visible declarations include: #define _ASM_POWERPC_RUNLATCH_H; extern void __ppc64_runlatch_on(void);; extern void __ppc64_runlatch_off(void);; #define ppc64_runlatch_off() \; #define ppc64_runlatch_on() \; #define ppc64_runlatch_on(); #define ppc64_runlatch_off().

Control flow: scheduler and idle paths toggle the latch only when thread state says the hardware bit needs changing. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: state is per-thread/per-CPU hardware run-latch status, not stored here. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with PowerPC64 idle, scheduler, and performance/power-management code.

Risks: incorrect toggling wastes power or hurts performance and 32-bit/no-runlatch builds must remain no-ops. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 44 lines, 1180 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/runlatch.h -->
