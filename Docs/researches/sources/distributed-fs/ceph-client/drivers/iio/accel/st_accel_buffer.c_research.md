# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_buffer.c

Purpose: triggered-buffer support for the shared ST accelerometer driver.

Important APIs/types/functions: `st_accel_trig_set_state()` enables or disables the common ST data-ready IRQ through `st_sensors_set_dataready_irq()`. `st_accel_buffer_postenable()` restricts enabled axes to the active scan mask and powers the sensor on. `st_accel_buffer_predisable()` powers the sensor off and restores all axes. `st_accel_allocate_ring()` installs a devm triggered buffer using the common `st_sensors_trigger_handler()`.

Control flow: when a buffer is enabled, IIO calls `postenable`, which programs the axis mask first and then enables the sensor. If enabling fails, it restores all axes before returning the error. When the buffer is disabled, IIO calls `predisable`, which powers the device off and re-enables all axes for direct reads. Trigger state changes go directly to the shared ST IRQ helper.

State and persistence behavior: no private state is stored in this file. It mutates device registers through shared ST sensor helpers for axis selection, power state, and data-ready IRQ state. The register settings persist until another helper call changes them.

Dependencies and integration points: depends on IIO buffer/triggered-buffer APIs and the ST common sensor helpers. The core probe calls `st_accel_allocate_ring()` and passes `ST_ACCEL_TRIGGER_SET_STATE` into trigger allocation when an IRQ is present.

Risks: active scan masks are represented as `indio_dev->active_scan_mask[0]`; this assumes the three accelerometer axes fit in the first mask word. Error recovery only restores axes when power-on fails, not if axis programming fails. Buffer state transitions depend on the common ST helper semantics for power and axis registers.

Test signals: enable buffers with all axes and subsets, verify axis-enable register programming, test power-on failure cleanup, disable buffers and confirm all axes are restored, and validate IRQ trigger enable/disable on boards with a data-ready interrupt.
