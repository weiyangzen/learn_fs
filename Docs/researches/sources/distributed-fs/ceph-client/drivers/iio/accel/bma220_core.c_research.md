# sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_core.c

## Purpose

`bma220_core.c` is the shared IIO core for the Bosch BMA220 accelerometer. It exposes three 6-bit acceleration channels, scale and low-pass filter controls, direct debug register access, optional IRQ-triggered buffered capture, and suspend/resume support.

## Important APIs, Types, and Functions

The file defines BMA220 register constants, `struct bma220_data`, channel specs, scale and filter tables, scan masks, writable-register predicate, and exported I2C/SPI regmap configs. The core IIO callbacks are `bma220_read_raw()`, `bma220_write_raw()`, `bma220_read_avail()`, and `bma220_reg_access()`. Lifecycle and power helpers include `bma220_init()`, `bma220_power()`, `bma220_reset()`, `bma220_deinit()`, `bma220_common_probe()`, and exported PM ops.

## Control Flow

Common probe allocates the IIO device, stores regmap, enables regulators `vddd`, `vddio`, and `vdda`, reads chip ID, powers and resets the chip by register-read side effects, initializes the mutex, configures IIO metadata and scan masks, optionally allocates/registers an IIO trigger and threaded IRQ, registers a cleanup action to suspend the chip, sets up a triggered buffer, and registers the IIO device.

Direct reads lock and read one acceleration register, sign-extending the 6-bit shifted value. Writes lock and update range/filter registers after exact table matching. The IRQ handler reads interrupt flag register `IF1`, polls the nested trigger when DRDY is set, and the trigger handler bulk-reads X/Y/Z and pushes a timestamped scan.

## State and Persistence Behavior

The driver caches range index and LPF index after successful writes. Hardware power and reset are unusual: reading the suspend or soft-reset register transitions state, so helpers perform up to two reads and compare returned mode values. Devm cleanup powers the chip down; PM suspend/resume use the same read-triggered power helper.

## Dependencies and Integration Points

It depends on regmap, regulators, IIO triggered buffers/triggers, threaded IRQs, PM, and bus wrappers that provide correctly shifted regmap addressing. SPI uses read flag bit 7; I2C uses `reg_shift = -1` to map SPI-style names to I2C addresses.

## Risks

The register-read side effects in `bma220_power()` and `bma220_reset()` are non-obvious and easy to break if converted to normal writes. `bma220_trigger_handler()` returns `IRQ_NONE` on read error without notifying trigger done, which can leave a trigger path waiting. The chip ID mismatch logs informationally and continues rather than failing. The triggered buffer setup error is logged but not returned before `devm_iio_device_register()`, so buffer setup failure may still allow device registration.

## Test Signals

Tests should cover I2C and SPI regmap address mappings, regulator enable failures, power/reset read-state loops, exact scale/filter write matching, direct raw sign extension, DRDY interrupt polling, triggered buffer reads, suspend/resume, and fault injection for bulk-read failure in the trigger handler.
