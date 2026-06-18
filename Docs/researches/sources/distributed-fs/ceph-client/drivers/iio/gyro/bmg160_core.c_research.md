# sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_core.c

## Purpose
Common IIO core for Bosch BMG160 and compatible BMI055/BMI088 gyroscopes, providing raw/temp reads, scale, sample frequency, low-pass filter, mount matrix, events, IRQ triggers, buffers, regulators, and runtime PM.

## Important APIs, Types, And Functions
`struct bmg160_data` stores regmap, triggers, mount matrix, mutex, scan buffer, range/filter/event state, IRQ, and trigger flags. Major functions cover chip init, mode/power control, bandwidth/filter/scale conversion, axis/temp reads, raw sysfs handlers, event handlers, any-motion and data-ready interrupt setup, buffer setup ops, trigger ops, `bmg160_core_probe`, `bmg160_core_remove`, and PM callbacks.

## Control Flow
Core probe enables regulators, reads mount matrix, resets and validates chip ID, initializes default bandwidth/range/interrupt latch mode, creates optional IRQ triggers, sets up triggered buffers, enables runtime PM autosuspend, and registers the IIO device. Raw writes temporarily resume the device for register writes. IRQ top half polls triggers and optionally wakes the threaded event handler.

## State And Persistence
Persistent device registers include power mode, range, bandwidth, interrupt mapping/enables, latch mode, slope threshold, and motion axis bits. Software caches selected DPS range, slope threshold, event enable state, trigger-enable state, and orientation. Runtime PM autosuspends after 2 seconds and remove enters deep suspend.

## Dependencies And Integration Points
Depends on regmap supplied by bus shims, regulators `vdd`/`vddio`, IIO events, triggered buffers, IIO triggers, runtime PM, and optional IRQ. Exports core probe/remove and PM ops for I2C/SPI modules.

## Risks
Event and trigger state interact through shared interrupt registers and need careful sequencing. Some table searches do not explicitly guard the "not found" index before indexing in filter helpers. The source includes apparent duplicated comment/`else` text in event paths that should be caught by compile tests.

## Test Signals
Probe over both buses with and without IRQ, verify chip-ID failure, read/write sample frequency, LPF, scale, temp and axes, enable buffer capture, enable data-ready and any-motion triggers, test event threshold busy behavior, and exercise runtime/system suspend and remove deep-suspend.
