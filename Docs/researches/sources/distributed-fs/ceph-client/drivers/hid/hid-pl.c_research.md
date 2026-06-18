<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-pl.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-pl.c

## Purpose
This driver supports PantherLord/GreenAsia-compatible gamepads and adapters, mainly adding optional force-feedback rumble support and multi-input handling for dual adapters. It leaves ordinary input parsing to HID core after custom probe setup.

## Important APIs, types, and functions
When `CONFIG_PANTHERLORD_FF` is enabled, `struct plff_device` stores the output report, maximum rumble value, and pointers to strong/weak output fields. `hid_plff_play` scales Linux `FF_RUMBLE` magnitudes into device report values and submits the output report. `plff_init` inspects HID output reports and input devices to attach memless force feedback. `pl_probe` handles quirks, parsing, hardware start, and force-feedback init.

## Control flow
Probe sets `HID_QUIRK_MULTI_INPUT` for dual adapter IDs using `driver_data`, parses the descriptor, starts hardware with force-feedback auto-connect disabled, then calls `plff_init`. The FF initializer walks each HID input and corresponding output report. It supports two report layouts: one field with at least four values, or four separate fields with specific LED usage patterns. It stores pointers to the strong/weak value locations, initializes them to zero, sends an initial report, and registers memless rumble with the input device.

## State and persistence behavior
Per-input force-feedback state is allocated as `plff_device` and owned by the input FF memless data path. The output report fields hold current rumble values. No state is persisted across unplug.

## Dependencies and integration points
The file depends on HID core, input force feedback, optional `CONFIG_PANTHERLORD_FF`, and IDs for Gameron, GreenAsia, and Jess/Saitek devices. It integrates with Linux input `FF_RUMBLE` and HID output reports.

## Risks and test signals
Risks include output report layout assumptions, mismatching report count to input devices, and value scaling differences between 0x7f and 0xff devices. Tests should cover single-field and four-field devices, dual adapter multi-input enumeration, rumble magnitude scaling, missing output reports, and builds with FF disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-pl.c -->
