# sources/distributed-fs/ceph-client/drivers/hid/hid-twinhan.c

Purpose: remaps the TwinHan IR remote control keyboard-page usages into media remote keys and suppresses modifier usages used as parts of multi-key remote-button encodings.

Important APIs, types, and functions: `twinhan_input_mapping()` handles `HID_UP_KEYBOARD` usages. It maps fixed usage IDs to keys such as `KEY_TEXT`, `KEY_RESTART`, `KEY_EPG`, numeric keys, playback keys, channel/volume controls, and `KEY_POWER2`. Modifier usages `0x0e0` through `0x0e7` and unknown usages return `-1`, which stops generic mapping and prevents stray modifier events.

Control flow: HID calls the mapping hook per usage. Non-keyboard pages return `0`; listed usages map and return `1`; modifier or unrecognized keyboard usages return `-1`.

State and persistence: stateless; no allocations or drvdata.

Dependencies and integration: integrates with HID input mapping and input key codes. `twinhan_devices[]` matches the TwinHan IR remote USB ID.

Risks: returning `-1` for all unrecognized keyboard-page usages intentionally drops events, which is correct for the known remote but can hide new buttons if the same VID/PID appears with a revised layout. The comments document multi-key encodings for power and volume where suppressing modifier components matters.

Test signals: no automated tests. Validate with the physical remote, checking that power/volume do not leave Ctrl/Alt/Meta states stuck and that all documented keys emit the expected input codes.
