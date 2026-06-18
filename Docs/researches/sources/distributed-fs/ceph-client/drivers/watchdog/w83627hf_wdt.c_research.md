# sources/distributed-fs/ceph-client/drivers/watchdog/w83627hf_wdt.c

## Purpose
`w83627hf_wdt.c` drives many Winbond/Nuvoton Super I/O watchdog variants through extended-function configuration ports. It detects supported chip IDs, selects watchdog logical device 8, configures watchdog output pins/control/status registers, and registers a modern watchdog device.

## Important APIs, types, and functions
Chip variants are enumerated in `enum chips`; register globals `cr_wdt_timeout`, `cr_wdt_control`, and `cr_wdt_csr` are selected by chip ID. Super I/O helpers are `superio_enter()`, `superio_exit()`, `superio_select()`, `superio_outb()`, and `superio_inb()`. Core routines are `wdt_find()`, `w83627hf_init()`, `wdt_set_time()`, `wdt_start()`, `wdt_stop()`, `wdt_set_timeout()`, and `wdt_get_time()`. `wdt_use_alt_key()` is a DMI quirk for alternate unlock keys.

## Control flow
Init applies DMI quirks, probes ports `0x2e` then `0x4e`, logs chip name, initializes timeout and nowayout, sets stop-on-reboot, configures the chip, and registers. Chip init activates the watchdog logical device, applies chip-specific output pin routing or KBRST pulse enablement, optionally disables an already-running watchdog if `early_disable` is set or reloads it otherwise, sets seconds mode, disables keyboard/mouse watchdog cancellation, captures and clears card-reset status, and exits configuration mode.

## State and persistence behavior
Global state records selected port, register addresses, unlock/lock keys, and static watchdog data. Hardware configuration persists in Super I/O logical-device registers; bootstatus is captured from the CSR and then cleared.

## Dependencies and integration points
The driver depends on x86 port I/O, muxed region reservation, DMI quirks, watchdog core, and chip-specific Super I/O register contracts.

## Risks and test signals
Risks include broad chip matrix with subtle register differences, touching pin muxes on boards where BIOS configured alternate WDTO pins, singleton global state, and timeout setter not programming hardware until start. Tests should cover both probe addresses, each known ID mapping, DMI alternate key path, early_disable, bootstatus capture/clear, seconds mode programming, start/stop/get_time, and reboot stop.
