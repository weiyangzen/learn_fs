
# sources/distributed-fs/ceph-client/include/uapi/linux/input-event-codes.h

## Purpose

`input-event-codes.h` defines the Linux input subsystem's event type, property, key/button, axis, switch, misc, LED, repeat, sound, and sound-profile numeric codes. It is intentionally usable from C and device-tree source, so it contains comments and `#define`s only. The complete 1016-line file was read.

## Important APIs, Types, and Functions

Major groups are `INPUT_PROP_*`, `EV_*`, `SYN_*`, hundreds of `KEY_*` and `BTN_*` codes, `REL_*`, `ABS_*` including multitouch slots and tracking IDs, `SW_*`, `MSC_*`, `LED_*`, `REP_*`, `SND_*`, and `SND_PROFILE_*`. It also defines count/max helpers such as `EV_CNT`, `KEY_CNT`, `ABS_CNT`, and compatibility aliases like `KEY_HANGUEL`, `KEY_SCREENLOCK`, and `BTN_A`.

## Control Flow

No executable flow exists. Drivers emit events using these numeric codes; user-space input libraries decode event streams and advertise capability bitmaps with the same values.

## State and Persistence Behavior

The header owns no runtime state. Input device state and capability bitmaps live in kernel input devices; event values are read through `struct input_event` from `input.h`.

## Dependencies and Integration Points

It has no includes by design and is included by `input.h`, device-tree sources, input drivers, HID mappings, evdev clients, libinput, compositors, and keymap tools.

## Risks and Edge Cases

Because device-tree includes the file, adding anything beyond comments/defines is unsafe. Numeric code stability is critical. Reserved `REL_RESERVED` and `ABS_RESERVED` help users detect historical HID misuse; new keys must avoid inappropriate fallback to macro or vendor ranges.

## Test Signals

Signals include UAPI compile and devicetree parse tests, input capability bitmap tests, HID/keymap mapping tests, evdev decoding tests, and checks that max/count constants track the highest defined codes.
