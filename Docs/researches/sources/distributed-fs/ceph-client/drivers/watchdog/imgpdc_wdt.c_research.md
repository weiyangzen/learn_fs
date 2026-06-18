<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imgpdc_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/imgpdc_wdt.c`

Purpose: Imagination Technologies PowerDown Controller watchdog driver for `img,pdc-wdt` devices. It maps PDC registers, enables `sys` and `wdt` clocks, programs coarse power-of-two timeouts, reports reset cause, and supplies a restart hook.

Important APIs, types, and functions: `struct pdc_wdt_dev` embeds `watchdog_device` plus clock and MMIO pointers. `pdc_wdt_keepalive()` writes the two tickle magic values, `pdc_wdt_stop()` clears `PDC_WDT_CONFIG_ENABLE` and tickles to commit the stop, `__pdc_wdt_set_timeout()` computes `order_base_2(timeout * clk_rate) - 1`, and `pdc_wdt_restart()` asserts `PDC_WDT_SOFT_RESET`.

Control flow: probe allocates state, maps the MMIO resource, enables clocks, derives min/max timeout from the watchdog clock, initializes the watchdog core device, stops any active watchdog, reads tickle status for boot cause, sets nowayout and restart priority, installs stop-on-reboot/unregister, then registers with `devm_watchdog_register_device()`.

State and persistence: timeout precision is hardware-limited to powers of two clock cycles, so the actual timeout is at least the requested value. Bootstatus is latched in `PDC_WDT_TICKLE1` status bits and translated to `WDIOF_CARDRESET` for timeout or bad tickle resets. Clock rate is a runtime dependency for all timeout math.

Dependencies and integration points: requires devicetree compatible `img,pdc-wdt`, `sys` and `wdt` clocks, MMIO, watchdog core, and restart priority 128. User-visible timeout values may differ from real hardware intervals due to rounding.

Risks and test signals: risks include invalid zero/high clock rates, coarse timeout surprises, and stop not completing unless tickled. Test with devicetree clocks, timeout values near powers of two, bootstatus after timeout/reset/user reset, restart path, and stop-on-reboot/unregister behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/imgpdc_wdt.c -->
