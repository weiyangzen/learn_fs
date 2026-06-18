# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Inspiroy-2-M.bpf.c

## Purpose

This HID-BPF program fixes Huion Inspiroy 2 M tablet descriptors and events, supporting both default firmware mode and raw tablet mode while avoiding duplicate inactive nodes when the firmware ID is known.

## Important APIs, Types, and Functions

The program matches USB VID `0x256C`, PID `0x0067`. It uses `HUION_FIRMWARE_ID` with expected prefix `HUION_T21k_`. Constants define descriptor lengths, report IDs, and packet sizes. Replacement descriptors `fixed_rdesc_pad`, `fixed_rdesc_pen`, and `fixed_rdesc_vendor` correct pad, pen, pressure, coordinate, button, and wheel semantics; disabled descriptors hide mute nodes. `hid_fix_rdesc()` selects descriptors. `inspiroy_2_fix_events()` converts default keyboard shortcut packets into pad reports and raw vendor pad packets into button/wheel reports. `last_button_state` preserves raw button bits between wheel packets.

## Control Flow

Probe accepts only known pad, pen, and vendor descriptor sizes. Descriptor fixup disables default pad/pen reports when firmware ID proves raw mode support, otherwise fixes all descriptors. Event handling rewrites report ID 3 keyboard/wheel packets to a compact pad report; report ID 8 vendor packets with pad marker bits are translated to pad state, while pen reports pass through.

## State and Persistence Behavior

Persistent BPF globals are the udev firmware ID buffer, expected prefix, and `last_button_state`. Runtime report rewrites are transient but descriptor replacements persist across the HID device instance.

## Dependencies and Integration Points

It depends on HID-BPF helpers, descriptor helper macros, udev-hid-bpf property passing, and the Huion raw-mode ecosystem described in comments.

## Risks and Test Signals

Risks include hard-coded dimensions/ranges, firmware ID prefix drift, wheel values represented in unsigned bytes, and stale raw button state. Test signals include pad button mapping for all default shortcuts, wheel direction correctness, raw mode button/wheel behavior, pen pressure/coordinate ranges, duplicate-node suppression, and BPF verifier load.
