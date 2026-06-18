# sources/distributed-fs/ceph-client/include/linux/drbd_limits.h

## Purpose
This header centralizes DRBD configuration limits, defaults, and scale units for minors, ports, startup timeouts, network parameters, synchronization, disk sizing, congestion, activity log layout, and feature defaults.

## Important APIs, types, and functions
It defines `*_MIN`, `*_MAX`, `*_DEF`, and `*_SCALE` constants for options such as minor count, port, wait-for-connection timeouts, network timeout, disk timeout, connect interval, ping interval/timeouts, max epoch size, send/receive buffer sizes, max buffers, unplug watermark, KO count, resync rate, activity log extents, minor number, disk size, bio vectors, resync planning rates, congestion fill/extents, AL stripes, socket-check timeout, and resync discard granularity. It also maps defaults to enums from `drbd.h`, such as `DRBD_ON_IO_ERROR_DEF`, `DRBD_FENCING_DEF`, and `DRBD_PROTOCOL_DEF`.

## Control flow, state, and persistence
No control flow is present. These constants define validation and default state for generated netlink policies and DRBD configuration. Some values directly affect persistent on-disk layout, especially activity log extents, stripe count, stripe size, and disk-size constraints.

## Dependencies and integration points
The constants are consumed by `drbd_genl.h`, DRBD configuration parsers, and user-space tools. They depend on policy enums from `drbd.h`.

## Risks and test signals
Risks include accepting nonsensical ranges, changing defaults that alter established behavior, and overflow in unit-scaled values. Tests should validate boundary values, generated policy min/max/default propagation, user-space error messages, and compatibility for historical defaults like discard-zeroes-if-aligned.
