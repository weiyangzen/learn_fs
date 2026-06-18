# sources/distributed-fs/ceph-client/drivers/hid/hid-belkin.c

Purpose: handles a small set of Belkin/Labtec special HID devices by forcing HIDDEV for one KVM and remapping several consumer usages on a wireless keyboard.

Important APIs/types/functions: quirk bits `BELKIN_HIDDEV` and `BELKIN_WKBD` are carried in `id->driver_data` and stored with `hid_set_drvdata()`. `belkin_input_mapping()` maps consumer usages `0x03a`, `0x03b`, and `0x03c` to `KEY_SOUND`, `KEY_CAMERA`, and `KEY_DOCUMENTS` when the wireless-keyboard quirk is set. `belkin_probe()` parses the descriptor and starts HID hardware, adding `HID_CONNECT_HIDDEV_FORCE` when requested.

Control flow: the HID driver matches either the Belkin Flip KVM or Labtec wireless keyboard. Probe records the quirk mask, parses, and starts HID with default listeners plus optional forced hiddev. During input mapping, only consumer-page usages on `BELKIN_WKBD` are intercepted; other usages continue through generic mapping.

State/persistence: the only driver state is the quirk bitmask stored as driver data. No dynamic state, sysfs attributes, or persistent settings are created.

Dependencies/integration: depends on HID parser/start APIs, HID input mapping helpers, hiddev connection flags, Linux input key codes, and IDs from `hid-ids.h`.

Risks: the driver stores an integer quirk mask through a pointer-shaped `void *`; this is common in old HID drivers but depends on safe cast width for these small flags. The KVM path intentionally exposes hiddev even if normal generic handling would not. The wireless mapping is narrow and may miss related usages.

Test signals: confirm the Flip KVM creates/claims hiddev, the Labtec keyboard maps the three special keys to the expected input codes, unrelated consumer usages remain generic, and parse/start errors propagate from probe.
