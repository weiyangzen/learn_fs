# sources/distributed-fs/ceph-client/drivers/watchdog/npcm_wdt.c

## Purpose
`npcm_wdt.c` drives the Nuvoton WPCM450/NPCM750 watchdog. It maps requested timeouts to the discrete hardware interval table, supports bark/pretimeout IRQ notification, and provides a restart operation.

## Important APIs, types, and functions
`struct npcm_wdt` contains `watchdog_device`, MMIO register pointer, and optional clock. Operations are `npcm_wdt_start`, `npcm_wdt_stop`, `npcm_wdt_ping`, `npcm_wdt_set_timeout`, `npcm_wdt_restart`, `npcm_wdt_interrupt`, and `npcm_is_running`.

## Control flow
Probe maps the register, gets an optional clock, requires an IRQ, initializes limits, normalizes the default/DT timeout to representable hardware values, restarts already-running hardware with the selected timeout, requests the IRQ, and registers the watchdog. Start enables clock, selects the nearest register value, enables reset, interrupt, counter reset, and watchdog. Stop writes zero and disables clock. Interrupt calls `watchdog_notify_pretimeout`. Restart enables the clock and writes the shortest reset-enabled sequence.

## State and persistence
Hardware state is the WTCR register and clock gate. The previous running state can be inherited from firmware and marked `WDOG_HW_RUNNING`. Timeout is rounded to discrete supported values.

## Dependencies and integration points
It depends on OF compatibles `nuvoton,wpcm450-wdt` and `nuvoton,npcm750-wdt`, platform IRQ, optional clock, watchdog core pretimeout notification, and restart callback.

## Risks and test signals
Risks include ignored `clk_prepare_enable` return in start/restart, discrete timeout rounding surprising users, interrupt flag handling without explicit acknowledge beyond watchdog register behavior, and requiring an IRQ even if only reset mode is desired. Test signals include all timeout buckets, active-at-boot restart, IRQ delivery, optional clock absence, restart path, and stop clock balance.
