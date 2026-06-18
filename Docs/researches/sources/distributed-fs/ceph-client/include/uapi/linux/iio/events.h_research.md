
# sources/distributed-fs/ceph-client/include/uapi/linux/iio/events.h

## Purpose

`iio/events.h` defines the Industrial I/O event delivery ABI, including event data layout, event-fd ioctl, and bit extraction helpers for packed event identifiers. The complete 43-line file was read.

## Important APIs, Types, and Functions

The key structure is `iio_event_data` with `id` and `timestamp`. It defines `IIO_GET_EVENT_FD_IOCTL` and macros to extract event type, direction, channel type, channel numbers, modifier, and differential flag from a packed event code.

## Control Flow

User space obtains an event fd via ioctl and reads `iio_event_data` records. The extraction macros decode the `id` field into semantic components supplied by IIO drivers.

## State and Persistence Behavior

The header owns no state. Event queues and timestamps are maintained in kernel IIO devices and exposed through the event fd.

## Dependencies and Integration Points

It includes `linux/ioctl.h` and `linux/types.h`, and integrates with IIO event-capable drivers and `iio/types.h` enum values.

## Risks and Edge Cases

Packed bit layouts are ABI. Risks include sign extension for 16-bit channel extraction, stale assumptions about event type-specific channel numbering, timestamp source consistency, and invalid user buffers.

## Test Signals

Tests should validate ioctl event-fd creation, event read format, extraction macro results for constructed IDs, timestamp ordering, and invalid/closed device behavior.
