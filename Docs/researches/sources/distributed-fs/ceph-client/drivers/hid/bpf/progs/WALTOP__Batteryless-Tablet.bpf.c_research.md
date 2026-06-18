# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/WALTOP__Batteryless-Tablet.bpf.c

## Purpose
This program fixes a WALTOP batteryless tablet by replacing its descriptor, correcting an ambiguous secondary barrel button report, and reshaping pressure values. The descriptor replacement adds Secondary Barrel Switch, corrects pen coordinate/tilt semantics, and keeps mouse, keyboard, and consumer-control collections.

## Important APIs, Types, And Functions
The match is USB WALTOP VID `0x172F`, PID `0x0505`, descriptor size 335. `fixed_rdesc[]` is a full replacement descriptor. `bitwidth32()`, `floor_log2_32()`, and `scaled_log2()` implement a fixed-point approximation for pressure scaling. `hid_fix_rdesc()` copies the replacement descriptor and returns its size. `waltop_fix_events()` handles pen report ID 16. `HID_BPF_OPS(waltop_batteryless)` installs both hooks.

## Control Flow
Probe accepts only descriptor size 335. Descriptor fixup always copies `fixed_rdesc`. Event fixup ignores non-pen reports. For pen reports, if the tablet sends Tip Switch and Barrel Switch together while neither was previously held, the code clears both and sets `SECONDARY_BARREL_SWITCH`, interpreting that transition as the physical secondary button. It then stores the current button byte. Pressure is read little-endian from bytes 6-7; values up to 102 are multiplied by 12, while higher values pass through `scaled_log2()` to map the exponential sensor curve into the advertised 0-2047 logical range.

## State And Persistence
`last_button_state` persists the prior pen button byte to distinguish a new ambiguous secondary-button press from ongoing tip or barrel holds. There is no external persistence.

## Dependencies And Integration Points
The file depends on HID-BPF helpers and stable report ID 16 layout. It integrates with the digitizer input path by presenting corrected pen buttons, axes, tilt, pressure, plus existing mouse/keyboard/media collections.

## Risks
The secondary-button heuristic assumes the only unambiguous simultaneous tip+barrel transition is the secondary button. If users press tip and barrel at exactly the same time from idle, it could be remapped. The pressure scaling is an approximation tuned to observed values 12 and 102. Full descriptor replacement is broad and sensitive to changes in the original descriptor.

## Test Signals
Tests should compare descriptor size and key pen usages, press tip/barrel/secondary barrel in isolation and combinations, verify pressure curve values around 0, 100, 102, and 2047, and confirm non-pen reports remain unchanged.
