# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_buffer.c

## Purpose
Buffered capture support for the common ST magnetometer driver.

## Important APIs, Types, And Functions
`st_magn_trig_set_state()` toggles the common ST data-ready IRQ through `st_sensors_set_dataready_irq()`. `st_magn_buffer_postenable()` and `st_magn_buffer_predisable()` enable and disable the sensor around buffer use. `st_magn_allocate_ring()` installs a devm-managed triggered buffer using the common `st_sensors_trigger_handler`.

## Control Flow
The ST common probe calls `st_magn_allocate_ring()`. When userspace enables the IIO buffer, postenable powers measurements on; when disabled, predisable powers them off. Trigger state changes are delegated to common ST sensor IRQ handling.

## State And Persistence
No private state. It mutates device enable and data-ready IRQ state through `struct st_sensor_data` owned by the IIO device.

## Dependencies And Integration Points
Integrates IIO triggered buffers, IIO triggers, and `linux/iio/common/st_sensors.h`. It is conditional through declarations in `st_magn.h`.

## Risks And Test Signals
The buffer path relies on common ST helpers matching channel layout and scan ordering. Test buffer enable/disable, trigger attachment, IRQ toggling, and direct reads before and after buffered capture.
