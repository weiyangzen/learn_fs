# sources/distributed-fs/ceph-client/drivers/hid/hid-megaworld.c

## Purpose

`hid-megaworld.c` adds force-feedback rumble support for Mega World gamepads. The generic HID/input mapping handles normal controls; this driver locates the device's output report fields and wires Linux `FF_RUMBLE` events to the report values expected by the controller.

## Important APIs, Types, and Functions

- `struct mwctrl_device` stores the selected output report and pointers to the weak/strong magnitude fields inside that report.
- `mwctrl_play()` is the memless force-feedback callback. It scales 16-bit Linux rumble magnitudes down by eight bits, writes strong and weak values into the HID report fields, and sends `HID_REQ_SET_REPORT`.
- `mwctrl_init()` validates output report fields, gets the first input device, allocates per-FF data, enables `FF_RUMBLE`, creates a memless FF device, initializes the report's constant field, and stores weak/strong field pointers.
- `mwctrl_probe()` parses the device, starts HID with default connections except generic FF, and initializes rumble.

## Control Flow

Probe calls `hid_parse()`, starts hardware with `HID_CONNECT_DEFAULT & ~HID_CONNECT_FF`, then `mwctrl_init()`. Initialization requires at least one HID input, validates output report values for indices 0 through 3, allocates `mwctrl_device`, registers a memless FF handler on the first input device, selects the output report, writes the fixed first field value `0x02`, and records field 2 as strong and field 3 as weak. Later FF playback calls update the report and send it synchronously through HID core.

## State and Persistence Behavior

The only persistent driver state is the allocated `mwctrl_device` retained by input FF core and pointers into HID report storage. Rumble state is not separately cached; the current effect lives in the report values. There is no suspend/resume logic or nonvolatile configuration.

## Dependencies and Integration Points

The driver depends on HID report validation, HID output requests, Linux input FF memless support, and Mega World VID/PID definitions from `hid-ids.h`. It deliberately disables generic HID force feedback to avoid duplicate ownership of the output report.

## Risks and Edge Cases

- `mwctrl_init()` loops over output report value indices and uses the last validated report; unusual descriptors with multiple output reports could select an unintended report.
- It assumes field 2 is strong and field 3 is weak, with field 0 fixed to `0x02`; descriptor changes could break rumble silently.
- No remove callback is provided; cleanup relies on HID/input teardown and the FF core's ownership of the allocated data.
- Magnitudes are truncated from 16 bits to 8 bits, so low-level effects may lose precision.

## Test Signals

Test probe failure with no inputs, missing/short output reports, memless FF creation failure, and successful rumble playback writing weak/strong bytes then sending `SET_REPORT`. Hardware validation should verify both actuators respond with the expected strength mapping and stop when zero magnitudes are sent.
