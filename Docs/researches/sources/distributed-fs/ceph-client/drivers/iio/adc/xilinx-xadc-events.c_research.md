# sources/distributed-fs/ceph-client/drivers/iio/adc/xilinx-xadc-events.c

## Purpose
This companion file implements the XADC IIO event ABI used by `xilinx-xadc-core.c`. It maps hardware alarm bits to IIO channels, pushes threshold events, and reads/writes threshold and hysteresis values while keeping `struct xadc` alarm state synchronized with hardware configuration.

## Important APIs, Types, And Functions
The exported callbacks are `xadc_handle_events()`, `xadc_read_event_config()`, `xadc_write_event_config()`, `xadc_read_event_value()`, and `xadc_write_event_value()`. Internal helpers `xadc_event_to_channel()`, `xadc_get_threshold_offset()`, and `xadc_get_alarm_mask()` translate between XADC threshold numbers, alarm mask bits, channel addresses, and IIO event directions.

## Control Flow
Interrupt handlers in the core pass a normalized event bitmask to `xadc_handle_events()`, which iterates the low eight bits and calls `xadc_handle_event()`. Temperature events are pushed as rising threshold events; voltage events are pushed as either-direction threshold events because the hardware status does not identify upper versus lower threshold cause. Event configuration updates `xadc->alarm_mask`, calls the variant `ops->update_alarm()`, then rewrites `XADC_REG_CONF1` alarm-disable bits while holding `xadc->mutex`.

Threshold reads use the cached `xadc->threshold[]` or `temp_hysteresis` value, right-shifted from the hardware's MSB-aligned representation to the channel realbits. Threshold writes left-shift userspace values back into MSB alignment, validate the 16-bit range, update the cache, and write the corresponding `XADC_REG_THRESHOLD()` register. For temperature hysteresis, the driver stores hysteresis as a relative userspace value but programs the hardware lower threshold as an absolute value derived from the cached upper threshold.

## State And Persistence
This file mutates shared `struct xadc` state: `alarm_mask`, `threshold[16]`, and `temp_hysteresis`. The threshold cache is initialized by the core at probe from hardware registers. All hardware register writes are protected by the XADC mutex and use the lock-asserting `_xadc_*` accessors.

## Dependencies And Integration Points
It depends on the channel order and register definitions in `xilinx-xadc.h`, the `xadc_ops->update_alarm()` implementation selected by the core, and IIO event helper macros. It is not a standalone module; it supplies callbacks referenced from `xadc_info` in the core.

## Risks And Test Signals
A notable risk is channel mapping drift: event-to-channel translation assumes the core channel arrays keep internal supplies in the expected order. The first temperature threshold event is ignored because only over-temperature is handled. Voltage event direction is ambiguous by design. Tests should exercise enable/disable of every alarm-capable channel, rising/falling threshold writes, temperature hysteresis recalculation including hysteresis greater than threshold, event delivery mapping for Zynq and AXI normalized masks, and invalid event info handling.
