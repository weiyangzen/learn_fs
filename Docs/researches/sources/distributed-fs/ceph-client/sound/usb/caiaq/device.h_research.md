# sources/distributed-fs/ceph-client/sound/usb/caiaq/device.h

## Purpose
Defines CAIAQ/Native Instruments product ids, endpoint command constants, device specification format, central runtime state, and command helper prototypes.

## Important APIs, Types, and Functions
Important definitions include `USB_VID_NATIVEINSTRUMENTS`, product ids for RigKontrol, Kore, Audio DJ, Traktor, and Maschine devices, `EP1_BUFSIZE`, `EP4_BUFSIZE`, `MAX_STREAMS`, EP1 command ids, `struct caiaq_device_spec`, `struct snd_usb_caiaqdev`, `struct snd_usb_caiaq_cb_info`, `caiaqdev()` and `caiaqdev_to_dev()` macros, plus EP1 command helper prototypes.

## Control Flow
No executable logic. The packed `caiaq_device_spec` is filled from an EP1 GET_DEVICE_INFO reply and drives audio/MIDI/input initialization.

## State and Persistence
`snd_usb_caiaqdev` is the persistent per-card state. It includes command URBs/buffers, audio stream arrays, panic flags, control state, optional input device, rawmidi and PCM handles, and product strings.

## Dependencies and Integration Points
Includes `../usbaudio.h`, embedding the generic `snd_usb_audio` as the first field. Used by every CAIAQ source file.

## Risks
The struct is large and cross-module; lifetime is tied to ALSA card private data. Arrays are sized by `MAX_STREAMS` and require runtime validation before indexing. Optional input fields exist only under config guard, so code must keep guards aligned.

## Test Signals
Compile CAIAQ with input enabled/disabled and run probe tests that verify spec-derived stream counts stay within `MAX_STREAMS`.
