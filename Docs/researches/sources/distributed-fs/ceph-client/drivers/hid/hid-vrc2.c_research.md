# sources/distributed-fs/ceph-client/drivers/hid/hid-vrc2.c

Purpose: fixes and binds the VRC-2 two-axis car controller, replacing its descriptor with a simple joystick descriptor and ignoring a bogus sibling endpoint/interface.

Important APIs, types, and functions: local VID/PID constants are kept out of `hid-ids.h` because they may be borrowed. `vrc2_rdesc_fixed[]` describes a joystick with X/Y 16-bit absolute axes and trailing constants. `vrc2_report_fixup()` always returns the fixed descriptor. `vrc2_probe()` rejects interfaces whose original report descriptor size is 23, then parses and starts HID normally.

Control flow: on matched device, probe first filters the bogus endpoint by `hdev->dev_rsize`. For the real interface, HID parsing invokes descriptor fixup, then `hid_hw_start()` connects default input handling.

State and persistence: stateless; no private data or allocations.

Dependencies and integration: depends on HID report fixup and generic input handling. Registers a `hid_driver` named `vrc2` for the local USB IDs.

Risks: descriptor fixup is unconditional for non-rejected interfaces. If hardware with the borrowed VID/PID differs, it may receive an incorrect joystick descriptor. The bogus endpoint filter is based only on descriptor size.

Test signals: no automated tests. Validate by plugging the controller, confirming only the useful interface binds, and checking ABS_X/ABS_Y ranges in evtest.
