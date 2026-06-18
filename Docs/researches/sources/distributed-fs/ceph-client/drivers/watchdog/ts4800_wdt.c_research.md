# sources/distributed-fs/ceph-client/drivers/watchdog/ts4800_wdt.c

## Purpose
`ts4800_wdt.c` drives the Technologic Systems TS-4800 watchdog through a syscon regmap register. Hardware supports only a few feed values, so the driver maps requested timeouts to the closest supported 2 or 10 second feed.

## Important APIs, types, and functions
`struct ts4800_wdt` stores watchdog, regmap, feed offset, and selected feed value. Important functions are `ts4800_write_feed()`, `ts4800_wdt_start()`, `ts4800_wdt_stop()`, `ts4800_wdt_set_timeout()`, and `ts4800_wdt_probe()`. `ts4800_wdt_map` defines timeout-to-register mappings.

## Control flow
Probe parses the `syscon` phandle and offset, obtains the parent regmap, initializes min/max timeout from the mapping table, applies nowayout and optional timeout, defaults to maximum if unset, calls set-timeout to choose feed value, disables the write-only watchdog into a known state, then registers. Start writes the selected feed value; stop writes the disable value.

## State and persistence behavior
Because the feed register is write-only, probe cannot discover prior state and always disables it. Selected timeout and feed value are cached in software; hardware state persists in syscon logic.

## Dependencies and integration points
It depends on OF syscon phandle format, regmap, platform devices, and watchdog core.

## Risks and test signals
Risks include unsupported timeout rounding logic, write-only state loss at probe, and syscon phandle reference leaks if paths change. Tests should cover missing phandle/offset/regmap, timeout mapping below/between/above supported values, start/stop writes, nowayout close behavior, and initialization disable.
