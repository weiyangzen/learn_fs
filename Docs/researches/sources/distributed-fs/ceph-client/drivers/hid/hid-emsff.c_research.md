# sources/distributed-fs/ceph-client/drivers/hid/hid-emsff.c

## Purpose
`hid-emsff.c` adds rumble force-feedback support for the EMS Trio Linker Plus II USB adapter. It disables generic HID force-feedback setup and registers a device-specific memless FF handler that writes scaled motor strengths into the adapter's output report.

## Important APIs, Types, And Functions
`struct emsff_device` stores the HID output report pointer used for effects. `emsff_play()` converts Linux `FF_RUMBLE` weak and strong magnitudes from 16-bit to 8-bit values, writes them into output report field values 1 and 2, and sends a `HID_REQ_SET_REPORT`. `emsff_init()` locates the first HID input and first output report, validates the report has at least one field and seven values, allocates `emsff_device`, sets `FF_RUMBLE`, registers memless force feedback, initializes the report to command byte `0x01` with zero motors, sends it, and logs support. `ems_probe()` parses, starts HID with generic FF disabled, and initializes EMS FF.

## Control Flow
Probe first parses the HID descriptor. It starts HID using `HID_CONNECT_DEFAULT & ~HID_CONNECT_FF` so the custom implementation owns rumble registration. `emsff_init()` then binds the first input device to a memless FF callback. When user space plays a rumble effect, input core calls `emsff_play()`, which mutates the already discovered output report and sends it to hardware.

## State And Persistence
The only private state is the allocated `emsff_device` retained by the input FF memless layer. The current report values live in the HID report object and are overwritten per effect. There is no persistent hardware programming.

## Dependencies And Integration Points
The driver depends on HID core, Linux input force-feedback, HID output reports, and EMS vendor/product IDs from `hid-ids.h`. It exposes `FF_RUMBLE` to user space through the input device created by generic HID parsing.

## Risks
The implementation assumes the first input and first output report are the correct endpoints and that report field zero has at least seven values. Variants with different layouts will fail initialization or receive incorrect bytes. Allocation uses normal kernel heap rather than devm; cleanup is delegated to input FF ownership once `input_ff_create_memless()` succeeds. There is no explicit remove callback because HID/input teardown handles normal lifetime.

## Test Signals
Test signals include successful probe for `USB_DEVICE_ID_EMS_TRIO_LINKER_PLUS_II`, `FF_RUMBLE` advertised by `evtest`, `fftest` producing weak and strong motor changes, zeroed initial report on probe, graceful failure on descriptors without output reports, and no duplicate generic FF registration.
