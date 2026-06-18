# sources/distributed-fs/ceph-client/samples/uhid/uhid-example.c

## Purpose

This user-space example creates a virtual HID device through `/dev/uhid`: a three-button mouse with wheel and LED output report handling.

## Important APIs, Types, and Functions

It defines a HID report descriptor `rdesc`, helper `uhid_write()`, lifecycle functions `create()` and `destroy()`, event reader `event()`, output parser `handle_output()`, input sender `send_event()`, keyboard handler `keyboard()`, and `main()`. It uses `struct uhid_event`, `UHID_CREATE`, `UHID_DESTROY`, `UHID_INPUT`, `UHID_OUTPUT`, `poll`, `termios`, and global button/movement state.

## Control Flow

`main()` puts stdin in noncanonical mode, opens `/dev/uhid` or a supplied path, creates the virtual device, and polls stdin plus the UHID fd. Keyboard commands toggle buttons or set relative movement/wheel deltas and call `send_event()`. UHID events from the kernel are logged; output reports for report id 2 are decoded as LED flags. On exit or error, the program sends `UHID_DESTROY`.

## State and Persistence Behavior

Global booleans track button state, and signed chars hold one-shot movement/wheel deltas reset after each event. The virtual HID device persists until destroyed or the fd closes.

## Dependencies and Integration Points

It depends on UHID, input/HID subsystems, terminal stdin, and access to `/dev/uhid`. Resulting devices integrate with evdev and HID debugfs.

## Risks and Edge Cases

The code modifies terminal mode without restoring the original state. `uhid_write()` compares short write size against `sizeof(ev)`, which is size of pointer in the diagnostic expression, though the earlier `ret != sizeof(*ev)` check is correct. Running creates a real input device.

## Test Signals

Run as permitted user, observe a new HID/evdev mouse, press movement/button keys, verify pointer/input events, and write LED events through evdev to see output reports logged.
