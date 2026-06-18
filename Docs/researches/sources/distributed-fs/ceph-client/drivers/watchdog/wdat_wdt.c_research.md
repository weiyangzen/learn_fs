# sources/distributed-fs/ceph-client/drivers/watchdog/wdat_wdt.c

## Purpose
`wdat_wdt.c` implements the ACPI WDAT hardware watchdog driver. It parses the firmware WDAT table into action-specific instruction lists and exposes the watchdog through the modern watchdog core.

## Important APIs, types, and functions
Core types are `struct wdat_instruction`, wrapping an `acpi_wdat_entry` and mapped register pointer, and `struct wdat_wdt`, containing the platform device, `watchdog_device`, timer period, suspend flags, and action lists. Important functions are `wdat_wdt_run_action`, `wdat_wdt_read`, `wdat_wdt_write`, `wdat_wdt_enable_reboot`, `wdat_wdt_boot_status`, `wdat_wdt_set_running`, watchdog ops `start`, `stop`, `ping`, `set_timeout`, optional `get_timeleft`, `wdat_wdt_probe`, and noirq suspend/resume callbacks.

## Control flow
Probe obtains the ACPI WDAT table, validates period/count bounds, maps platform memory or I/O resources, converts each WDAT entry into an instruction tied to the matching resource, and links it under its action number. It reads boot status, detects already-running state, enables reboot-on-fire, sets a safer initial timeout, marks nowayout/stop policies, and registers with the watchdog core. Runtime ops execute firmware-defined action sequences for start, stop, reset, countdown, and timeleft.

## State and persistence
Runtime state is device-managed and firmware-derived. Hardware countdown/reboot configuration persists in platform registers until firmware or the driver changes it. The driver remembers whether it stopped the watchdog during suspend so resume can reprogram appropriately.

## Dependencies and integration points
It depends on ACPI WDAT definitions, generic address structures, platform resources, I/O mapping helpers, PM noirq hooks, and the watchdog core. It integrates with firmware-provided WDAT platform devices and ACPI sleep state handling.

## Risks and test signals
Risks include malformed WDAT tables, unsupported access widths or address spaces, register-resource mismatch, preserve-mask arithmetic, period/count overflow, firmware reinitialization across sleep, and optional actions returning `-EOPNOTSUPP`. Test signals include WDAT systems with memory and I/O GAS entries, missing optional actions, boot-status clear, running-at-boot detection, suspend-to-idle versus S3/S4 paths, timeout conversion boundaries, and ACPI table fuzzing.
