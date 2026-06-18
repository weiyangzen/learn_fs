# sources/distributed-fs/ceph-client/drivers/iio/industrialio-triggered-event.c

## Purpose
`industrialio-triggered-event.c` is a small helper for drivers that generate IIO events from a trigger-driven poll function. It allocates `indio_dev->pollfunc_event` and marks the IIO device as supporting triggered events.

## Important APIs, types, and functions
- `iio_triggered_event_setup()` allocates a pollfunc using `iio_alloc_pollfunc()` with `IRQF_ONESHOT`, names it from the IIO device name and ID, stores it in `indio_dev->pollfunc_event`, and sets `INDIO_EVENT_TRIGGERED`.
- `iio_triggered_event_cleanup()` clears `INDIO_EVENT_TRIGGERED` and frees the pollfunc with `iio_dealloc_pollfunc()`.

## Control flow
Drivers call setup after fully initializing `indio_dev` but before registration. During later trigger selection in `industrialio-trigger.c`, devices with `INDIO_EVENT_TRIGGERED` attach `pollfunc_event` to the selected trigger. On driver cleanup, the driver calls `iio_triggered_event_cleanup()` to free the allocated pollfunc and clear the mode bit.

## State and persistence behavior
The helper mutates only `indio_dev->pollfunc_event` and `indio_dev->modes`. It has no hardware or persistent state. The allocated pollfunc owns a formatted name string and callback pointers until cleanup.

## Dependencies and integration points
The file depends on IIO trigger consumer helpers, trigger-core pollfunc allocation, and drivers that push events from their pollfunc thread or top half. It integrates with trigger selection through `INDIO_EVENT_TRIGGERED`.

## Risks
- Cleanup assumes setup succeeded and `pollfunc_event` is valid; drivers should pair calls carefully.
- Calling setup before `indio_dev->name` or ID is meaningful would produce poor pollfunc names, though the function expects a completely initialized unregistered device.
- The helper does not attach to a trigger itself; drivers still need normal IIO registration and trigger selection.

## Test signals
- Driver probe/remove tests should verify setup failure on allocation, mode bit set/cleared, and no pollfunc leak.
- Integration tests should select a trigger on a triggered-event device and confirm event pollfunc attach/detach through the trigger core.
