# sources/distributed-fs/ceph-client/tools/iio/iio_event_monitor.c

## Purpose

`iio_event_monitor.c` is an example and diagnostic program that opens an IIO character device, retrieves its event file descriptor, reads `struct iio_event_data` events, decodes event IDs, and prints readable event descriptions.

## Important APIs and Functions

It uses IIO UAPI headers `<linux/iio/events.h>` and `<linux/iio/types.h>`, plus helpers from `iio_utils.h`. Large lookup tables map channel types, event types, event directions, and modifiers to text. `event_is_known` validates decoded enum values before indexing those tables. `print_event` extracts channel type, modifier, event type, direction, channel numbers, and differential flag with `IIO_EVENT_CODE_EXTRACT_*` macros. `enable_events` scans `<device>/events` for `*_en` attributes and writes enable or disable values. `main` handles `-a`, resolves a device name to `/dev/iio:deviceN`, opens the character device, issues `IIO_GET_EVENT_FD_IOCTL`, closes the main fd, then reads events in a loop.

## State, Dependencies, and Integration

The program's only persistent side effect is optional enabling/disabling of event sysfs knobs when `-a` is used. It depends on IIO sysfs under `/sys/bus/iio/devices`, IIO character devices under `/dev`, and device support for event fds. It integrates with `iio_utils.c` for name lookup and sysfs writes.

## Risks and Test Signals

The event loop is unbounded and exits only on read failure. If the process is killed before normal cleanup after `-a`, enabled event knobs may remain enabled. Event enum coverage must track the UAPI or new event codes print as unknown. Tests should compile against current UAPI, run on devices with and without event support, verify `-a` enables and later disables sysfs attributes, and feed known synthetic event IDs to `event_is_known` and `print_event`.
