# sources/distributed-fs/ceph-client/drivers/hid/hid-ezkey.c

## Purpose
`hid-ezkey.c` handles the BTC 8193/EZKey keyboard's nonstandard consumer-page mouse and wheel usages. It maps special consumer usages to mouse button and wheel events, and corrects a broken scroll-wheel direction/path by temporarily mapping one usage to horizontal wheel and converting it during event handling.

## Important APIs, Types, And Functions
`ez_map_rel()` and `ez_map_key()` wrap `hid_map_usage()` for relative axes and keys. `ez_input_mapping()` checks for consumer-page usages and maps usage `0x230` to `BTN_MOUSE`, `0x231` to `REL_WHEEL`, and `0x232` to `REL_HWHEEL` as a temporary quirk representation. `ez_event()` intercepts events for `REL_HWHEEL`, emits `REL_WHEEL` with negated value, and consumes the original event. `ez_devices[]` matches `USB_DEVICE_ID_BTC_8193`, and `ez_driver` registers input mapping and event callbacks.

## Control Flow
The driver has no custom probe, so generic HID setup handles parse/start. During input mapping, only consumer-page usages are considered. Recognized usages return 1 after explicit mapping, while other usages fall back to generic HID behavior. At runtime, the event hook validates that input is claimed, `field->hidinput` exists, and the usage has a type. The temporary `REL_HWHEEL` event is then rewritten to a negated vertical wheel event on the input device.

## State And Persistence
There is no private state and no persistence. The `REL_HWHEEL` mapping is only a marker used between mapping and event callbacks.

## Dependencies And Integration Points
The file depends on HID input mapping/event hooks, Linux input relative/key events, and EZKey IDs from `hid-ids.h`. It integrates the keyboard's special controls into the normal input stream.

## Risks
The quirk deliberately advertises/uses `REL_HWHEEL` internally; if other code observes capability bits before events are rewritten, the device may appear to have a horizontal wheel even though events are converted. Direction is hardcoded as `-value`, so firmware variants with corrected direction would be inverted. Only three usage IDs are handled; other special keys remain generic or unmapped.

## Test Signals
Testing should confirm BTC 8193 reports `BTN_MOUSE`, vertical wheel for usage `0x231`, and inverted vertical wheel for usage `0x232`, with no stray horizontal wheel events reaching user space. Generic keyboard keys and consumer controls outside those usages should continue through normal HID mapping.
