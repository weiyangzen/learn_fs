<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/Makefile

Purpose: This Makefile builds Sega Dreamcast-specific machine support.

Important APIs/types/functions: It sets `obj-y := setup.o irq.o` and conditionally adds `rtc.o` for `CONFIG_RTC_DRV_GENERIC`.

Control flow: Dreamcast builds always include setup and System ASIC IRQ handling; generic RTC support additionally includes AICA RTC registration.

State and persistence: Build selection only.

Dependencies and integration points: It depends on `CONFIG_SH_DREAMCAST`, generic RTC config, and the Dreamcast machine directory selected from the board Makefile.

Risks and test signals: Missing `irq.o` would prevent Maple/System ASIC device interrupts; missing `rtc.o` only affects timekeeping. Tests include Dreamcast build with and without `RTC_DRV_GENERIC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-dreamcast/Makefile -->
