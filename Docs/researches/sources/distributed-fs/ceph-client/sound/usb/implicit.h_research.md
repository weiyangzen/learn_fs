# sources/distributed-fs/ceph-client/sound/usb/implicit.h

## Purpose
Declares implicit-feedback detection and sync-format selection APIs.

## APIs and Integration
`snd_usb_parse_implicit_fb_quirk()` is called during format discovery to annotate an `audioformat` with implicit sync endpoint details. `snd_usb_find_implicit_fb_sync_format()` is called during PCM setup to find a compatible sync-side `audioformat` for selected hw params and to report fixed-rate behavior.

## State, Dependencies, and Risks
Callers must pass initialized USB-audio chip, format, descriptors, and hw params. The implementation mutates format state and may set quirk flags. Misuse can produce unlinked or incorrectly linked sync endpoints.

## Test Signals
Compile coverage and implicit-feedback full-duplex playback/capture tests validate the API.
