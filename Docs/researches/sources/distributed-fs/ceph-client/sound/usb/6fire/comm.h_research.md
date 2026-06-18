# sources/distributed-fs/ceph-client/sound/usb/6fire/comm.h

## Purpose
Defines the 6Fire communication runtime interface shared by command, MIDI, control, and chip lifecycle code.

## Important APIs, Types, and Functions
Declares `COMM_RECEIVER_BUFSIZE = 64`, `struct comm_runtime`, and lifecycle functions `usb6fire_comm_init()`, `usb6fire_comm_abort()`, and `usb6fire_comm_destroy()`. The runtime struct exposes `init_urb`, `write8`, and `write16` callbacks.

## Control Flow
No executable logic. Other modules dereference function pointers after `usb6fire_comm_init()` succeeds.

## State and Persistence
The struct owns a receive URB and buffer, a chip pointer, serial byte, and command/MIDI helper callbacks. It persists until card private free calls destroy.

## Dependencies and Integration Points
Includes `common.h`. `midi.c` uses `init_urb`; `control.c` uses `write8`/`write16`; `chip.c` owns lifetime.

## Risks
The `write16` parameter names are reversed from the implementation's low/high order, creating maintenance risk. Since function pointers are optional by convention but not null-checked by all callers, init ordering must keep comm first.

## Test Signals
Compile and runtime smoke tests should confirm control rate writes and MIDI URB init use the expected byte order and that no caller uses comm before initialization.
