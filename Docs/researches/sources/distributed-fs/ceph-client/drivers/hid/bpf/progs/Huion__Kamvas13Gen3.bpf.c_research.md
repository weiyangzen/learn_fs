# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas13Gen3.bpf.c

## Purpose
This program supports the Huion Kamvas 13 Gen 3 by preferring vendor/raw mode, where wheel identity and wheel buttons are distinguishable. It replaces the vendor descriptor with a meaningful pen and custom tablet-pad descriptor, disables unused firmware-mode tablet and wheel nodes when a matching firmware property indicates raw mode, and rewrites vendor reports into standard input reports.

## Important APIs, Types, And Functions
The match uses `VID_HUION` `0x256c`, PID `0x2008`, and `HID_GROUP_ANY`. Descriptor lengths are 36 for vendor, 368 for tablet, and 108 for wheel. `fixed_rdesc_vendor[]` describes report ID 8 pen data and custom report ID 9 pad data. `hid_fix_rdesc_huion_kamvas13_gen3()` performs descriptor replacement/disablement. `hid_fix_event_huion_kamvas13_gen3()` handles vendor report subtypes: pen `0x08`, pen out `0x00`, buttons `0x0e`, and wheels `0x0f`.

## Control Flow
The descriptor hook checks `UDEV_PROP_HUION_FIRMWARE_ID` for prefix `HUION_M22c_`. If present, tablet and wheel descriptors are replaced with fixed-size vendor descriptors so silent duplicate firmware nodes do not produce input devices. The vendor descriptor is always expanded into fixed pen and pad collections. In the event hook, non-14-byte or non-report-ID-8 events are ignored. Pen reports have Y tilt inverted in place. Button and wheel reports are rewritten into the packed custom pad report: subtype `0x0f` maps `data[3]` to top or bottom wheel and `data[5]` from 1/2 to signed +1/-1; subtype `0x0e` updates `last_button_state` only on clean transitions, filtering ambiguous multi-button holds.

## State And Persistence
`last_button_state` persists the most recent accepted pad-button bitmap so wheel-only reports still include current button state and ambiguous non-release events can be ignored while a button is held. No BPF maps or external persistence are used.

## Dependencies And Integration Points
The file depends on HID-BPF helper macros and udev-hid-bpf firmware properties populated by raw-mode switching tools. It integrates with the input stack by presenting the vendor endpoint as a digitizer pen plus tablet function keys, including two relative axes: generic wheel and Consumer AC Pan for the bottom wheel.

## Risks
The implementation intentionally focuses on vendor mode and does not fully repair firmware-mode wheel ambiguity. The author notes uncertainty for pens with erasers; Invert and Eraser bit positions are not confirmed. Filtering simultaneous button holds is heuristic and may drop real multi-button combinations. Descriptor size or firmware prefix changes will bypass some fixes.

## Test Signals
Validation should cover vendor, tablet, and wheel descriptor sizes; firmware property present and absent; pen coordinate, pressure, and tilt reports; top and bottom wheel deltas; wheel-button buttons 6 and 7; ambiguous simultaneous button traces; and battery/feature report preservation through the fixed descriptor. A good runtime signal is custom report ID 9 with top wheel in byte 5 and bottom wheel in byte 6.
