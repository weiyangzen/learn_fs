# sources/distributed-fs/ceph-client/drivers/hid/hid-evision.c

## Purpose
`hid-evision.c` contains small EVision-specific HID quirks. For the EVision ICL01 keyboard/configuration device it suppresses bogus consumer reports sent after keyboard configuration. For the EVision TeLink receiver it fixes a descriptor usage maximum so all expected usages are parsed.

## Important APIs, Types, And Functions
`evision_input_mapping()` inspects usages during input mapping. It only applies to product `USB_DEVICE_ID_EVISION_ICL01`, only on the consumer page, and returns `-1` for key down/up pseudo-usages and configuration/reset events that should not become input events. `evision_report_fixup()` checks for product `USB_DEVICE_ID_EV_TELINK_RECEIVER`, descriptor size 236, and a `Usage Maximum` item at index 59 with value 3; it changes that maximum to 5. `evision_devices[]` binds both devices, and `evision_driver` wires input mapping and descriptor fixup callbacks.

## Control Flow
There is no custom probe. HID core matches the ID table, applies `evision_report_fixup()` before parsing for the TeLink receiver, and invokes `evision_input_mapping()` while building input mappings for the ICL01. Suppressed usages return `-1`, which tells HID input not to map them; all other usages fall back to generic HID behavior.

## State And Persistence
The driver keeps no runtime private state and performs no persistent device writes. All behavior is descriptor-time or mapping-time filtering.

## Dependencies And Integration Points
The file depends on HID core, input mapping constants, and EVision IDs from `hid-ids.h`. It integrates by correcting generic HID parsing rather than creating custom input devices.

## Risks
The ICL01 filter depends on exact usage encodings; if firmware changes bogus report IDs/usages, they may leak into user space. The TeLink descriptor fixup is offset- and size-specific; descriptor variants will not be fixed unless they match the hardcoded shape. The comment uses `//` in kernel C for the usage-max change, which is accepted in modern kernel style but stands out in an otherwise C-comment file.

## Test Signals
For ICL01, keyboard configuration should no longer emit bogus consumer input events for key down/up, configuration saved, or reset notifications. For TeLink, debugfs `rdesc` after fixup should show usage max 5 at the target item and the expected extra inputs should be available. Generic consumer keys outside the filtered usages should still work.
