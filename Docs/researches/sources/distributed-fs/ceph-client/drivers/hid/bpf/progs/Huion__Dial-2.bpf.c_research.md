# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Dial-2.bpf.c

## Purpose

This HID-BPF program fixes Huion Dial 2 tablet descriptors and reports across firmware/default mode and raw tablet mode. It avoids duplicate unusable nodes when a firmware ID is known and translates vendor/keyboard-style reports into tablet pad, pen, button, and dial reports.

## Important APIs, Types, and Functions

The program matches USB VID `0x256C`, PID `0x0060`. It consumes udev property `HUION_FIRMWARE_ID` and expects prefix `HUION_T216_`. Constants define descriptor lengths, report IDs, and report lengths for pad, pen, vendor, dial, and keyboard paths. Static replacement descriptors are `fixed_rdesc_pad`, `fixed_rdesc_pen`, `fixed_rdesc_vendor`, plus disabled vendor-sized descriptors. `dial_2_fix_rdesc()` selects the replacement descriptor. `dial_2_fix_events()` rewrites default keyboard/dial reports and raw vendor pad reports. `last_button_state` persists pad button state across raw dial events.

## Control Flow

Probe accepts only the three known descriptor sizes. During descriptor fixup, known firmware ID disables default pad/pen nodes and always fixes the vendor node; without firmware ID it fixes all nodes so manual mode switching still works. Event flow handles default pad report ID 3, default dial report ID 17, and raw vendor report ID 8. Raw pad packets become a packed pad report with button state plus two dial axes; pen packets pass through.

## State and Persistence Behavior

Persistent BPF state includes `UDEV_PROP_HUION_FIRMWARE_ID`, `EXPECTED_FIRMWARE_ID`, and `last_button_state`. Descriptor changes persist through HID reprobe; event rewrites are per report.

## Dependencies and Integration Points

It depends on HID-BPF, HID report descriptor helper macros, udev-hid-bpf property injection, and Huion mode-switch tooling that can set firmware ID.

## Risks and Test Signals

Risks include fixed report layouts, firmware prefix mismatch, button state becoming stale when reports are lost, and signed dial values encoded as `0xff`. Test signals include correct behavior in default and raw modes, no duplicate active devices when firmware ID is present, button/dial mapping tests, descriptor-size probe rejection, and verifier acceptance of bounded copies.
