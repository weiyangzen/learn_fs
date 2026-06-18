# sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/inv_sensors_timestamp.c

Purpose: common timestamp estimator for InvenSense sensors, especially FIFO devices where interrupt timing, sensor output data rate, chip clock jitter, and ODR changes must be reconciled into per-sample timestamps.

Important APIs, types, and functions: `inv_sensors_timestamp_init()` initializes chip parameters, jitter min/max, multiplier, period, and theoretical chip period accumulator. `inv_sensors_timestamp_update_odr()` records a pending ODR multiplier change and optionally applies it immediately when FIFO is off. `inv_sensors_timestamp_interrupt()` updates interrupt interval bounds, estimates chip period from sample count, initializes or aligns the next sample timestamp, and tolerates invalid intervals. `inv_sensors_timestamp_apply_odr()` applies pending ODR changes and recomputes timestamp alignment using FIFO period/count/sample index. Internal helpers update rolling accumulators, validate measured periods against jitter bounds, update chip period, and align timestamps toward interrupt timestamps.

Control flow: a concrete driver initializes once, calls update when ODR changes, calls interrupt on FIFO interrupts with sample count and timestamp, calls apply ODR at a known sample position, then advances `ts->timestamp` by `ts->period` while emitting samples.

State and persistence: all mutable state lives in caller-owned `struct inv_sensors_timestamp`: chip constants, min/max period, multiplier, pending multiplier, rolling chip-period accumulator, interrupt interval, current timestamp, and period. It is volatile runtime state.

Dependencies and integration: depends on math64/kernel helpers and the public IIO InvenSense timestamp header. Exports GPL namespace `IIO_INV_SENSORS_TIMESTAMP`.

Risks and test signals: period validation excludes boundary equality, so borderline jitter values are rejected. ODR changes while FIFO active return `-EAGAIN` if one is pending. Tests should cover initialization math, rolling average with empty slots, invalid interrupt intervals, first interrupt initialization, timestamp alignment drift, FIFO ODR change alignment, and zero sample count no-op.
