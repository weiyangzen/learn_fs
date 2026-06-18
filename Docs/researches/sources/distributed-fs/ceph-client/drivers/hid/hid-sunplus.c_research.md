# sources/distributed-fs/ceph-client/drivers/hid/hid-sunplus.c

Purpose: handles Sunplus Wireless Desktop quirks by correcting a bad descriptor logical maximum and remapping two nonstandard consumer usages to zoom keys.

Important APIs/types/functions: `sp_report_fixup()` patches descriptor bytes when the expected pattern is present. `sp_input_mapping()` maps consumer usages `0x2003` and `0x2103` with `hid_map_usage_clear()`. `sp_driver` registers report-fixup and input-mapping callbacks for `USB_DEVICE_ID_SUNPLUS_WDESKTOP`.

Control flow: descriptor fixup checks size at least 112 and a specific long-item pattern at offsets 104-106, then changes both related maximum bytes so usages decode as `0x2103` rather than the broken `0x0380` style value. During input mapping, only Consumer page usages are considered; zoom-in and zoom-out usages become `KEY_ZOOMIN` and `KEY_ZOOMOUT`.

State and persistence: no private state. Effects are in-memory descriptor edits and input mapping decisions.

Dependencies/integration: depends on HID parser, Linux input consumer-key mapping, and Sunplus IDs.

Risks: byte-offset descriptor patch can miss firmware variants or patch an unintended descriptor if the guard is too broad; current guard includes size and exact bytes. Only two consumer usages are custom mapped, so other vendor hotkeys still depend on generic HID behavior.

Test signals: descriptor should parse the Sunplus zoom usages correctly; zoom controls should emit `KEY_ZOOMIN/KEY_ZOOMOUT`; unrelated consumer keys should remain generic; devices with different descriptors should not be patched.
