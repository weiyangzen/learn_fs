# sources/distributed-fs/ceph-client/sound/usb/6fire/control.h

## Purpose
Declares 6Fire mixer/control runtime state and sample-rate constants.

## Important APIs, Types, and Functions
Defines `CONTROL_MAX_ELEMENTS`, six `CONTROL_RATE_*` values plus `CONTROL_N_RATES`, `struct control_runtime`, and lifecycle functions `usb6fire_control_init()`, `usb6fire_control_abort()`, `usb6fire_control_destroy()`.

## Control Flow
No executable logic. PCM code uses the function pointers and rate enum to configure hardware.

## State and Persistence
Runtime fields cache route switches, USB streaming flag, volumes, mute state, and update masks. The `element` array is declared but not actively populated in current `control.c`.

## Dependencies and Integration Points
Includes `common.h`; used by `chip.c`, `control.c`, and `pcm.c`.

## Risks
Enums must stay synchronized with rate tables in `control.c`, `pcm.c`, and endpoint packet sizes in `firmware.c`. The unused `element` array may confuse ownership expectations.

## Test Signals
Build coverage plus runtime sample-rate tests at all six rates are the best signal that enum/table synchronization is intact.
