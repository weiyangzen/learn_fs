# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_buffer.c

## Purpose
Triggered-buffer glue for ST gyroscope common driver.

## Important APIs, Types, And Functions
Exports `st_gyro_trig_set_state` and `st_gyro_allocate_ring`. Buffer setup ops are `st_gyro_buffer_postenable` and `st_gyro_buffer_predisable`.

## Control Flow
Postenable applies the active scan mask to hardware axes, enables the sensor, and restores all axes if enable fails. Predisable disables the sensor and restores all axes. Trigger state delegates data-ready IRQ enablement to ST sensor common code. Ring allocation uses `devm_iio_triggered_buffer_setup` with `st_sensors_trigger_handler`.

## State And Persistence
Hardware state affected here is axis-enable mask, sensor enable bit, and data-ready IRQ state. No file-local persistent state.

## Dependencies And Integration Points
Depends on IIO buffers/triggers and ST sensors common helpers such as `st_sensors_set_axis_enable`, `st_sensors_set_enable`, `st_sensors_set_dataready_irq`, and `st_sensors_trigger_handler`.

## Risks
Buffer enable failures can leave axes temporarily restricted if restore fails. Active scan mask assumptions must match the three-axis channel table. Built only when `CONFIG_IIO_BUFFER` is enabled.

## Test Signals
Enable buffers with different scan masks, verify axis mask programming and restore on disable, toggle trigger state, and test failure injection in sensor enable paths.
