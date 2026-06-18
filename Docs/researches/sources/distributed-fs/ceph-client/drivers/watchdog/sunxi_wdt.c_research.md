# sources/distributed-fs/ceph-client/drivers/watchdog/sunxi_wdt.c

## Purpose
`sunxi_wdt.c` drives Allwinner sunxi watchdog variants. It abstracts variant-specific register offsets, reset bits, timeout shift, and key values while exposing standard watchdog start/stop/ping/set-timeout and restart operations.

## Important APIs, types, and functions
`struct sunxi_wdt_reg` describes register layout and keying; `struct sunxi_wdt_dev` stores watchdog, MMIO base, and selected layout. Core functions are `sunxi_wdt_restart()`, `sunxi_wdt_ping()`, `sunxi_wdt_set_timeout()`, `sunxi_wdt_stop()`, and `sunxi_wdt_start()`. Variant tables cover sun4i, sun6i, sun20i, and sun55i compatibles.

## Control flow
Probe allocates state, selects variant data from DT, maps registers, initializes 1..16 second bounds, reads optional timeout, applies nowayout and restart priority, stores drvdata, stops the watchdog into a known state, sets stop-on-reboot, and registers. Start programs reset behavior, writes the timeout selector from `wdt_timeout_map`, reloads, and enables. Restart forces reset mode, enables with the lowest timeout, reloads, then loops re-enabling until reset occurs.

## State and persistence behavior
Timeout is stored in the watchdog device and encoded into mode register selector bits. Variant key values are ORed into protected register writes where required. Hardware state persists in mode/config/control registers.

## Dependencies and integration points
The driver depends on OF match data, platform MMIO resources, watchdog core, restart handlers, and Allwinner-specific register layouts.

## Risks and test signals
Risks include timeout rounding by incrementing unsupported values only once, write-key omissions for variants, infinite loop in restart by design, and differences between reset mask/value meanings. Tests should cover all compatible variants, unsupported timeout requests, stop clearing enable, ping reload, restart reset path, boot probe stop, and timeout map boundaries.
