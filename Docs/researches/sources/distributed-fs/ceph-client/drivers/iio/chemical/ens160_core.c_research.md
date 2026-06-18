# sources/distributed-fs/ceph-client/drivers/iio/chemical/ens160_core.c

## Purpose
`ens160_core.c` implements the ScioSense ENS160 multi-gas IIO core. It exposes TVOC and equivalent CO2 concentration channels, optional IRQ-triggered buffering, chip initialization, and sleep PM.

## Important APIs, Types, And Functions
`struct ens160_data` stores regmap, mutex, aligned scan buffer, firmware version bytes, and a 16-bit scratch buffer. `ens160_chip_init()` resets the device, verifies part ID, moves to idle, clears GPR, requests firmware version, enters standard mode, registers an idle cleanup action, and checks device status validity. `ens160_read_raw()` handles direct raw reads and scales. `ens160_trigger_handler()` bulk-reads TVOC/ECO2 into the scan. `ens160_setup_trigger()` registers an own-device data-ready trigger. `devm_ens160_core_probe()` wires everything together and is exported.

## Control Flow
Transport probe calls the core with regmap and IRQ. The core optionally registers a trigger if IRQ is positive, initializes the chip, initializes the mutex, sets up a triggered buffer, and registers the IIO device. Direct reads claim direct mode, lock, bulk-read one channel, and release. IRQ-triggered buffer reads both channels from consecutive registers.

## State And Persistence
Firmware version and mode state are cached/logged during init. The cleanup action returns the chip to idle. Suspend enters deep sleep; resume transitions idle then standard. The mutex serializes direct and buffered reads.

## Dependencies And Integration Points
It depends on regmap, IIO direct/triggered-buffer APIs, IIO triggers, sleep PM ops, and `IIO_ENS160` namespace export for transports.

## Risks
The mutex is initialized after `ens160_chip_init()`, but direct/buffer callbacks are not registered until later, so this is acceptable but fragile if init starts using the mutex. Status validity is checked only once. Environmental compensation input registers are defined but not exposed. IRQ setup occurs before chip init; trigger won't be active yet, but error ordering should be tested.

## Test Signals
Test part ID mismatch, firmware version command sequence, status validity failure, direct read scales, IRQ and no-IRQ probe paths, trigger enable bits, suspend/resume modes, and cleanup action on probe failure.
