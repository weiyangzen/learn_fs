# sources/distributed-fs/ceph-client/drivers/hid/hid-semitek.c

Purpose: provides a narrow descriptor quirk for Semitek keyboards whose interface 2 incorrectly describes report ID `0x04` as an array of keycodes rather than a bitmask.

Important APIs/types/functions: the only behavioral callback is `semitek_report_fixup()`, registered in `semitek_driver`. The device table matches `USB_VENDOR_ID_SEMITEK` and `USB_DEVICE_ID_SEMITEK_KEYBOARD`.

Control flow: HID core calls report fixup before parsing. If the descriptor is exactly `0xcb` bytes and bytes `0x83/0x84` match the expected `Input` item with value `0x00`, the driver changes byte `0x84` to `0x02`, turning the field into Data/Variable/Absolute semantics. Otherwise it returns the descriptor unchanged. There is no custom probe; default HID driver flow handles parsing and input setup.

State and persistence: there is no driver-private state. The only state is the in-memory descriptor byte patch used for this device instance.

Dependencies/integration: depends on HID report descriptor parsing and the Semitek vendor/product IDs in `hid-ids.h`.

Risks: byte-offset fixups are fragile if firmware changes the descriptor length or layout. The guard is tight, so unknown variants fail safe by not patching but may remain unusable. Because no probe validation exists, regressions show up during HID parse/input behavior rather than driver-specific errors.

Test signals: affected keyboard should no longer emit broken key arrays for report `0x04`; `hid-recorder` or evtest should show independent key bits; descriptor parse should succeed without adding unrelated mappings.
