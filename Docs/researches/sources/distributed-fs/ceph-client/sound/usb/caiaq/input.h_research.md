# sources/distributed-fs/ceph-client/sound/usb/caiaq/input.h

## Purpose
Declares optional CAIAQ Linux input support hooks.

## Important APIs, Types, and Functions
Provides `snd_usb_caiaq_input_dispatch()`, `snd_usb_caiaq_input_init()`, `snd_usb_caiaq_input_disconnect()`, and `snd_usb_caiaq_input_free()`.

## Control Flow
No executable logic. `device.c` calls these only under `CONFIG_SND_USB_CAIAQ_INPUT`.

## State and Persistence
No header-owned state.

## Dependencies and Integration Points
Requires `struct snd_usb_caiaqdev` from `device.h`. Tied to CAIAQ Makefile and Kconfig input option.

## Risks
Callers must keep init/disconnect/free order correct when input is compiled in. Header lacks a trailing comment on `#endif`, but functional impact is none.

## Test Signals
Build with input enabled and disabled; runtime input device registration/unregistration.
