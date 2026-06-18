# sources/distributed-fs/ceph-client/drivers/media/usb/au0828/Makefile

## Purpose
Composes the AU0828 module from core, I2C, card, DVB, optional analog, optional VBI, and optional RC objects.

## Important APIs, types, and functions
Always links `au0828-core.o`, `au0828-i2c.o`, `au0828-cards.o`, and `au0828-dvb.o`. Adds `au0828-video.o` and `au0828-vbi.o` when `CONFIG_VIDEO_AU0828_V4L2=y`; adds `au0828-input.o` when `CONFIG_VIDEO_AU0828_RC=y`. Emits `au0828.o` for `CONFIG_VIDEO_AU0828`.

## Control flow and state
No runtime flow exists. Object inclusion controls which external functions in `au0828.h` are real versus inline stubs.

## Dependencies and integration points
Adds include paths for media tuners and DVB frontends, required by card setup and DVB attach logic. Integrates with kbuild and optional `extra-cflags-y/m`.

## Risks and test signals
Risks are unresolved symbols if config guards and object inclusion diverge. Test signals are clean builds with analog/RC enabled and disabled, and no missing include errors for tuner/frontend headers.
