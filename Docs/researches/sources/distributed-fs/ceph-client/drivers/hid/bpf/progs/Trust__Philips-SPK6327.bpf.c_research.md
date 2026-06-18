# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Trust__Philips-SPK6327.bpf.c

## Purpose
This descriptor quirk fixes a Trust/Philips SPK6327 keyboard whose modifier keys are declared as Array input instead of Variable input, causing modifiers such as Ctrl, Alt, and Super to behave like Left Shift.

## Important APIs, Types, And Functions
The match is USB VID `0x145F`, PID `0x024B`. `hid_fix_rdesc()` reads the descriptor and changes byte 101 from `0x00` to `0x02`. `HID_BPF_OPS(trust_spk6327)` installs descriptor fixup only. `probe()` applies the program to interface 1 by accepting descriptor size 169 and rejecting interface 0 size 62.

## Control Flow
The hook obtains up to 4096 descriptor bytes. If available and the modifier Input flags byte at offset 101 is `0x00`, it changes it to `0x02`. The descriptor length is unchanged. Probe is a simple descriptor-size gate.

## State And Persistence
There is no mutable runtime state.

## Dependencies And Integration Points
The file depends on HID-BPF descriptor mutation and the target keyboard's fixed interface layout. It integrates before HID parsing so modifier usages become independent variable bits.

## Risks
The offset is specific to the 169-byte interface. If another firmware changes descriptor size or offset, the quirk will reject or fail to fix. The byte guard prevents rewriting a descriptor already fixed by firmware or kernel changes.

## Test Signals
Descriptor dump should show the modifier Input item flags changed to `0x02`. Functional tests should press LCtrl, LAlt, Super, and Shift independently and confirm they report distinct modifiers.
