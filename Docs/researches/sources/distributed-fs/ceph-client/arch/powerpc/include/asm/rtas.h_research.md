<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas.h

Purpose: Main kernel interface for Run-Time Abstraction Services on CHRP and pSeries PowerPC systems.

Important APIs/types/functions: RTAS function handles/tokens, status constants, `rtas_call()`, unlocked call variants, busy-delay helpers, error-log helpers, flash/NVRAM/power/sensor/indicator APIs, syscall controls, and global RTAS state. Source-visible declarations include: #define _POWERPC_RTAS_H; enum rtas_function_index {; typedef struct {; #define rtas_fn_handle(x_) ((const rtas_fn_handle_t) { .index = x_, }); #define RTAS_FN_CHECK_EXCEPTION rtas_fn_handle(RTAS_FNIDX__CHECK_EXCEPTION); #define RTAS_FN_DISPLAY_CHARACTER rtas_fn_handle(RTAS_FNIDX__DISPLAY_CHARACTER); #define RTAS_FN_EVENT_SCAN rtas_fn_handle(RTAS_FNIDX__EVENT_SCAN); #define RTAS_FN_FREEZE_TIME_BASE rtas_fn_handle(RTAS_FNIDX__FREEZE_TIME_BASE).

Control flow: client code resolves firmware tokens, builds argument counts and outputs, serializes through RTAS locking when required, handles busy/extended delay statuses, and consumes firmware return words. As a header, executable flow is mostly in inline helpers, macros, or implementation files that consume these declarations.

State and persistence: global RTAS metadata, lock state, reserved user region, event logs, and firmware tokens persist after early discovery. Header-defined constants and layouts shape persistent kernel, firmware, hardware, or user ABI state even when this file owns no storage.

Dependencies and integration points: Direct includes are #include <linux/mutex.h>, #include <linux/spinlock.h>, #include <asm/page.h>, #include <asm/rtas-types.h>, #include <linux/time.h>, #include <linux/cpumask.h>. Integrated with pSeries platform setup, XICS, PCI config, NVRAM, RTC, reboot/poweroff, firmware flash, hotplug, event scan, and user `sys_rtas`.

Risks: firmware return codes are not Linux errno, calls may need retry delays, and argument/work-area layout mistakes can corrupt firmware-visible memory. Changes should be checked across 32/64-bit, endian, SMP, and relevant platform `CONFIG_*` combinations where applicable.

Test signals: PowerPC defconfig/allmodconfig build coverage, targeted boot or qemu/hardware coverage for the relevant platform, and subsystem tests around the named integration points. For ABI-facing layouts, compare generated offsets, UAPI headers, and compat signal/syscall behavior.

Source read size: 579 lines, 24630 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/rtas.h -->
