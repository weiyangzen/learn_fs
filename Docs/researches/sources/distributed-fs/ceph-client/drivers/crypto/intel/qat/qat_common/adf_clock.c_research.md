# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_clock.c

## Purpose
This file measures QAT accelerator-engine clock frequency by synchronizing with firmware timestamp counters over the admin interface. Older Gen2 devices use this to calibrate heartbeat timestamp behavior.

## Important APIs, Types, And Functions
The public API is `adf_dev_measure_clock()`. Internal helpers include `timespec_to_us()`, `timespec_to_ms()`, and `measure_clock()`. Constants define retry count, delay, ME clock divider, and acceptable time delta threshold.

## Control Flow
`measure_clock()` reads system monotonic time, sends an admin timestamp sync, waits 10 ms, reads firmware timestamp, reads system time again, and computes frequency from firmware counter delta and elapsed time if the measurement window is stable. `adf_dev_measure_clock()` retries up to 10 times and validates that the resulting frequency lies within caller-provided min/max bounds.

## State And Persistence Behavior
No state is stored here. Callers store the measured frequency in `hw_device->clock_frequency`.

## Dependencies And Integration Points
It depends on admin timestamp commands, Linux timekeeping, delays, and device logging. C3xxx/C62x hardware data calls it during setup.

## Risks
System scheduling jitter can make measurements fail; the threshold controls this. Admin communication must already be functional. Wrong min/max bounds reject valid hardware or accept bad measurements.

## Test Signals
Clock measurement on Gen2 devices, retry behavior under load, failure with broken admin firmware, and heartbeat timing stability validate this file.
