<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/meson_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/meson_wdt.c`

Purpose: watchdog driver for older Amlogic Meson6/Meson8 watchdog blocks with variant-specific enable bits, counter masks, and count units.

Important APIs, types, and functions: `struct meson_wdt_data` describes enable bit, terminal-count mask, and counts-per-second. `meson_wdt_change_timeout()` updates terminal count bits, ping writes the reset register, start programs timeout/pings/enables, stop clears enable, and restart loops writing a reset-enabled terminal count until hardware resets.

Control flow: probe maps MMIO, selects match data, computes max timeout from mask/count unit, initializes watchdog defaults and restart priority, applies module timeout and nowayout, stops the watchdog initially, installs stop-on-reboot, registers, and logs settings.

State and persistence: the driver intentionally stops the watchdog during probe rather than handing off a running firmware watchdog. Timeout is stored in terminal-count bits and constrained by variant mask. No bootstatus or timeleft support is provided.

Dependencies and integration points: depends on OF compatibles `amlogic,meson6-wdt`, `meson8-wdt`, `meson8b-wdt`, `meson8m2-wdt`, watchdog core, MMIO, and restart priority.

Risks and test signals: risks include stopping a bootloader-enabled watchdog unexpectedly, count-unit differences, infinite restart loop if reset fails, and max timeout calculation. Test each compatible data set, start/stop/ping, reboot restart, module timeout bounds, and stop-on-reboot behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/meson_wdt.c -->
