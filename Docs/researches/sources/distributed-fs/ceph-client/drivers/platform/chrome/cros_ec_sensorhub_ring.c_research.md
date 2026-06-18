# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub_ring.c

## Purpose
`cros_ec_sensorhub_ring.c` implements Chrome EC motion-sense FIFO processing. It registers per-sensor push callbacks, enables/disables EC FIFO interrupts, drains FIFO events from MKBP notifications, reconstructs sample timestamps across EC/AP timebases, handles batching and lost samples, and forwards samples into IIO sensor drivers.

## Important APIs, Types, and Functions
- `cros_ec_sensorhub_register_push_data()` and `cros_ec_sensorhub_unregister_push_data()` manage per-sensor callbacks.
- `cros_ec_sensorhub_ring_fifo_enable()` sends `MOTIONSENSE_CMD_FIFO_INT_ENABLE` and resets tight timestamp batch state.
- Timestamp helpers include `cros_ec_sensor_ring_median()`, `cros_ec_sensor_ring_ts_filter_update()`, `cros_ec_sensor_ring_ts_filter()`, and `cros_ec_sensor_ring_fix_overflow()`.
- `cros_ec_sensor_ring_process_event()` transforms raw EC FIFO entries into `cros_ec_sensors_ring_sample` records.
- `cros_ec_sensor_ring_spread_add()` and `_legacy()` distribute batched samples in time.
- `cros_ec_sensorhub_ring_handler()` drains FIFO data via `MOTIONSENSE_CMD_FIFO_READ`.
- `cros_ec_sensorhub_event()` is the notifier callback for `EC_MKBP_EVENT_SENSOR_FIFO`.
- `cros_ec_sensorhub_ring_allocate()`, `cros_ec_sensorhub_ring_add()`, and `cros_ec_sensorhub_ring_remove()` own allocation, notifier registration, FIFO enable, and cleanup.

## Control Flow
When `cros_ec_get_next_event()` stores a sensor FIFO MKBP event, the Chrome EC notifier calls `cros_ec_sensorhub_event()`. The notifier validates event type/size, ignores events queued during suspend, copies FIFO info and the IRQ timestamp, then calls the ring handler. The handler locks the shared command buffer, optionally refreshes FIFO info if lost samples are reported, validates count/size against the allocated ring, reads FIFO entries in chunks, converts each raw entry into an output sample, unlocks, reports lost vectors, spreads timestamps, and invokes registered per-sensor callbacks.

## State and Persistence
Ring state lives in `struct cros_ec_sensorhub`: FIFO info buffer, ring sample array, FIFO size, per-sensor push callback array, notifier block, command mutex, last/new timestamps, overflow tracking for EC sample and FIFO timestamps, optional tight-timestamp filter state, per-sensor batch state, and future-timestamp analytics counters. State persists for the platform device lifetime and is reset selectively when FIFO interrupts are toggled or ODR/lost-sample events invalidate interpolation history.

## Dependencies and Integration Points
The file depends on IIO device pointers for callback dispatch, Chrome EC motion-sense command definitions, notifier chains from the EC core, `cros_ec_get_time_ns()`, and tracepoints from `cros_ec_sensorhub_trace.h`. Sensor child drivers integrate by registering push callbacks for their sensor number.

## Risks and Edge Cases
Timestamping is the highest-risk area. The driver must translate 32-bit EC microsecond timestamps into AP nanoseconds, account for wraparound, filter IRQ latency jitter, prevent future timestamps from escaping, and spread batched samples without inventing impossible ordering. Tight timestamp spreading can drop samples when no previous batch period exists. FIFO count/size mismatches, zero reads, too many entries, or EC read errors abort the current drain. Callback registration rejects duplicate sensor slots but does not serialize with unregister beyond normal driver lifetime assumptions.

## Test Signals
There is no local unit test for the ring algorithms in this subset. Useful signals are trace events (`cros_ec_sensorhub_timestamp`, `data`, `filter`), warnings for lost/future samples, and end-to-end IIO sample delivery from EC FIFO events. The code is structured with pure-ish helpers that could be KUnit-tested for median selection, overflow correction, and timestamp spreading.
