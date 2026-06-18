# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30.h

## Purpose
`scd30.h` is the shared header for Sensirion SCD30 CO2 sensor core and transports. It defines command IDs, common state, command callback type, PM ops, and core probe signature.

## Important APIs, Types, And Functions
`enum scd30_cmd` lists transport-neutral operations: start/stop measurement, interval, readiness, read measurement, automatic self calibration, forced recalibration, temperature offset, firmware version, and reset. `scd30_command_t` abstracts transport command execution. `struct scd30_state` stores serialization lock, device/regulator, measurement completion, transport private pointer, IRQ, cached pressure compensation, interval, latest measurements, and command callback. `scd30_probe()` is the shared core entry.

## Control Flow
The header has no executable control flow. Transport drivers provide a `scd30_command_t` implementation and call `scd30_probe()`, after which the core uses the callback for all device operations.

## State And Persistence
The shared state caches pressure compensation because the sensor cannot report it, measurement interval, and latest measurements. The mutex serializes device access and completion reports data readiness.

## Dependencies And Integration Points
It depends on completion, mutex, device, PM, regulator, and fixed-width types. It bridges I2C/serial transport implementations with the SCD30 core.

## Risks
Transport-private storage is embedded as `void *priv` because device driver data is already used for IIO; misuse can create lifetime issues. Cached pressure compensation can drift from hardware if commands fail. Command enum and transport implementations must remain synchronized.

## Test Signals
Compile all SCD30 transports, verify command callback coverage for every enum value, test cached pressure/interval behavior, IRQ and polling readiness paths, and suspend/resume PM ops.
