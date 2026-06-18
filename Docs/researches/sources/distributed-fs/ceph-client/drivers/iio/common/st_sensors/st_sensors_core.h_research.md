
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_core.h

## Purpose
`st_sensors_core.h` is a small local header for declarations shared inside the ST common implementation files.

## Important APIs, types, and functions
- Forward declares `struct iio_dev`.
- Declares `st_sensors_write_data_with_mask()`, which trigger code uses to program interrupt polarity and related fields.

## Control flow
No runtime control flow exists in this header.

## State and persistence behavior
No state is defined here.

## Dependencies and integration points
It connects `st_sensors_trigger.c` to the non-public helper implemented in `st_sensors_core.c` without exposing that prototype through the public ST sensors header.

## Risks and edge cases
The header intentionally exposes only one helper. Any additional cross-file local helper use would need to be declared here or moved to the public header if needed by sensor-specific modules.

## Test signals
Build coverage with `CONFIG_IIO_TRIGGER=y` is enough to validate this declaration remains consistent with the implementation.
