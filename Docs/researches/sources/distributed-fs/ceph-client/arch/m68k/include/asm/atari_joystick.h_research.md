<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_joystick.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_joystick.h

## Purpose
This header declares the Atari joystick driver interface and shared joystick state structure.

## Important APIs, Types, And Functions
- `atari_joystick_interrupt(char *)` consumes interrupt data from the Atari keyboard/IKBD path.
- `atari_joystick_init()` initializes joystick support.
- `atari_mouse_buttons` exposes mouse button state shared with input handling.
- `struct joystick_status` stores fire/direction data, readiness/activity flags, and a wait queue for blocking readers.

## Control Flow
IKBD input code calls the interrupt handler with device bytes. The driver updates `joystick_status` and wakes waiters. Initialization registers the device/input path.

## State And Persistence Behavior
State persists in driver-owned `joystick_status` instances and `atari_mouse_buttons`. The header only defines the shape and entry points.

## Dependencies And Integration Points
It depends on wait queue types being visible to includers and integrates with Atari keyboard, mouse, joystick, and input drivers.

## Risks And Edge Cases
The interrupt byte buffer has an untyped `char *` interface, so length and packet interpretation must be controlled by the caller. Shared mouse button state can race unless protected by driver locking.

## Test Signals
Joystick event delivery, blocking read wakeups, mouse button state updates, initialization success, and IKBD interrupt packet parsing validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/atari_joystick.h -->
