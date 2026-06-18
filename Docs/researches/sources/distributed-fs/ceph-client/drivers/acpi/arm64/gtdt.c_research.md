# sources/distributed-fs/ceph-client/drivers/acpi/arm64/gtdt.c

## Purpose
Parses the ARM Generic Timer Description Table for architected timer PPIs, MMIO timer frames, and SBSA generic watchdog platform devices.

## Important APIs, Types, And Functions
Exports early helpers `acpi_gtdt_init()`, `acpi_gtdt_map_ppi()`, and `acpi_gtdt_c3stop()`. Device-init logic is in `gtdt_platform_timer_init()`, `gtdt_parse_timer_block()`, and `gtdt_import_sbsa_gwdt()`.

## Control Flow
`acpi_gtdt_init()` stores GTDT bounds and counts valid platform timer structures for revision 2 or later. PPI helpers map timer GSIs and report always-on state. At device init, the table is reacquired with permanent mappings, platform timers are walked, non-secure watchdogs become `sbsa-gwdt` devices, and timer blocks become `gtdt-arm-mmio-timer` devices after frame validation and IRQ mapping.

## State And Persistence
An initdata descriptor stores table pointers during parsing. Registered platform devices persist. Mapped GSIs remain registered unless error cleanup explicitly unregisters them.

## Dependencies And Integration Points
Integrates ACPI GTDT, GSI registration, ARM arch timer code, platform devices, and SBSA watchdog driver.

## Risks
Malformed platform timer lengths, mismatched counts, duplicate or invalid frame numbers, missing base addresses, and partial IRQ mapping failures are key firmware risks.

## Test Signals
Check revision less than 2, count mismatch clamping, PPI polarity/trigger mapping, c3stop flags, secure timer frame skipping, duplicate frame rejection, watchdog without IRQ, and platform-device registration.
