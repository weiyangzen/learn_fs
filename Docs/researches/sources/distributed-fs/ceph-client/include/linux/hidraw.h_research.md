# sources/distributed-fs/ceph-client/include/linux/hidraw.h

## Purpose
`hidraw.h` defines the in-kernel structures and entry points for the hidraw character device interface. Hidraw exposes raw HID reports to userspace without input-layer interpretation.

## Important APIs, Types, And Functions
`struct hidraw` tracks a minor, existence/open counters, wait queue, underlying `hid_device`, device node, list lock, and open reader list. `struct hidraw_report` stores a report buffer and length. `struct hidraw_list` is per-open-file state with a ring buffer of `HIDRAW_BUFFER_SIZE` reports, head/tail, fasync pointer, backpointer, list node, read mutex, and revoked flag. With `CONFIG_HIDRAW`, functions include `hidraw_init()`, `hidraw_exit()`, `hidraw_report_event()`, `hidraw_connect()`, and `hidraw_disconnect()`; otherwise stubs compile away the feature.

## Control Flow And State
HID core connects hidraw during device setup, forwards raw input reports via `hidraw_report_event()`, and disconnects during teardown. Per-file ring buffers retain reports until userspace reads them. The revoked flag and existence state prevent further use after disconnect. Raw feature/output requests from userspace flow through HID core low-level request paths and may be visible to HID-BPF as file-sourced operations.

## Dependencies And Integration Points
It includes `uapi/linux/hidraw.h` and references HID core structures. It integrates with `hid_device.hidraw`, `HID_CLAIMED_HIDRAW`, character devices, fasync, wait queues, and BPF source tracking for hidraw-originated requests.

## Risks
Risks include report buffer lifetime, ring overflow policy, disconnect races with blocking readers, fasync notification ordering, and leaking raw reports from devices that should be ignored or claimed only by special drivers. Disabled-config stubs make `hidraw_connect()` fail with `-1`.

## Test Signals
Exercise hidraw open/read/poll/fasync, raw descriptor and report ioctls from userspace, disconnect while open, large reports near `HID_MAX_BUFFER_SIZE`, multiple readers, and builds with `CONFIG_HIDRAW=n`.
