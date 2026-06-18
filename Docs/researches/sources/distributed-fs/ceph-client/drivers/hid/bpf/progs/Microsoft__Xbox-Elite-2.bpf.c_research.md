# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Microsoft__Xbox-Elite-2.bpf.c

## Purpose
This descriptor quirk fixes Bluetooth Xbox Elite Series 2 controller paddle reporting. The original descriptor places paddle usages in a consumer/assign-selection block that the kernel does not interpret properly, yielding `KEY_UNKNOWN`; the program replaces that block with a gamepad button collection for buttons 21-24.

## Important APIs, Types, And Functions
The match is Bluetooth Microsoft VID/PID for Xbox Elite 2. `OFFSET_ASSIGN_SELECTION` identifies the descriptor block to replace, and `ORIGINAL_RDESC_SIZE` gates probe. `rdesc_assign_selection[]` contains the expected original bytes and `fixed_rdesc_assign_selection[]` contains same-sized replacement bytes. `_Static_assert`s enforce equal replacement length and in-bounds offset. `hid_fix_rdesc()` verifies and copies the replacement; `probe()` repeats the size/content validation.

## Control Flow
Probe only accepts the known keyboard interface descriptor size and expected original block. Descriptor fixup then checks the same block with `__builtin_memcmp()` and copies the replacement into place. The hook returns 0 because descriptor length is unchanged.

## State And Persistence
The program is stateless aside from descriptor bytes modified during HID parsing.

## Dependencies And Integration Points
It depends on HID-BPF helpers and on the exact Bluetooth descriptor layout. It integrates by changing how the HID parser classifies the paddles, causing them to appear as gamepad buttons rather than unknown keyboard/consumer usages.

## Risks
The fix is intentionally exact-match. Firmware changes to the descriptor block or size will reject the quirk. If Microsoft changes paddle usages but leaves the same size, the memcmp protects against writing over an unexpected layout.

## Test Signals
Tests should verify `probe()` rejects descriptors with changed size or changed assign-selection bytes, accepts the known descriptor, and exposes paddles as buttons 21-24 without `KEY_UNKNOWN` events.
