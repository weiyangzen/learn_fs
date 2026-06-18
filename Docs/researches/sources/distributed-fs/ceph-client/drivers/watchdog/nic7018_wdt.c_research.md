# sources/distributed-fs/ceph-client/drivers/watchdog/nic7018_wdt.c

## Purpose
`nic7018_wdt.c` supports the National Instruments NIC7018 ACPI watchdog. It chooses between two prescaler periods, programs a compact counter/prescaler register, and exposes time-left readback.

## Important APIs, types, and functions
`struct nic7018_wdt` stores I/O base, active period, and watchdog object. `struct nic7018_config` represents hardware period/divider pairs. Key functions are `nic7018_get_config`, `nic7018_set_timeout`, `nic7018_start`, `nic7018_stop`, `nic7018_ping`, `nic7018_get_timeleft`, `nic7018_probe`, and `nic7018_remove`.

## Control flow
Probe obtains an ACPI-provided I/O resource, reserves it, initializes watchdog limits and module options, unlocks the watchdog register block, and registers the watchdog. Start recalculates timeout, enables reload-port access, writes reload, and enables reset. Stop clears control registers and resets preset/prescaler. Ping writes the reload port. Remove unregisters the watchdog and locks the register block.

## State and persistence
The selected period is cached for `get_timeleft`, while hardware stores the actual counter/prescaler and lock state. No bootstatus is reported. Register lock state is restored on removal.

## Dependencies and integration points
It depends on ACPI ID `NIC7018`, platform I/O resources, watchdog core, and module parameters `timeout`/`nowayout`.

## Risks and test signals
Risks include rounded timeouts not matching user request, global hardware unlock during lifetime, no explicit stop before unregister, and `get_timeleft` using cached period that assumes no external reprogramming. Test signals include ACPI probe, region conflicts, timeout rounding around 16/30 seconds, start/stop lock behavior, reload-port enable, and timeleft register reads.
