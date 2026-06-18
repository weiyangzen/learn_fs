# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__KeydialK20.bpf.c

## Purpose
This program fixes the USB Huion Keydial K20 across firmware and raw/vendor modes. Firmware mode sends buttons as keyboard shortcuts and exposes an unreliable wheel/puck node; tablet mode sends vendor reports. The program creates a tablet-pad descriptor, disables duplicate firmware nodes when raw-mode firmware is detected, and rewrites both vendor and keyboard reports into a single pad report.

## Important APIs, Types, And Functions
The match is USB Huion PID `0x0069`. Known descriptor lengths are pad 135, puck 108, and vendor 18. `k20_fix_rdesc()` rewrites or disables descriptors based on `UDEV_PROP_HUION_FIRMWARE_ID` prefix `HUION_T21h_`. `k20_fix_events()` converts vendor report ID 8 and firmware keyboard report ID 3. `HID_BPF_OPS(keydial_k20)` publishes both hooks, and `probe()` accepts only the three known descriptor sizes.

## Control Flow
If the firmware ID prefix matches, the pad and puck descriptors are disabled to avoid duplicate silent or redundant devices. If the prefix is absent, the pad descriptor is replaced with a tablet-pad descriptor that preserves original report lengths. The vendor descriptor is always replaced with a tablet-pad descriptor for raw mode. Event handling first rewrites vendor reports: `data[1] == 0xf1` is a wheel report and maps direction byte 2 to 0xff, otherwise bytes 4-6 become the 19-button bitmap stored in `last_button_state`. Firmware report ID 3 scans the keyboard report and modifier byte against a mapping table, creates the button bitmap, zeros consumed key slots, and emits the same pad report with wheel zero.

## State And Persistence
`last_button_state` persists raw-mode button state for wheel-only vendor reports. Firmware keyboard reports compute a local button bitmap per report. No durable persistence exists.

## Dependencies And Integration Points
The file depends on HID-BPF helpers, report helper macros, and udev-hid-bpf firmware properties from tools such as huion-switcher. It integrates with Linux tablet-pad handling by using Digitizers Tablet Function Keys and HID button usages that map to BTN_0-BTN_9 and BTN_A-family controls.

## Risks
Firmware-mode wheel and wheel-button data are documented as unreliable and intentionally not supported; users need raw/tablet mode for reliable wheel operation. Descriptor length gating may fail on new firmware. The keyboard mapping assumes default Huion shortcut assignments. Missing firmware properties can leave duplicate event nodes.

## Test Signals
Tests should cover descriptor sizes 18, 108, and 135, property-present and property-absent paths, raw-mode button and wheel reports, firmware keyboard shortcut translation for buttons 1-18, and rejection of unknown descriptor sizes. Runtime success is a single tablet-pad event stream with correct 19-button bitmap and wheel deltas in raw mode.
