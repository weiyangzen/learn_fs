<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_buffer.c

## Purpose
`st_pressure_buffer.c` provides triggered-buffer glue for ST pressure sensors using the generic ST sensors IIO helper layer.

## Important APIs, types, and functions
`st_press_trig_set_state()` forwards trigger enable/disable to `st_sensors_set_dataready_irq()`. Buffer setup ops enable the sensor in `postenable` and disable it in `predisable` through `st_sensors_set_enable()`. `st_press_allocate_ring()` installs a devm triggered buffer using the common `st_sensors_trigger_handler()`.

## Control flow
The core calls `st_press_allocate_ring()` during common probe. When a buffer is enabled, IIO calls the postenable hook to power/enable sampling. Trigger events are handled by the common ST trigger handler. Disabling the buffer powers the sensor down.

## State and persistence behavior
This file stores no state. It mutates hardware enable and data-ready IRQ state through the shared ST sensor data associated with the IIO device.

## Dependencies and integration points
It depends on IIO buffers/triggers and the generic ST sensors common helpers. It is compiled only when buffer support is enabled through the header declarations.

## Risks
Because enable/disable is delegated, regressions usually come from changes in common ST helper semantics. The ring setup uses the parent device for devm lifetime, so parent/child device lifetime must stay as designed.

## Test signals
Enable and disable buffered capture, verify data-ready IRQ masking, confirm sensor power transitions, and build with trigger/buffer configs toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_buffer.c -->
