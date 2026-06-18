<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/time.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/time.h

Purpose: Declares PowerPC timebase, decrementer, clockevent, and VDSO timekeeping interfaces.

Important APIs/types/functions: timebase frequencies, decrementer globals, calibration functions, RTC and clockevent hooks, `get_tbl()`, `get_tb()`, and VDSO timebase include. Source-visible declarations include: #define __POWERPC_TIME_H; extern u64 decrementer_max;; extern unsigned long tb_ticks_per_jiffy;; extern unsigned long tb_ticks_per_usec;; extern unsigned long tb_ticks_per_sec;; extern struct clock_event_device decrementer_clockevent;; extern u64 decrementer_max;; extern void generic_calibrate_decr(void);.

Control flow: boot calibrates timebase/decrementer, timer interrupt code programs decrementer, and readers fetch TB values for clocks. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: frequency globals and boot timebase persist as calibration state. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/types.h>, #include <linux/percpu.h>, #include <asm/processor.h>, #include <asm/cpu_has_feature.h>, #include <asm/vdso/timebase.h>. Integrated with timekeeping, clocksource/clockevent, pSeries/PPC RTC, vDSO, and scheduler ticks.

Risks: timebase frequency mismatches cause clock drift and decrementer wrap/max handling is CPU-specific. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 120 lines, 2949 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/time.h -->
