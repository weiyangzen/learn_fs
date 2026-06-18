# sources/distributed-fs/ceph-client/include/clocksource/timer-ti-dm.h

Purpose: OMAP/TI dual-mode timer constants, offsets, and minimal public timer type.

Important APIs/types/functions: clock source IDs, interrupt bits, trigger modes, capability flags, empty `struct omap_dm_timer`, `omap_dm_timer_modify_idlect_mask`, v1/v2 register offsets, functional register offsets, control bits, and write-pending bit masks.

Control flow: implementation code uses offsets and flags to select clock source, program IRQs, configure autoreload/compare/prescale/capture/PWM, poll write-pending bits, and support v1/v2 register layout differences.

State and persistence: timer hardware registers hold counter/load/match/control/IRQ state. The header only describes their layout.

Dependencies and integration points: depends on delay, I/O, and platform-device headers; integrates with OMAP dmtimer, clocksource, PWM, and platform hwmod code.

Risks: posted write-pending handling is fragile; failing to wait on the right `WP_*` bit can race register updates. v1/v2 offset mismatch can program the wrong register.

Test signals: OMAP boot tests, PWM/timer shared use, tick accuracy, suspend/resume timer retention, and register layout coverage on v1 and v2 IP.
