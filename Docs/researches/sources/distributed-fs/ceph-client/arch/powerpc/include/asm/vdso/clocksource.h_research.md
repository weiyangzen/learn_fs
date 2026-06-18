<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/clocksource.h

Purpose: Selects the PowerPC vDSO architecture clock mode.

Important APIs/types/functions: `VDSO_ARCH_CLOCKMODES` set to `VDSO_CLOCKMODE_ARCHTIMER`. Source-visible declarations include: #define _ASM_POWERPC_VDSO_CLOCKSOURCE_H; #define VDSO_ARCH_CLOCKMODES VDSO_CLOCKMODE_ARCHTIMER.

Control flow: generic vDSO time code uses this macro to decide supported fast clocksource modes. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: clocksource selection persists in vDSO data/config. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are no direct includes. Integrated with generic vDSO timekeeping and PowerPC timebase clocksource.

Risks: the selected mode must match the implementation used by PowerPC vDSO timebase reads. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 7 lines, 182 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/vdso/clocksource.h -->
