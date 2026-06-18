# sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_core.c

## Purpose

`bma400_core.c` is the shared IIO core for the Bosch BMA400 accelerometer. It exposes acceleration, temperature, step count, activity classification, mount matrix, scale, sample frequency, oversampling ratio, triggered buffering, data-ready triggers, and events for step detection, activity, generic activity/inactivity magnitude, and single/double tap gestures.

## Important APIs, Types, and Functions

`struct bma400_data` stores device/regmap, mutex, orientation, power mode, cached sample frequency/OSR/scale, trigger, step/activity/event enable state, tap/generic event masks, and DMA-aligned buffer/status fields. `bma400_regmap_config` marks read-only and volatile registers and uses Maple cache. Important helpers include power/ODR/OSR/scale getters and setters, step enable/read, tap timing sysfs handlers, event enable/value callbacks, trigger set-state/handler, top-level interrupt handler, init, cleanup, and exported `bma400_probe()`.

## Control Flow

Probe allocates IIO state, runs `bma400_init()`, reads mount matrix, initializes the mutex, fills IIO metadata, optionally creates a trigger and threaded IRQ, sets up a triggered buffer, and registers the IIO device. Init enables `vdd`/`vddio`, validates chip ID `0x90`, wakes the chip to normal mode if needed, registers a power-down action, initializes availability tables, caches ODR/OSR/scale, configures INT1 as open drain, and selects the variable ODR filter data source.

Direct reads return processed temperature, steps, activity confidence, raw acceleration, ODR, scale, OSR, or step enable state. Writes set acceleration ODR, scale, OSR, or step enable. Event config writes program generic interrupt engines for rising/falling magnitude events, tap interrupt bits with a 200 Hz and normal-mode constraint, step event mapping, or activity event state. The IRQ handler reads 16-bit status, disables advanced interrupts on engine overrun, pushes tap/generic/step/activity events, and polls the nested trigger on data-ready status. The trigger handler bulk-reads acceleration and optional temperature and pushes a timestamped scan.

## State and Persistence Behavior

The driver keeps cached power mode, sample rate, oversampling ratio, scale, steps enabled, and event enable masks. Hardware settings persist until reset or cleanup. Power cleanup puts the device into sleep. Generic interrupts are initialized with all axes enabled, filtered data source, reference update mode, default threshold, and default duration before mapping/enable bits are set. Activity events depend on the step engine.

## Dependencies and Integration Points

The core depends on regmap with cache/volatile rules, regulators, IIO triggered buffers/triggers, IIO events, mount matrix parsing, IRQ status handling, and bus wrappers. It integrates with sysfs event attributes for tap timing/value availability and with the IIO activity and steps channel types.

## Risks

The TODO header is stale because events, interrupts, and steps are now implemented, which can mislead maintainers. `bma400_tap_event_en()` always updates the single-tap map bit before switching on the requested direction, so double-tap enable paths also touch single-tap mapping. The triggered buffer setup error is returned correctly here, unlike some older drivers, but the IRQ handler reads two status bytes into little-endian `data->status`; mask definitions must remain consistent. Advanced interrupt overrun disables all advanced interrupts and only logs an error, so user-visible event state may become stale. Tap events require normal mode and 200 Hz, which must be enforced in tests.

## Test Signals

Test coverage should include chip ID mismatch, regulator failures, wake-from-sleep sequencing, scale/ODR/OSR available lists and writes, raw and buffered accel/temp reads, step count and step event enable, activity confidence and activity events, generic rising/falling event threshold/period/hysteresis reads and writes, tap timing/value configuration, 200 Hz tap requirement, data-ready trigger polling, interrupt overrun disable behavior, and power-down cleanup.
