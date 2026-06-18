# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Thrustmaster__TCA-Yoke-Boeing.bpf.c

## Purpose
This descriptor quirk fixes the Thrustmaster TCA Yoke Boeing joystick descriptor so non-existing axes do not appear in Linux. Two vendor input fields are incorrectly marked as data inputs; the program marks them as constants.

## Important APIs, Types, And Functions
The match is USB Thrustmaster PID `PID_TCA_YOKE_BOEING`. `hid_fix_rdesc_tca_yoke()` expects descriptor length 148, reads the descriptor, checks Generic Desktop Joystick at the beginning, and edits Input flag bytes after offsets 90 and 103. `probe()` rejects devices whose offset 91 is no longer the original `0x02`, which means the kernel or firmware may already be fixed.

## Control Flow
Descriptor fixup returns early if size is not 148, data is unavailable, or the descriptor does not start with Usage Page Generic Desktop / Usage Joystick. If both relevant items are Input items, it changes bytes 91 and 104 to `0x03` (`Constant, Variable, Absolute`). It returns 0 because the descriptor length is unchanged.

## State And Persistence
There is no state.

## Dependencies And Integration Points
It depends on HID-BPF helpers and the exact joystick descriptor layout. It integrates with the joystick input stack by preventing phantom axes from being created.

## Risks
The `probe()` check only tests one of the changed bytes, while fixup changes two. Firmware variants with partial changes may need additional handling. Offset-based descriptor edits are sensitive to layout changes, but the start-of-descriptor and input-item checks reduce accidental writes.

## Test Signals
Descriptor tests should show bytes 91 and 104 changed from data input to constant input for the original descriptor. Runtime joystick enumeration should no longer include the non-existing axes while hat, buttons, and real axes remain.
