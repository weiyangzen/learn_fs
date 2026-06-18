# sources/distributed-fs/ceph-client/drivers/thermal/thermal_mmio.c

## Purpose
`thermal_mmio.c` is a small platform thermal driver for simple memory-mapped temperature sensors. The current match table supports Amazon Annapurna Labs compatible `"amazon,al-thermal"`.

## Important APIs, Types, and Functions
`struct thermal_mmio` stores the mapped base, read callback, mask, and scale factor. `thermal_mmio_get_temperature` implements thermal-zone `.get_temp`; `thermal_mmio_probe` maps resources, applies match-data initialization, registers a DT thermal zone, and logs the first reading. `al_thermal_init` configures byte reads, `0xff` mask, and a `1000` factor.

## Control Flow
Probe allocates driver state, maps MMIO resource 0, calls the compatible-specific initializer, registers sensor id 0 with `devm_thermal_of_zone_register`, reads the current temperature through the thermal-zone callback, and reports success. Reads mask the MMIO value and multiply by the configured factor to produce millidegrees.

## State and Persistence Behavior
Runtime state is devm-managed and lasts until device removal. There is no suspend logic or nonvolatile persistence; hardware registers remain the source of truth.

## Dependencies and Integration Points
It integrates platform devices, OF matching, resource-managed ioremap, thermal OF zones, and the generic thermal framework. The DT thermal zone supplies trips/polling/cooling maps.

## Risks and Edge Cases
The generic math assumes raw code times factor is a valid millidegree value; additional compatibles must supply correct masks and scaling. There is no range checking, sign handling, or multi-register support.

## Test Signals
DT binding/probe smoke tests, ioremap failure paths, thermal zone registration, `temp` sysfs read returning raw byte times 1000, and future compatible tests for non-byte sensors.
