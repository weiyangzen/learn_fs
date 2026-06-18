# sources/distributed-fs/ceph-client/drivers/hid/hid-gembird.c

Fixes a malformed Gembird JPD-DualForce 2 joypad report descriptor. The original descriptor duplicates Z usage and mislabels axes; the driver patches that descriptor before HID parsing.

`gembird_jpd_faulty_rdesc` is the byte pattern searched at offset `GEMBIRD_START_FAULTY_RDESC`; `gembird_jpd_fixed_rdesc` replaces it with X/Y data, one constant Z byte, and Rx/Ry axes. `gembird_report_fixup()` checks descriptor size and pattern, allocates a larger devm-managed descriptor, copies the original descriptor around the replacement block, updates `*rsize`, and returns the patched descriptor.

There is no runtime state beyond the patched descriptor memory and no persistent hardware setting. Dependencies are HID report fixup hooks, device-managed allocation, and `hid-ids.h` constants for the Gembird USB match.

Risks are mainly offset-specific matching and size arithmetic. Firmware variants with similar but not identical descriptors will not be fixed. Test signals include parsed axis layout on real hardware, fallback when the byte pattern is absent, fixed descriptor size, and safe behavior when the descriptor is shorter than expected.
