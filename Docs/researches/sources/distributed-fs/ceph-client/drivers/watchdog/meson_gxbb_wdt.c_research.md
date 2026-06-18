<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/meson_gxbb_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/meson_gxbb_wdt.c`

Purpose: watchdog driver for newer Amlogic Meson GXBB/T7 watchdog hardware with 1 ms timebase setup, optional running-state handoff, and timeleft support.

Important APIs, types, and functions: `struct meson_gxbb_wdt` stores MMIO, watchdog core device, and clock. Match `wdt_params` supplies reset bit position. Start/stop toggle `GXBB_WDT_CTRL_EN`; ping writes reset register; set_timeout writes `TCNT` setup value in milliseconds; get_timeleft subtracts current count from setup count.

Control flow: probe maps registers, enables clock, reads match data, initializes watchdog core bounds and module timeout, detects an already-enabled watchdog and temporarily stretches timeout while preserving running state, programs control register with divider/reset/clock bits, sets final timeout, and registers. PM suspend stops active watchdog; resume restarts it.

State and persistence: watchdog enable may persist from boot and is marked `WDOG_HW_RUNNING`. Timeout register is limited to 16-bit milliseconds, so max hardware heartbeat is about 65 seconds. Control register holds clock divider and reset routing.

Dependencies and integration points: depends on OF compatibles `amlogic,meson-gxbb-wdt` and `amlogic,t7-wdt`, clock rate, MMIO, watchdog core, and system sleep PM ops.

Risks and test signals: risks include divider truncation, max timeout clamping while recording requested timeout, preserving enabled state during setup, and T7 reset-bit differences. Test already-running firmware handoff, get_timeleft, suspend/resume, timeout near 65 seconds, and reset-line behavior per compatible.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/meson_gxbb_wdt.c -->
