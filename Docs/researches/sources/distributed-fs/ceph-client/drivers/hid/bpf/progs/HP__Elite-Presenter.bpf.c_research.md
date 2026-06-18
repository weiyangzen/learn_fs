# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/HP__Elite-Presenter.bpf.c

## Purpose

This HID-BPF program improves the HP Elite Presenter Mouse Bluetooth report descriptor so the second mouse-like collection is treated as a pointer collection, enabling both mouse and digital laser pointer behavior.

## Important APIs, Types, and Functions

The program matches Bluetooth generic HID VID `0x03F0`, PID `0x464A`. `hid_fix_rdesc()` obtains the descriptor buffer and changes byte 79 from application mouse (`0x02`) to pointer (`0x01`) when applicable. `HID_BPF_OPS(hp_elite_presenter)` attaches only the descriptor-fixup hook. `probe()` requires descriptor size 264.

## Control Flow

The probe gate validates descriptor length. Descriptor fixup then performs one conditional byte substitution. No event hook is installed.

## State and Persistence Behavior

The program is stateless after attach. Its only persistent effect is the fixed descriptor used when HID core reprobes the device.

## Dependencies and Integration Points

It depends on HID-BPF descriptor fixup hooks and is intended to complement or improve a kernel quirk for the same device.

## Risks and Test Signals

Risks are hard-coded offset assumptions and future firmware descriptors with the same length but different layout. Test signals include both pointer modes appearing as intended, probe rejection on unexpected descriptors, and no event-path overhead.
