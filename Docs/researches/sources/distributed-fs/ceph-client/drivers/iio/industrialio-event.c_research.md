# sources/distributed-fs/ceph-client/drivers/iio/industrialio-event.c

## Purpose
`industrialio-event.c` implements IIO event delivery and event-control sysfs. It lets drivers expose event enable/value/label attributes derived from channel event specs, queue detected events into a small FIFO, and provide userspace an event-only anon fd via `IIO_GET_EVENT_FD_IOCTL`.

## Important APIs, types, and functions
- `struct iio_event_interface` stores the event waitqueue, 16-entry `kfifo` of `struct iio_event_data`, dynamic sysfs attribute list, busy flag, sysfs group, read lock, and ioctl handler.
- `iio_push_event()` queues an event and wakes pollers when the event fd is open.
- `iio_event_getfd()` returns an anon inode for event reads, enforces a single open event fd, and resets the FIFO output side on successful open.
- `iio_event_chrdev_read()` performs blocking or nonblocking reads from the event FIFO.
- `iio_ev_state_show/store()` call driver `read_event_config` and `write_event_config`.
- `iio_ev_value_show/store()` call driver `read_event_value` and `write_event_value` with fixed-point formatting/parsing.
- `iio_device_add_event()` and `iio_device_add_event_sysfs()` build event attributes from `iio_event_spec` masks and shared scopes.
- `iio_device_register_eventset()`, `iio_device_wakeup_eventset()`, and `iio_device_unregister_eventset()` manage event subsystem lifetime for an IIO device.

## Control flow
During IIO device registration, the core calls `iio_device_register_eventset()`. If static `event_attrs` exist or any channel has event specs, the function allocates an event interface, initializes the FIFO/waitqueue/read lock, builds dynamic event sysfs attributes for every channel event spec, creates the `events` sysfs group, and registers an ioctl handler. Userspace first opens the normal IIO cdev and issues `IIO_GET_EVENT_FD_IOCTL`; the handler calls `iio_event_getfd()`, which takes `mlock`, sets the busy bit, takes an IIO device reference, creates an anon read-only fd, and resets FIFO output.

Drivers call `iio_push_event()` with an event code and timestamp. Events are silently ignored before registration or when no event fd is open. Reads block until the FIFO contains data or the device is unregistered; poll reports readable when the FIFO is non-empty. Release clears the busy bit and drops the device reference.

Event sysfs names are generated from event type, direction, and info kind, for example threshold rising enable/value names. Enable attributes use config callbacks; all other event info attributes use event value callbacks. Optional event labels use `read_event_label`.

## State and persistence behavior
The event interface is runtime-only. It contains queued event data, the single-open busy bit, dynamic attribute memory, and read serialization. Event enable/value state lives in the hardware or driver state behind the `iio_info` callbacks. Unregister wakes blocked readers so they return `-ENODEV`.

## Dependencies and integration points
This file integrates with the IIO core ioctl handler list, channel event specs, `iio_format_value()`, `iio_str_to_fixpoint()`, anon inodes, `kfifo`, wait queues, sysfs group creation, and driver event callbacks. It depends on core lifetime conventions around `indio_dev->info`.

## Risks
- The FIFO holds only 16 events; `iio_push_event()` drops events silently when full because it only checks whether `kfifo_put()` copied.
- The comment requires callers to avoid concurrent `iio_push_event()` for the same device; drivers must serialize event producers.
- A single event fd is allowed. Userspace expecting multiple independent readers gets `-EBUSY`.
- Event value writes always parse with micro precision; drivers needing different precision must account for that ABI behavior.
- Dynamic event attribute creation relies on valid event type/direction/info enum values and channel metadata.

## Test signals
- Sysfs tests should cover dynamic event attribute names for separate and shared masks, optional labels, enable config callbacks, value callbacks, and invalid callback absence.
- Event fd tests should cover ioctl fd creation, second-open `-EBUSY`, nonblocking empty reads, blocking wakeup, poll, FIFO reset on open, FIFO overflow behavior, and unregister wakeup.
- Driver integration tests should push events before registration, without an event fd, and with an event fd to verify discard versus delivery.
