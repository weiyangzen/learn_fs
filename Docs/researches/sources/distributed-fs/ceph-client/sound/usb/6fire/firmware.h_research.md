# sources/distributed-fs/ceph-client/sound/usb/6fire/firmware.h

## Purpose
Declares the 6Fire firmware readiness API and state constants.

## Important APIs, Types, and Functions
Defines `FW_READY = 0`, `FW_NOT_READY = 1`, and `usb6fire_fw_init(struct usb_interface *intf)`.

## Control Flow
No executable logic. Probe interprets `FW_NOT_READY` as a successful firmware upload that should not register an ALSA card yet.

## State and Persistence
No state in header.

## Dependencies and Integration Points
Includes `common.h`; used by `chip.c` and implemented by `firmware.c`.

## Risks
The distinction between `0` ready and positive `FW_NOT_READY` is part of probe control flow; callers must not treat all nonnegative returns as ready.

## Test Signals
Probe tests should cover both ready and not-ready return paths.
