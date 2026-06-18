
# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_sensorhub.h

## Purpose
This header describes the ChromeOS EC MEMS sensor hub platform interface. It connects EC motion-sense FIFO commands to Linux IIO sensor devices, timestamp correction, batching, overflow handling, and push callbacks.

## Important APIs And Types
`struct cros_ec_sensor_platform` maps an IIO sensor child to an EC sensor id. `cros_ec_sensorhub_push_data_cb_t` is the per-sensor callback used to push a 3-axis sample and AP-domain timestamp into an IIO device. `struct cros_ec_sensors_ring_sample` stores packed FIFO samples. Timestamp state is split into EC overflow state, median filter history (`cros_ec_sensors_ts_filter_state`), and per-sensor batch state (`cros_ec_sensors_ts_batch_state`). `struct cros_ec_sensorhub` aggregates the EC device, reusable `cros_ec_command`, motion-sense params/response pointers, command mutex, MKBP notifier, FIFO ring, timestamp slots, FIFO info, overflow/filter state, future timestamp statistics, and per-sensor push callback table. Public functions register/unregister push callbacks, allocate/add/remove the ring, and enable FIFO interrupts.

## Control Flow, State, And Persistence
Sensorhub control flow is event-driven: EC MKBP/FIFO notifications trigger FIFO reads through the shared command buffer; ring samples are timestamp-corrected, batched, and dispatched to registered IIO callbacks. The state is runtime-only and maintained in memory: timestamp filter history, overflow offsets, batch metadata, FIFO sizing, and future timestamp clamp statistics. No disk persistence exists.

## Dependencies And Integration Points
The header depends on `ktime`, mutexes, notifiers, ChromeOS EC motion-sense ABI, and IIO forward declarations. Integration points are the ChromeOS EC core notifier chain, IIO sensor drivers, motion sense commands in `cros_ec_commands.h`, and power-management paths that enable/disable FIFO interrupts.

## Risks And Test Signals
Risks concentrate around timestamp correctness, EC counter overflow, FIFO overflow/loss accounting, concurrent command-buffer access, unregistering callbacks while events are in flight, and future timestamps that must be clamped. Test signals include FIFO enable/disable round trips, ring allocation bounds, per-sensor callback registration, batched sample ordering, overflow repair tests, median timestamp filter behavior under jitter, and IIO sample timestamps staying monotonic.
