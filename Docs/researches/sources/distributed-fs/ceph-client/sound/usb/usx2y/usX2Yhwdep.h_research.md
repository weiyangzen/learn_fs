<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.h -->
# sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.h

## Purpose
Tiny private header declaring the US-X2Y hwdep creation entry point.

## APIs, Types, and Functions
Declares `int usx2y_hwdep_new(struct snd_card *card, struct usb_device *device);`.

## Control Flow, State, and Persistence
No runtime state or control flow. The declaration allows `usbusx2y.c` to create the firmware/control hwdep device during probe before firmware has initialized the full ALSA device stack.

## Dependencies and Integration
Relies on forward-visible ALSA `struct snd_card` and USB `struct usb_device` types from including source files. Implemented by `usX2Yhwdep.c`.

## Risks and Test Signals
Risk is limited to prototype drift or missing includes in consumers. Build coverage of `usbusx2y.c` and successful hwdep creation during probe validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/usb/usx2y/usX2Yhwdep.h -->
