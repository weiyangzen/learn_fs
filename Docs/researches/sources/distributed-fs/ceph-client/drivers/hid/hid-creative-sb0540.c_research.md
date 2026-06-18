# sources/distributed-fs/ceph-client/drivers/hid/hid-creative-sb0540.c

## Purpose
`hid-creative-sb0540.c` handles the Creative SB0540 infrared receiver, translating nonstandard six-byte HID reports into Linux input key events for the bundled remote control. It bypasses normal HID input mapping because the useful command code is encoded in raw report payload bits rather than as ordinary HID usages.

## Important APIs, Types, And Functions
`creative_sb0540_key_table[]` is the user-facing keymap, while `creative_sb0540_codes[]` contains the corresponding 16-bit remote codes sourced from LIRC. `struct creative_sb0540` stores the input device, HID device, and mutable keymap exposed through the input layer. `reverse()` reverses the bit order of an 8-bit payload value inside a `u64`. `get_key()` searches the code table and returns the key currently assigned at the matching keymap index. `creative_sb0540_raw_event()` decodes reports and emits press/release pairs. `creative_sb0540_input_configured()` initializes the input device keycode metadata and supported key bits. `creative_sb0540_input_mapping()` returns `-1` so generic hid-input mapping is skipped. `creative_sb0540_probe()` allocates state, forces HID input creation, parses the device, and starts HID.

## Control Flow
Probe stores per-device state with `hid_set_drvdata()`, sets `HID_QUIRK_HIDINPUT_FORCE`, calls `hid_parse()`, and starts HID with `HID_CONNECT_DEFAULT`. During input configuration, the driver points `input_dev->keycode` at its keymap, enables `EV_KEY` and `EV_REP`, copies the default key table, marks all nonreserved keys, and clears `KEY_RESERVED`.

Each raw event is accepted only when the length is exactly six bytes and the device has an input claim. The driver reverses `data[5]`, constructs an NEC-style code and its complement, byte-swaps it to match the LIRC table, then looks up a Linux key. Unknown or reserved codes are logged and ignored. Valid codes are emitted as immediate key down, key up, and `input_sync()`. Returning zero lets hidraw and hiddev still receive the raw packet.

## State And Persistence
The mutable state is the input device pointer and keymap in `struct creative_sb0540`. The keymap begins as `creative_sb0540_key_table[]` and can be exposed through normal input keycode handling. There is no nonvolatile device programming, no workqueue, and no explicit remove path because devm allocation and HID core teardown cover lifetime.

## Dependencies And Integration Points
This driver depends on HID core callbacks, Linux input key reporting, `hid-ids.h` Creative vendor/product IDs, and generic HID input registration. It intentionally integrates with hidraw/hiddev by not consuming raw reports exclusively, while still producing standard `EV_KEY` events for desktop/media applications.

## Risks
The decoder assumes report length and payload layout remain fixed. Unknown codes produce HID errors, which can become noisy if the receiver reports unrelated traffic. Because each accepted report generates a synthetic press and release immediately, long-press repeat behavior depends on the remote sending repeated packets and on input repeat settings, not on explicit state tracking. Table order must stay synchronized between `creative_sb0540_key_table[]` and `creative_sb0540_codes[]`; mismatches silently report the wrong key.

## Test Signals
Validation should include probe success for `USB_DEVICE_ID_CREATIVE_SB0540`, `evtest` showing mapped media/navigation/numeric keys, unknown-code logging for unsupported buttons, hidraw still receiving six-byte reports, keymap size consistency, and repeat behavior for held remote buttons.
