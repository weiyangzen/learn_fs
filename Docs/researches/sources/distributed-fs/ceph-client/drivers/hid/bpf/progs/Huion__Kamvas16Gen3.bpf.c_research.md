# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas16Gen3.bpf.c

## Purpose
This is the Kamvas 16 Gen 3 sibling of the Kamvas 13 Gen 3 quirk. It enables practical vendor-mode operation by replacing the vendor descriptor with a fixed pen and tablet-pad descriptor, disabling unused firmware-mode nodes when raw-mode firmware is detected, and rewriting vendor reports into standard pen and pad reports. It also accounts for the Kamvas 16's 24-bit X-axis layout.

## Important APIs, Types, And Functions
The target device is USB Huion PID `0x2009`. Known descriptor sizes are vendor 36, tablet 328, and wheel 200; vendor report ID is 8 and vendor report length is 14. `fixed_rdesc_vendor[]` defines a 24-bit X axis, 16-bit Y, pressure, tilt, eight pad buttons, top wheel, and bottom wheel. `hid_fix_rdesc_huion_kamvas16_gen3()` handles descriptor replacement. `hid_fix_event_huion_kamvas16_gen3()` handles pen, buttons, and wheel report subtypes.

## Control Flow
The descriptor hook checks `UDEV_PROP_HUION_FIRMWARE_ID` for prefix `HUION_M22d_`. When present, descriptor sizes 328 and 200 are replaced by disabled descriptors; size 36 is always replaced by the fixed vendor descriptor. The event hook accepts only 14-byte vendor report ID 8. Pen reports invert Y tilt and rearrange bytes from the device layout into the descriptor layout by moving `data[8]` into the third byte of X and shifting subsequent Y/pressure bytes. Button and wheel subtype handling mirrors Kamvas13Gen3: clean button state is persisted, top/bottom wheel direction is converted from 1/2 to +1/-1, and a packed custom report ID 9 is returned.

## State And Persistence
`last_button_state` stores the current accepted pad-button bitmap. There are no maps, files, or cross-load persistence.

## Dependencies And Integration Points
Dependencies are HID-BPF core helpers, `hid_report_helpers.h`, and udev firmware properties. The fixed descriptor integrates the vendor endpoint with Linux as a digitizer pen plus tablet pad. The file explicitly references Kamvas13Gen3 behavior for detailed wheel/button caveats.

## Risks
The 24-bit X byte shuffle is layout-specific; a firmware change to report packing would corrupt coordinates. Eraser/Invert behavior remains unverified for pens with erasers. The simultaneous-button filter can reject legitimate overlapping button presses. The firmware-prefix gating may leave duplicate firmware nodes if userspace does not set the expected property.

## Test Signals
Descriptor tests should cover sizes 36, 328, and 200. Event tests should verify 24-bit X reconstruction against known maximum 69920, Y maximum 39340, pressure maximum 16383, Y tilt inversion, eight pad buttons including wheel buttons, and separate top/bottom wheel deltas. Negative tests should send non-ID-8 or non-14-byte reports and expect no rewrite.
