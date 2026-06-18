# sources/distributed-fs/ceph-client/sound/usb/6fire/chip.h

## Purpose
Declares the shared 6Fire per-device state container.

## Important APIs, Types, and Functions
`struct sfire_chip` holds `usb_device`, `snd_card`, interface count, registration index, shutdown flag, and pointers to `midi_runtime`, `pcm_runtime`, `control_runtime`, and `comm_runtime`.

## Control Flow
No executable logic. The struct fields are populated in `chip.c` and consumed by every 6fire submodule.

## State and Persistence
The struct persists as ALSA card private data until `snd_card_free_when_closed()`. `shutdown` gates URB resubmission in `comm.c`, while component pointers gate abort/destroy calls.

## Dependencies and Integration Points
Includes `common.h` for forward declarations and core USB/ALSA includes. All 6fire implementation files include this header to access cross-module state.

## Risks
The struct is the ownership hub; dangling component pointers or use after card free are primary risks. Any new component must follow the existing init/destroy pointer discipline.

## Test Signals
Compile coverage is most important. Runtime tests should observe that component pointers are null after destroy and that disconnect sets `shutdown` before URB abort.
