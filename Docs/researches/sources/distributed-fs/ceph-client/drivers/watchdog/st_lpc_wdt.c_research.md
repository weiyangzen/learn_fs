# sources/distributed-fs/ceph-client/drivers/watchdog/st_lpc_wdt.c

## Purpose
`st_lpc_wdt.c` uses the ST LPC block in watchdog mode. It loads the low-power alarm timer, controls LPC watchdog enable, and configures reset masking/type through a syscon regmap.

## Important APIs, types, and functions
`struct st_wdog_syscfg` describes syscon registers/masks; `struct st_wdog` stores MMIO base, device, regmap, syscfg, clock, clock rate, and warm-reset flag. Key functions are `st_wdog_setup()`, `st_wdog_load_timer()`, `st_wdog_start()`, `st_wdog_stop()`, `st_wdog_set_timeout()`, `st_wdog_keepalive()`, `st_wdog_probe()`, `st_wdog_remove()`, `st_wdog_suspend()`, and `st_wdog_resume()`.

## Control flow
Probe requires device-tree property `st,lpc-mode` equal to `ST_LPC_MODE_WDT`, maps registers, obtains `st,syscfg`, enables the clock, computes `max_timeout`, initializes the global watchdog device, reads `timeout-sec`, registers, then unmasks watchdog reset via `st_wdog_setup(true)`. Start writes `LPC_WDT_OFF`; timeout/ping load `timeout * clkrate` into the LPA register and start it. Suspend stops an active watchdog, masks reset, and disables the clock; resume reverses that and reloads/restarts if active.

## State and persistence behavior
The driver uses a static global `st_wdog_dev`, so only one instance is represented. Hardware state persists in LPC timer registers and syscon reset gate/type bits. Clock rate determines all timeout encoding.

## Dependencies and integration points
Dependencies include ST LPC DT bindings, syscon/regmap, clock framework, device tree, and watchdog core. `stih407_syscfg` supplies enable mask data for compatible `st,stih407-lpc`.

## Risks and test signals
Risks include static singleton behavior, timeout overflow if clock rates are unexpectedly high, reset gate misconfiguration, and resume unregistering on clock-enable failure. Tests should validate mode rejection, syscfg phandle failures, max-timeout calculation, cold/warm reset bit programming, timeout/ping register writes, and suspend/resume transitions.
