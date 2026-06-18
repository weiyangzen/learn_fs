# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__KeydialK20-Bluetooth.bpf.c

## Purpose
This program fixes the Bluetooth Huion Keydial K20/Keydial Mini. Unlike the USB K20, it does not rely on switching into vendor mode; instead it rewrites the active Bluetooth keyboard, consumer-control, and mouse-wheel reports into one tablet-pad report and disables the silent puck node.

## Important APIs, Types, And Functions
The match is Bluetooth Huion PID `0x8251`. Descriptor lengths are 160 for the active pad node and 114 for the silent puck node. `k20_bt_fix_rdesc()` replaces the active descriptor with `fixed_rdesc_pad[]` and the puck descriptor with `disabled_rdesc_puck[]`. `k20_bt_fix_events()` rewrites report IDs 1, 2, and 5 into report ID 11. A packed local `pad_report` carries a stylus dummy bit, dummy X/Y bytes, a 32-bit button field, and an 8-bit wheel value.

## Control Flow
Descriptor fixup is length-selected: size 160 becomes a tablet function-key descriptor with 19 buttons and a wheel; size 114 becomes a fixed-size vendor-only disabled descriptor. Event fixup maps report ID 1 keyboard events to buttons by scanning HID key arrays and modifiers. Modifiers Control, Alt, and Shift become buttons 13, 14, and 15; normal key usages map through the 18-entry table. Report ID 2 maps Consumer Play/Pause to button 19 and updates `last_button_state`. Report ID 5 carries mouse wheel deltas and emits them while preserving the last button bitmap.

## State And Persistence
`last_button_state` is a persistent global holding the current 19-button bitmap across independent keyboard, consumer-control, and wheel reports. This is required because the physical wheel click and wheel movement arrive on different report IDs from key buttons.

## Dependencies And Integration Points
The program depends on HID-BPF helpers and `hid_report_helpers.h`. It integrates the Bluetooth remote with Linux tablet-pad handling by advertising Digitizers Tablet Function Keys plus button usages 1-10 and 0x31-0x3a for higher buttons.

## Risks
The keyboard mapping table assumes the default Bluetooth key assignments. Unknown key assignments or remapped firmware profiles will not be translated. The event hook reads 12 bytes even though source reports are shorter, relying on HID-BPF data access and the output struct size; unexpected report lengths should be tested. Wheel deltas are passed through as unsigned bytes, with 0xff representing -1.

## Test Signals
Descriptor tests should show the 160-byte node converted to report ID 11 and the 114-byte node disabled. Runtime tests should press each mapped key button, each modifier-derived button, Play/Pause wheel click, and wheel up/down, checking that button state persists correctly while wheel-only reports are emitted.
