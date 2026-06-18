# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/FR-TEC__Raptor-Mach-2.bpf.c

## Purpose

This HID-BPF program fixes the FR-TEC/Betop Raptor Mach 2 joystick report descriptor and event stream so the hat switch has kernel-compatible values.

## Important APIs, Types, and Functions

The program matches USB generic HID device VID `0x11C0`, PID `0x5606` through `HID_BPF_CONFIG`. `hid_fix_rdesc_raptor_mach_2()` is a `HID_BPF_RDESC_FIXUP` program that changes descriptor byte 177 from logical maximum 239 to 7. `raptor_mach_2_fix_hat_switch()` is a `HID_BPF_DEVICE_EVENT` program that divides report byte 33 by 30 for report ID 1. `HID_BPF_OPS(raptor_mach_2)` attaches both hooks. `probe()` accepts only the expected 232-byte descriptor with byte 177 still equal to `0xef`.

## Control Flow

At load/probe time the descriptor gate rejects already-fixed or unknown descriptors. During descriptor fixup, the BPF program mutates the logical max. During events, only joystick report ID 1 is changed; other reports pass through.

## State and Persistence Behavior

The program has no mutable persistent state. It mutates the report descriptor buffer and event buffer supplied by HID-BPF.

## Dependencies and Integration Points

It depends on HID-BPF helpers, `hid_bpf_get_data()`, BPF tracing macros, and udev-hid-bpf loading conventions.

## Risks and Test Signals

Risks are hard-coded descriptor and report offsets. Test signals include probe rejection on descriptor changes, hat switch reporting 0..7 instead of 0..239, no changes to non-ID-1 reports, and successful BPF verifier load.
