# `sources/distributed-fs/ceph-client/include/linux/iio/common/inv_sensors_timestamp.h`

Purpose: timestamp estimation state machine for Invensense sensors, compensating for chip clock period, jitter, interrupts, ODR changes, and FIFO batching.

Important APIs/types/functions: `struct inv_sensors_timestamp_chip`, interval and accumulator structs, `struct inv_sensors_timestamp`, init, ODR update, interrupt update, `inv_sensors_timestamp_pop`, ODR apply, and reset.

Control flow and state: persistent timestamp state tracks chip period bounds, interrupt interval, last sample timestamp, current/new multipliers, measured period, and an accumulator of chip-period measurements. Interrupt handler updates intervals based on sample count; `pop` advances by current period per sample; ODR apply handles pending ODR changes.

Dependencies/integration: uses fixed-width integer types and is consumed by Invensense IIO drivers with FIFO and interrupt streams.

Risks: timestamp drift if jitter bounds or initial period are wrong; ODR changes during FIFO batches require careful `fifo_no` handling; reset clears interval/timestamp but not chip config; 64-bit timestamp arithmetic must avoid underflow/overflow.

Test signals: regular interrupt sample cadence, jittered interrupts, FIFO batches, ODR changes mid-stream, reset behavior, and long-duration drift checks.
