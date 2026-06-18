
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_trigger.c

## Purpose
`st_sensors_trigger.c` implements common data-ready trigger allocation and IRQ handling for ST sensors. It timestamps hardware IRQs, filters spurious/shared interrupts with sensor status registers, handles edge vs level IRQ behavior, and registers an IIO trigger for each device.

## Important APIs, types, and functions
- `st_sensors_new_samples_available()` checks the configured DRDY status register/mask, or returns true when no status register exists.
- `st_sensors_irq_handler()` is the top half that captures a timestamp and wakes the thread.
- `st_sensors_irq_thread()` polls the IIO trigger, handles spurious IRQs, and loops for missed edge-triggered samples.
- `st_sensors_allocate_trigger()` allocates/registers the trigger, configures active-low interrupt polarity when supported, requests the threaded IRQ, and attaches the trigger to the IIO device.
- `st_sensors_validate_device()` enforces trigger ownership.
- Both public helpers are exported in namespace `IIO_ST_SENSORS`.

## Control flow
Sensor-specific drivers call `st_sensors_allocate_trigger()` with trigger ops. The helper creates a trigger, examines the IRQ trigger type, may program active-low polarity through `st_sensors_write_data_with_mask()`, rejects edge IRQs without a DRDY status register, adds `IRQF_ONESHOT` for level IRQs, adds `IRQF_SHARED` for open-drain lines with status checking, requests the threaded IRQ, registers the trigger, and stores it on `indio_dev`. At runtime, top half timestamps and bottom half checks whether this sensor has data; if so it calls `iio_trigger_poll_nested()`.

## State and persistence behavior
It updates `struct st_sensor_data` fields `trig`, `hw_timestamp`, and `edge_irq`, and relies on `hw_irq_trigger` set by `st_sensors_set_dataready_irq()`. It may persistently program interrupt active-low bits in the sensor.

## Dependencies and integration points
This file depends on IIO trigger APIs, IRQ APIs, regmap reads, `st_sensors_core.h`, and ST settings structures. It integrates with `st_sensors_buffer.c` through the trigger handler and with `st_sensors_core.c` for DRDY enable/polarity configuration.

## Risks and edge cases
- Edge IRQ mode is rejected without a status register; board firmware must use level interrupts or provide correct status metadata.
- The edge-mode loop can behave like polling at very high sample rates, increasing IRQ thread CPU time.
- Open-drain shared IRQ is only enabled when a status register exists; otherwise shared interrupt setups can misattribute events.
- Unsupported IRQ trigger types are forced to rising edge, which may hide firmware mistakes until runtime.

## Test signals
Test rising/falling/high/low IRQ firmware configurations, open-drain shared IRQ behavior, edge-triggered missed-sample loop, spurious IRQ return paths, and validation that a trigger cannot be attached to a different IIO device.
