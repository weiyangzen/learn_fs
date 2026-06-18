# sources/distributed-fs/ceph-client/include/uapi/linux/joystick.h

## Purpose
`joystick.h` defines the legacy Linux joystick character-device ABI for event reads, device metadata, correction data, axis/button mappings, and old calibration structures.

## Important APIs, Types, and Functions
`struct js_event` carries timestamp, signed value, event type, and axis/button number. Event type bits identify button, axis, and init events. Ioctls fetch version, axes, buttons, name, correction data, axis map, and button map; some ioctls set correction and mappings. `struct js_corr` describes correction coefficients. Legacy structures `JS_DATA_TYPE`, `JS_DATA_SAVE_TYPE_32`, and `JS_DATA_SAVE_TYPE_64` support old API calibration.

## Control Flow
Userspace reads a stream of `js_event` records from `/dev/input/js*`, uses ioctls to discover device shape, and optionally updates correction or mapping tables. The input subsystem translates raw input events into joystick ABI records.

## State and Persistence
Axis/button maps and correction values are kernel device state, usually per open device and not durable across removal/reboot unless userspace reapplies them. Event queues are transient.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/input.h>`. Integration points include evdev/input drivers, compatibility with old joystick applications, and game/controller calibration tools.

## Risks and Test Signals
Tests should cover struct sizes, event stream ordering, init events, ioctl buffer lengths, `JSIOCGNAME(len)` variable sizing, correction math boundaries, and 32/64-bit legacy save structure compatibility.
