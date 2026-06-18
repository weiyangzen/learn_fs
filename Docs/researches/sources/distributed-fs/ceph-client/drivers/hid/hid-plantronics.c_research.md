<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-plantronics.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-plantronics.c

## Purpose
This driver normalizes Plantronics USB HID headset controls. It maps vendor-specific and telephony/consumer volume/mute usages to Linux input keys, forces HID input/hiddev exposure, and filters duplicate key presses that some devices emit within a few milliseconds.

## Important APIs, types, and functions
`struct plt_drv_data` stores decoded device type, last key timestamp, double-key timeout, and last key code. `plantronics_device_type` decodes either product ID for multi-HID interfaces or primary vendor collection usage. `plantronics_input_mapping` decides whether usages should be ignored, defaulted, or mapped to `KEY_VOLUMEUP`, `KEY_VOLUMEDOWN`, or `KEY_MICMUTE`. `plantronics_event` filters repeated key-down events. `plantronics_probe` allocates state, parses, determines type, initializes duplicate filtering, and starts HID.

## Control flow
Probe parses first because collection data is needed to classify device type. For BT300-style multi-HID interfaces, the product ID remains the type; otherwise collection usages on Plantronics HID 1.0/2.0 vendor pages select the type. Input mapping allows generic consumer controls and telephony mute where appropriate, handles DA60 special mute mapping, maps vendor controls for non-basic-telephony devices, and ignores unrelated usages. The usage table limits `.event` callbacks to relevant volume/mute usages, where duplicate presses of the same key within `PLT_DOUBLE_KEY_TIMEOUT` are consumed.

## State and persistence behavior
State is per device and allocated with devm. Duplicate filtering uses `jiffies`, stores only the last key and timestamp, and is disabled if HZ granularity cannot represent the 5 ms timeout. No persistent state exists.

## Dependencies and integration points
The file integrates HID input mapping, HID usage filtering, Linux input key codes, hiddev forced connection, and Plantronics vendor usage pages. It exposes normal input events to userspace and keeps hiddev available for legacy/control applications.

## Risks and test signals
Risks include device classification errors, suppressing legitimate fast repeated presses, and mapping changes for basic telephony compliant devices. Tests should cover DA60, BT300 range, HID 1.0/2.0 vendor pages, standard consumer controls, mic mute, duplicate filtering at HZ-dependent boundaries, and hiddev/input node creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-plantronics.c -->
