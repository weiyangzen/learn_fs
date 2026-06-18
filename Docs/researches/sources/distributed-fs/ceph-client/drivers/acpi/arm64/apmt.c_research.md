# sources/distributed-fs/ceph-client/drivers/acpi/arm64/apmt.c

## Purpose
Parses the ARM APMT table and creates platform devices for architectural PMU nodes.

## Important APIs, Types, And Functions
Main functions are `acpi_apmt_init()`, `apmt_init_platform_devices()`, `apmt_add_platform_device()`, and `apmt_init_resources()`. Devices are named `arm-cs-arch-pmu`.

## Control Flow
Initialization obtains the APMT table and keeps it mapped for runtime node access. The parser walks nodes by length, allocates a static fwnode for each, builds memory resources for page 0 and optional page 1, maps overflow GSIs to IRQ resources, stores the node pointer in platform data, assigns the fwnode, and adds the platform device.

## State And Persistence
`apmt_table` remains mapped after successful initialization because platform data points into it. Platform devices and their fwnodes persist.

## Dependencies And Integration Points
Depends on ACPI APMT structures, GSI registration, platform devices, and the CoreSight architectural PMU driver.

## Risks
Node length and table boundary trust is a risk because the loop advances by firmware-provided lengths. IRQ registration failures result in devices without IRQ resources rather than total failure.

## Test Signals
Test missing table, malformed node lengths, dual-page resources, no-overflow IRQ nodes, failed fwnode allocation, failed platform data/resource addition, and PMU driver probe.
