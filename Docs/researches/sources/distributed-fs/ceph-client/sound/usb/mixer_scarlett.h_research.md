# sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett.h

## Purpose
`mixer_scarlett.h` declares the first-generation Focusrite Scarlett and Forte mixer creation hooks used by the USB mixer quirk dispatcher.

## Important APIs
- `snd_scarlett_controls_create(struct usb_mixer_interface *mixer)` creates controls for supported first-generation Scarlett interfaces.
- `snd_forte_controls_create(struct usb_mixer_interface *mixer)` creates controls for the Focusrite Forte.

## Control flow and integration
`mixer_quirks.c` includes this header and calls the appropriate function from its USB ID switch. The header has an include guard and expects `struct usb_mixer_interface` to be declared by earlier includes in the translation unit.

## State, dependencies, and risks
The header owns no state and exposes only two function declarations. The primary risk is keeping the dispatcher’s product-ID table aligned with the implementation’s internal USB ID switch: a caller may route a USB ID here that the implementation rejects with `-EINVAL`.

## Test signals
Compile/link coverage verifies symbol consistency. Runtime probe tests should confirm `snd_usb_mixer_apply_create_quirk()` selects this legacy Scarlett/Forte path only for the IDs supported by `mixer_scarlett.c`.
