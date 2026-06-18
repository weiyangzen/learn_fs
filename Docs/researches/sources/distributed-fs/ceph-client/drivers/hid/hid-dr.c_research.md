# sources/distributed-fs/ceph-client/drivers/hid/hid-dr.c

## Purpose
`hid-dr.c` supports DragonRise USB game controllers. It provides optional rumble force-feedback for product `0x0006`, replaces a broken report descriptor for product `0x0011`, and restores legacy axis mapping behavior for reused generic-desktop axis usages.

## Important APIs, Types, And Functions
When `CONFIG_DRAGONRISE_FF` is enabled, `struct drff_device` stores the output report used for rumble. `drff_play()` translates Linux `FF_RUMBLE` magnitudes to device bytes and sends output reports. `drff_init()` locates the first input device and output report, validates field capacity, registers memless force feedback with `input_ff_create_memless()`, initializes the output report, and sends a stop report. Without the config option, `drff_init()` is an inline no-op. `pid0011_rdesc_fixed[]` is the replacement descriptor for PID `0x0011`, selected by `dr_report_fixup()` when the original size is exactly 101 bytes. `dr_input_mapping()` maps reused HID generic desktop axes to relative or absolute Linux axes based on field flags. `dr_probe()` parses, starts HID without generic FF connection, and initializes DragonRise-specific FF when appropriate.

## Control Flow
Probe calls `hid_parse()` and `hid_hw_start()` with `HID_CONNECT_DEFAULT & ~HID_CONNECT_FF`, because this driver owns force-feedback setup. For PID `0x0006`, it calls `drff_init()` and stops HID again on failure. For PID `0x0011`, HID core invokes `dr_report_fixup()` before parsing and swaps in the fixed descriptor if the descriptor length matches the known broken version. Input mapping handles X/Y/Z/Rx/Ry/Rz usages manually, preserving old behavior where repeated usages are assigned by low nibble rather than rejected as duplicates.

`drff_play()` receives memless FF effects from the input layer. If either strong or weak magnitude is nonzero, it scales both from 16-bit to 8-bit, avoids weak value `0x0a` because it triggers bad behavior, sends a setup report with command `0x51`, then sets run bytes `0xfa 0xfe`. For stop, it sends command `0xf3`. It clears motor bytes before the final request.

## State And Persistence
The FF path allocates one `drff_device` per input FF instance and stores the HID output report pointer. Report field values are reused and mutated for each effect. There is no persistent device programming. Descriptor replacement is static and per-parse.

## Dependencies And Integration Points
The file depends on HID core, input force-feedback, output reports, conditional `CONFIG_DRAGONRISE_FF`, and DragonRise vendor IDs from `hid-ids.h`. It exposes ordinary joystick/gamepad input events and optionally `FF_RUMBLE` through the input subsystem.

## Risks
FF setup assumes the first HID input and first output report are the correct ones and that field zero has at least seven values. Device variants with different report layouts can fail or receive wrong rumble bytes. The PID `0x0011` descriptor replacement is gated only by product and size, so firmware variants with same size but different layout could be misparsed. The legacy axis mapping intentionally accepts duplicated usages, which may preserve compatibility but can also hide descriptor quality issues.

## Test Signals
Test with PID `0x0006` should show `FF_RUMBLE` in `evtest`/`fftest`, correct start/stop motor behavior, and no generic HID FF duplicate registration. PID `0x0011` should parse using the fixed descriptor and expose two axes plus ten buttons. Axis mapping should remain stable for reused axis usages, and builds should cover both `CONFIG_DRAGONRISE_FF=y` and disabled configurations.
