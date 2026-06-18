# sources/distributed-fs/ceph-client/drivers/watchdog/ni903x_wdt.c

## Purpose
`ni903x_wdt.c` drives the National Instruments 903x ACPI watchdog through an I/O port register block. It programs a 24-bit seed counter and services the watchdog by setting a PET control bit.

## Important APIs, types, and functions
`struct ni903x_wdt` stores the device, I/O base, and watchdog object. Key functions are `ni903x_resources`, `ni903x_wdd_start`, `ni903x_wdd_stop`, `ni903x_wdd_ping`, `ni903x_wdd_set_timeout`, `ni903x_wdd_get_timeleft`, `ni903x_acpi_probe`, and `ni903x_acpi_remove`.

## Control flow
Probe walks ACPI `_CRS` to find and reserve exactly one I/O resource of at least eight bytes, initializes watchdog limits, applies module timeout/nowayout, registers the device, then switches hardware from boot mode to user mode. Start resets the controller, enables processor reset, writes the seed derived from `timeout / 30.720 us`, then starts/pets the watchdog. Stop writes reset only. Time-left capture sets `CAPTURECOUNTER` and reads the three counter bytes.

## State and persistence
Hardware state is in control, seed, and counter registers. The ACPI I/O resource reservation persists for device lifetime. No bootstatus is decoded; watchdog timeout persists only in hardware until reprogrammed.

## Dependencies and integration points
It integrates ACPI ID `NIC775C`, ACPI resource walking, x86-style `inb/outb` I/O, watchdog core, and module parameters `timeout` and `nowayout`.

## Risks and test signals
Risks include ACPI resources with extra unsupported I/O ranges, unreported request-region size mismatches, integer truncation of counter math, and stop semantics that may reset but not fully disable depending on hardware. Test signals include `_CRS` parse failure, short I/O region, get-timeleft capture, default and boundary timeout programming, module nowayout, and remove path stop/unregister.
