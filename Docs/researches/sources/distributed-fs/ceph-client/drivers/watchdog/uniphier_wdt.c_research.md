# sources/distributed-fs/ceph-client/drivers/watchdog/uniphier_wdt.c

## Purpose
`uniphier_wdt.c` drives the Socionext UniPhier watchdog through a parent syscon regmap. It supports power-of-two timeouts, reset-selection setup, polling around counter clear status, and standard start/stop/ping operations.

## Important APIs, types, and functions
`struct uniphier_wdt_dev` embeds watchdog and regmap. Important helpers are `uniphier_watchdog_ping()`, `__uniphier_watchdog_start()`, `__uniphier_watchdog_stop()`, `__uniphier_watchdog_restart()`, `uniphier_watchdog_start()`, `uniphier_watchdog_stop()`, and `uniphier_watchdog_set_timeout()`. Probe is `uniphier_wdt_probe()`.

## Control flow
Probe gets the parent syscon regmap, initializes timeout defaults and bounds, applies optional module/DT timeout and nowayout, stores drvdata, stops the watchdog, programs reset selection to reset both targets, and registers. Start rounds the timeout to a power of two, waits until status is clear, writes period, enables and clears, then polls until status is set. Ping writes the clear bit and waits for status set.

## State and persistence behavior
Timeout is rounded and stored in the watchdog device. Hardware state persists in syscon registers `WDTTIMSET`, `WDTRSTSEL`, and `WDTCTRL`. No durable software state exists.

## Dependencies and integration points
It depends on DT compatible `socionext,uniphier-wdt`, parent syscon regmap, polling helpers, and watchdog core stop-on-reboot.

## Risks and test signals
Risks include power-of-two rounding not reflected until set/start, polling timeouts, parent syscon assumptions, and `WDIOF_OVERHEAT` option being a semantic mismatch for a watchdog reset source. Tests should cover parent lookup, reset-selection write, ping/start poll timeouts, rounded timeout requests, stop clearing enable, and nowayout/stop-on-reboot behavior.
