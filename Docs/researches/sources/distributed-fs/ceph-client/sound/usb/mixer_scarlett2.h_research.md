# sources/distributed-fs/ceph-client/sound/usb/mixer_scarlett2.h

## Purpose

`mixer_scarlett2.h` is the private declaration header for the Focusrite Scarlett 2 protocol mixer implementation. It exposes the single initialization hook used by the surrounding USB audio mixer code while keeping the large implementation details in `mixer_scarlett2.c`.

## Important API

- `int snd_scarlett2_init(struct usb_mixer_interface *mixer);`

This function is implemented in `mixer_scarlett2.c`. The USB audio mixer path calls it with the active `struct usb_mixer_interface`. It detects supported Focusrite devices, optionally delegates to the FCP driver, initializes proprietary USB notifications, reads device configuration, creates ALSA controls, registers the hwdep firmware/configuration interface, and exposes a proc device-map file when supported.

## Dependencies and Integration

The header assumes `struct usb_mixer_interface` is declared before inclusion. In this tree it is included from USB audio mixer code that already has the relevant ALSA USB mixer definitions. The include guard `__USB_MIXER_SCARLETT2_H` prevents duplicate declarations.

The declaration integrates the Scarlett 2 mixer implementation with the broader ALSA USB audio driver without exporting its internal structs, product tables, USB packet helpers, notification handlers, or control callbacks.

## Control Flow and State

This header contains no control flow and owns no state. All state is allocated and managed by `snd_scarlett2_init()` and the implementation's private data. The only observable behavior from this header is whether callers can link against the initialization entry point.

## Persistence Behavior

No persistence is implemented here. Persistent behavior, including delayed config saves and flash segment access, is handled in `mixer_scarlett2.c`.

## Risks

- Include-order matters because the header does not forward-declare `struct usb_mixer_interface`; callers must include the USB mixer definitions first.
- Any signature change must be reflected in the caller and implementation together, or the driver will fail to build.
- The broad implementation is hidden behind one API, so callers cannot express partial feature initialization or inspect support status except through the function return and created ALSA side effects.

## Test Signals

- A compile test should verify all users include this header after defining or declaring `struct usb_mixer_interface`.
- Link/build coverage should confirm exactly one implementation of `snd_scarlett2_init()` is available.
- Runtime tests are driven by `mixer_scarlett2.c`: successful probe should call this entry point and create the expected Focusrite controls or cleanly no-op for unsupported/disabled conditions.
