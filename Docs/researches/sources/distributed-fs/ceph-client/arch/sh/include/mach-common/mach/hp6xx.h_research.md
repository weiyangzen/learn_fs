<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/hp6xx.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/hp6xx.h

Purpose: provides the HP Jornada HP6xx handheld GPIO/ADC/HD64461 constants.

Important APIs/types/functions: HP680_BTN_IRQ, HP680_TS_IRQ, HP680_HD64461_IRQ, DAC_LCD_BRIGHTNESS, DAC_SPEAKER_VOLUME, PGDR_OPENED, PGDR_MAIN_BATTERY_OUT, PGDR_PLAY_BUTTON, PGDR_REWIND_BUTTON.

Control flow: the file itself is declarative; board setup and drivers consume the constants to map memory windows, program CPLD/FPGA/GPIO registers, assign IRQs, or issue board-specific raw I/O.

State and persistence: state is in external board registers, latches, interrupt masks, and device windows touched by consumers; the header holds no runtime storage.

Dependencies/integration: integrates machine-vector setup, platform-device resources, interrupt routing, raw I/O helpers, and board-specific peripheral drivers.

Risks: physical addresses, bit masks, and IRQ numbers are hardware contracts; mistakes usually compile but produce dead devices, bad bus cycles, or interrupt storms.

Test signals: boot the board configuration and verify device probe, register access, external IRQ delivery, and any reset/power/LED controls named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/mach-common/mach/hp6xx.h -->
