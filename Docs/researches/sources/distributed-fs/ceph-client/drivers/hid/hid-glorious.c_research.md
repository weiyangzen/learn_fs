# sources/distributed-fs/ceph-client/drivers/hid/hid-glorious.c

Provides quirks for Glorious PC Gaming Race mice, mainly report descriptor fixes and friendlier device names for Model O, Model D, and Model I.

`glorious_report_fixup()` patches two known descriptor defects: Model O/O- consumer-control inputs marked constant, and Model I keyboard usage minimum set to one. `glorious_update_name()` maps product IDs to model names and rewrites `hdev->name`. `glorious_probe()` sets `HID_QUIRK_INPUT_PER_APP`, parses, updates the name, and starts HID.

Only in-memory descriptor bytes, `hdev->name`, and quirks change. There is no persistent hardware setting. Dependencies are HID core, report fixup hooks, and Glorious-related IDs from `hid-ids.h`.

Risks are descriptor-size and offset brittleness. Firmware revisions may miss fixes, while a same-sized unexpected descriptor could be patched incorrectly within the matched product set. Test signals include consumer-control events on Model O/D, keyboard events on Model I, descriptor byte patching, per-application input splitting, and unchanged behavior on non-target descriptors.
