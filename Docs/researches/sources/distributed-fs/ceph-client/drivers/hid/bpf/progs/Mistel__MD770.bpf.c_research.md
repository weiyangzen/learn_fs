# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Mistel__MD770.bpf.c

## Purpose
This descriptor quirk fixes the second interface of the Mistel MD770 keyboard so NKRO reports beyond the first six simultaneous key presses are parsed correctly. The bad descriptor marks the large key bitmap as Array input; it should be Variable input.

## Important APIs, Types, And Functions
The match is USB Holtek VID `0x04D9`, PID `0x0339`, descriptor size 203. `hid_rdesc_fixup_mistel_md770()` edits descriptor byte 201 from `0x00` to `0x02` when present. `HID_BPF_OPS(mistel_md770)` publishes only the descriptor hook. `probe()` gates on exact descriptor size.

## Control Flow
Descriptor fixup reads the full descriptor and checks `data[201]`. If it is the erroneous Input flags byte `0x00`, it changes it to `0x02` so the preceding keyboard usages are parsed as `Data,Var,Abs`. It returns 0 because no length changes occur.

## State And Persistence
There is no runtime state.

## Dependencies And Integration Points
The program depends on HID-BPF descriptor mutation before HID parsing. It integrates with the keyboard input path by making the second interface's bitmap usable for rollover keys.

## Risks
The fix is exact-size and offset based. A firmware variant with the same size but different layout could either be left unchanged due to the byte guard or require a new offset. There is no event hook, so any remaining malformed runtime reports are outside this quirk.

## Test Signals
A descriptor dump should show byte 201 changed to `0x02`. Functional testing should hold more than six keys and confirm the second interface emits valid key events instead of being ignored.
