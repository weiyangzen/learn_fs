# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Rapoo__M50-Plus-Silent.bpf.c

## Purpose
This descriptor quirk enables the two side buttons on the Rapoo M50 Plus Silent mouse. The original descriptor has five button bits but a Usage Maximum of only 3, so Linux cannot assign usages to buttons 4 and 5.

## Important APIs, Types, And Functions
The match is USB Rapoo VID `0x24AE`, PID `0x2015`, descriptor size 186. `hid_rdesc_fixup_rapoo_m50()` edits `data[17]` from `0x03` to `0x05`. `HID_BPF_OPS(rapoo_m50)` provides `.hid_rdesc_fixup`; `probe()` accepts only descriptor size 186.

## Control Flow
At descriptor fixup, the hook reads the descriptor and changes the Usage Maximum byte at offset 17 if it still has the bad value 3. It does not alter report count, size, or descriptor length because the descriptor already reserves five button bits.

## State And Persistence
There is no runtime state.

## Dependencies And Integration Points
The file depends on HID-BPF helpers and a stable mouse descriptor. It integrates with the normal mouse input parser so side buttons become standard button usages.

## Risks
The code relies on exact descriptor size and offset. Future descriptors may need different offsets. If the usage maximum is already fixed, the byte guard leaves it unchanged.

## Test Signals
Descriptor dump should show Usage Maximum 5 for the button collection. Runtime testing should produce left, right, middle, back, and forward button events.
