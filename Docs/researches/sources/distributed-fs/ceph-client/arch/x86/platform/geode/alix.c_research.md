<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/alix.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/alix.c

## Purpose
Detects PC Engines ALIX Geode boards and registers GPIO-backed LEDs and restart key support.

## Important APIs, Types, And Functions
`alix_present()` scans TinyBIOS/coreboot physical BIOS regions for ALIX signatures, `alix_present_dmi()` recognizes DMI identifiers, and `register_alix()` calls `geode_create_restart_key(24)` plus `geode_create_leds()` for pins 6, 25, and 27. The `force` module parameter bypasses BIOS matching.

## Control Flow
The `device_initcall` exits on non-Geode CPUs. Otherwise it checks TinyBIOS, coreboot, then DMI signatures; any match registers platform devices through the shared Geode helpers.

## State And Persistence
State consists of boot-time software nodes and platform devices for `gpio-keys-polled` and `leds-gpio`. The `force` parameter is read-only after boot.

## Dependencies And Integration Points
Uses `is_geode()`, DMI, physical BIOS mapping via `phys_to_virt()`, and `geode-common` software-node registration. It relies on the cs5535 GPIO provider to satisfy named GPIO references.

## Risks And Edge Cases
Signature scanning assumes accessible low BIOS mappings and can miss Award BIOS without `force`. False positives could register controls on the wrong machine. GPIO pin assumptions are board-model-specific.

## Test Signals
Boot log recognition messages, visible ALIX LEDs in the LED class, and a working restart key through input events validate the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/alix.c -->
