# sources/distributed-fs/ceph-client/drivers/hid/hid-cmedia.c

Purpose: implements two C-Media HID drivers in one module: CM6533 headphone jack detection through raw HID packets, and HS-100B report descriptor correction for audio mute controls.

Important APIs/types/functions: `struct cmhid` stores the input device, HID device, and switch map for CM6533. `cmhid_raw_event()` recognizes 16-byte jack packets by suffix and prefix and reports `SW_HEADPHONE_INSERT` through `hp_ev()`. `cmhid_input_configured()` forces the input device to expose only EV_SW headphone insertion capability. `cmhid_input_mapping()` returns `-1` to suppress generic mappings. `cmhid_probe()` sets `HID_QUIRK_HIDINPUT_FORCE`, parses, and starts HID with `HID_CONNECT_HIDDEV_FORCE`. `cmhid_hs100b_report_fixup()` replaces the 60-byte HS-100B descriptor with `hs100b_rdesc_fixed[]`, which marks microphone mute as an absolute telephony usage. `cmedia_init()` registers both HID drivers and unwinds the first if the second fails.

Control flow: CM6533 probe allocates private state, forces input creation, parses, and starts HID. When raw packets arrive, the driver checks claimed input state, exact packet length, known suffix, then known plug-in/plug-out prefixes and emits switch changes. HS-100B devices bind to a separate HID driver whose only behavior is descriptor replacement before generic parsing.

State/persistence: CM6533 keeps a heap `cmhid` until remove, with current switch state stored in the input subsystem. HS-100B keeps no private state. No persistent settings are written.

Dependencies/integration: integrates HID core, forced hidinput/hiddev connection, Linux input switch events, module-level multi-driver registration, and C-Media IDs.

Risks: raw jack detection is based on observed packet bytes and may miss firmware variants. `cmhid_input_mapping()` suppresses all generic input mapping, so CM6533 exposes only the switch. Probe uses manual allocation/free rather than devm, so error and remove paths must remain paired. HS-100B descriptor replacement is size-based only.

Test signals: verify CM6533 plug/unplug reports `SW_HEADPHONE_INSERT`, no generic bogus input usages appear, hiddev remains available, remove frees private data, HS-100B exposes correct mute/volume controls with the fixed descriptor, and module init unwinds cleanly if one driver registration fails.
