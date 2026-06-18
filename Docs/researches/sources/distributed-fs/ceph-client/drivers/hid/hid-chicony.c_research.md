# sources/distributed-fs/ceph-client/drivers/hid/hid-chicony.c

Purpose: supports Chicony special keyboards/devices by mapping Microsoft-vendor usages, synthesizing wireless radio control key events, and fixing an Acer Switch 12 descriptor that exceeds `HID_MAX_USAGES`.

Important APIs/types/functions: `ch_report_wireless()` turns wireless-radio-control reports with ID `0x11` into a press/release of `KEY_RFKILL`. `ch_raw_event()` routes wireless radio control application reports to that helper. `ch_input_mapping()` maps selected `HID_UP_MSVENDOR` usages to button and hotkey codes such as `BTN_1..BTN_B`, `KEY_WLAN`, brightness, display off, camera, and `KEY_PROG1`. `ch_switch12_report_fixup()` inspects USB interface 1 and rewrites `0x7fff` usage/logical maximums to `0x2fff` for the Acer Switch 12. `ch_probe()` requires USB, sets `HID_QUIRK_INPUT_PER_APP`, parses, and starts HID.

Control flow: probe ensures the device is USB, enables per-application input splitting, parses with possible descriptor fixup, and starts normal HID listeners. Input mapping consumes Microsoft-vendor usages. Raw events for the wireless radio controls application bypass normal mapping by manually reporting `KEY_RFKILL`.

State/persistence: no driver-private heap state is allocated. The only persistent runtime effect is input capability registration and descriptor mutation for the active device.

Dependencies/integration: depends on USB interface access, HID raw-event callbacks, hid-input mapping, input event reporting, `HID_QUIRK_INPUT_PER_APP`, and Chicony/Acer IDs.

Risks: `ch_switch12_report_fixup()` assumes a USB parent and specific descriptor offsets; probe rejects non-USB to keep that safe. `ch_report_wireless()` assumes `report->field[0]->hidinput` is valid when the report shape matches. Manual RFKILL press/release injection must not duplicate generic events.

Test signals: verify per-application input devices, Microsoft-vendor hotkeys, wireless RFKILL report synthesis, Acer Switch 12 descriptor fixup on interface 1 only, rejection of non-USB matches, and absence of duplicate RFKILL events.
