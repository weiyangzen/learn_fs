<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/common.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/common.c

## Purpose
Shared INT3472 helper library for reading ACPI buffers and discovering dependent camera sensors.

## Important APIs, Types, And Functions
`skl_int3472_get_acpi_buffer()` evaluates an ACPI object such as `CLDB` or `SSDB` and verifies it is a buffer. `skl_int3472_fill_cldb()` copies the CLDB buffer into `struct int3472_cldb` with size validation. `skl_int3472_get_sensor_adev_and_name()` finds the next ACPI consumer device and formats its I2C device name.

## Control Flow
Both discrete and TPS68470 paths use CLDB to decide control logic type. Discrete probe uses the sensor discovery helper to build GPIO/clock/regulator lookup names.

## State And Persistence
The helpers allocate returned ACPI buffers that callers must free. Sensor ACPI references are passed to callers, which must release them when no longer needed.

## Dependencies And Integration Points
Depends on ACPI companion/consumer APIs, device-managed string allocation, and exported symbol namespace `INTEL_INT3472`.

## Risks And Test Signals
Risks include CLDB truncation semantics, missing dependents, and leaked ACPI references on failure paths. Test with absent CLDB, malformed CLDB, multiple consumers, and module namespace resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/common.c -->
