<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geos.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/geode/geos.c

## Purpose
Detects Traverse Technologies GEOS Geode systems and registers their GPIO LEDs and restart key.

## Important APIs, Types, And Functions
`geos_init()` checks `is_geode()`, DMI vendor `Traverse Technologies`, and product `Geos`. `register_geos()` registers restart GPIO pin 3 and LEDs on pins 6, 25, and 27.

## Control Flow
The `device_initcall` self-filters by CPU and DMI, logs recognition, and delegates all device creation to `geode-common`.

## State And Persistence
Runtime state is the created software-node/platform-device graph for GPIO keys and LEDs.

## Dependencies And Integration Points
Uses DMI, `asm/geode.h`, and the shared Geode helper. Downstream integration is through generic GPIO, input, and LED subsystems.

## Risks And Edge Cases
Requires exact DMI strings, so firmware changes can prevent detection. Incorrect pin mapping would expose nonfunctional or wrong controls.

## Test Signals
Boot log recognition, LED class entries named with `geos`, and an input restart key are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/geode/geos.c -->
