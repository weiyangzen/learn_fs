# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/TUXEDO__Sirius-16-Gen1-and-Gen2.bpf.c

## Purpose
This event quirk suppresses an unwanted F13 key event on TUXEDO Sirius 16 Gen1/Gen2 devices using USB VID/PID `0x048D:0x8910`. It zeroes both array-encoded and bitmap-encoded appearances of HID usage `0x68`.

## Important APIs, Types, And Functions
The program declares only a device-event hook: `ignore_key_fix_event()`. It reads 37-byte report ID 1 reports, scans bytes 3 through 8 for usage `0x68`, and clears bit 0 of byte 22 for bitmap-encoded additional keys. `HID_BPF_OPS(ignore_button)` installs `.hid_device_event`.

## Control Flow
If the incoming report is shorter than 37 bytes, inaccessible, or not report ID 1, the hook returns without changes. Otherwise it clears any F13 usage found in the six-key array area and clears the bit corresponding to F13 in the extended bitmap area. The report length is unchanged.

## State And Persistence
The program is stateless.

## Dependencies And Integration Points
It depends on the target keyboard report layout and HID-BPF event mutation. It integrates after reports are received but before normal input delivery, preventing the unwanted key from reaching userspace.

## Risks
There is no `probe()` descriptor-size guard in the file, so safety relies on VID/PID and runtime report length/report ID checks. If a later firmware changes the F13 bit offset, the array path may still work but the bitmap path may miss or clear the wrong bit.

## Test Signals
Feed report ID 1 with `0x68` in bytes 3-8 and with byte 22 bit 0 set; both should be cleared. Reports with other IDs or length under 37 should be untouched. Functional testing should confirm the spurious F13 key no longer appears.
