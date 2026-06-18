# sources/distributed-fs/ceph-client/sound/usb/caiaq/audio.h

## Purpose
Declares CAIAQ audio lifecycle hooks.

## Important APIs, Types, and Functions
Exports declarations for `snd_usb_caiaq_audio_init()`, `snd_usb_caiaq_audio_disconnect()`, and `snd_usb_caiaq_audio_free()`.

## Control Flow
No executable logic. `device.c` calls these during setup, disconnect, and card free.

## State and Persistence
No state in header.

## Dependencies and Integration Points
Requires `struct snd_usb_caiaqdev` from `device.h` to be visible before use.

## Risks
Call order matters: disconnect should stop streams before free releases URBs.

## Test Signals
Build coverage and disconnect/free lifecycle tests.
