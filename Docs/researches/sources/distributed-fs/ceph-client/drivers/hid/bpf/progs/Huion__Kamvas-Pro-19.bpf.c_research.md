# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas-Pro-19.bpf.c

## Purpose
This program fixes Huion Kamvas Pro 19 and Kamvas Pro 27 pen-display descriptors and reports. It corrects the second stylus button usage from Secondary Tip Switch to Secondary Barrel Switch, creates an extra button usage for the third stylus button, and disambiguates the firmware's use of the Invert bit between eraser mode and the third button.

## Important APIs, Types, And Functions
The match table targets USB multitouch Win8 devices for PIDs `0x006B` and `0x006c`. `fixed_rdesc[]` is a full replacement descriptor for the pen, touch, feature, and newer firmware mouse/touchpad/vendor collections. `hid_fix_rdesc_huion_kamvas_pro_19()` handles descriptor replacement. `kamvas_pro_19_fix_3rd_button()` rewrites incoming report ID `0x0a` pen reports. `probe()` verifies descriptor sizes, confirms the original Secondary Tip Switch byte is still present at offset 17, and checks the HID device name against `HUION Huion Tablet_GT1902` or `HUION Huion Tablet_GT2701`, with `uhid test ` stripped for test devices.

## Control Flow
Descriptor fixup accepts old size 328 and newer firmware size 438. For size 438 it copies all of `fixed_rdesc`; for the older descriptor it copies only `PRE_240524_RDESC_FIXED_SIZE` bytes, preserving a descriptor length appropriate to the old firmware. Event fixup ignores non-pen reports, marks an out-of-range report by clearing `in_eraser_mode`, treats a subsequent Invert/Eraser state after out-of-range as real eraser mode, and otherwise copies the Invert bit into the inserted third-button bit position before clearing Invert.

## State And Persistence
Two booleans persist in BPF data: `prev_was_out_of_range` and `in_eraser_mode`. They encode proximity history so the event hook can decide whether an Invert bit means eraser entry or stylus button 3. There is no external persistence.

## Dependencies And Integration Points
The file depends on HID-BPF helpers and on stable Huion names and descriptor layouts. It integrates with the HID multitouch group, preserving touch report sections while modifying stylus semantics. The `hid_bpf_allocate_context()` call in `probe()` is used only to inspect the HID device name.

## Risks
Name matching and byte-offset checks prevent accidental binding, but they also make the quirk sensitive to firmware or kernel naming changes. The eraser/button heuristic assumes an out-of-proximity event precedes real eraser mode. If a future pen reports eraser/Invert differently, the third-button rewrite could suppress legitimate eraser state.

## Test Signals
Tests should include old and 240524+ firmware descriptor sizes, both GT1902 and GT2701 names, and a negative test where offset 17 is no longer Secondary Tip Switch. Runtime traces should verify button 2 maps to BTN_STYLUS2, button 3 maps through the inserted button usage, normal eraser transitions after out-of-range remain untouched, and simple third-button presses do not leave Invert set.
