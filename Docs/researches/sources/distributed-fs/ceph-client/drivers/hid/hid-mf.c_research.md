# sources/distributed-fs/ceph-client/drivers/hid/hid-mf.c

## Purpose

`hid-mf.c` provides force-feedback support for Mayflash controller adapters that identify as DragonRise devices. These adapters may expose multiple input devices and output reports; the driver pairs each output report with the corresponding input device and creates a memless rumble interface.

## Important APIs, Types, and Functions

- `struct mf_device` stores the HID output report associated with one input device.
- `mf_play()` scales Linux strong/weak rumble magnitudes from 16-bit to 8-bit values, writes weak then strong into the first output field, and sends `HID_REQ_SET_REPORT`.
- `mf_init()` iterates every HID output report, validates it has at least one field with two values, advances through the HID input list, allocates one `mf_device` per input, enables `FF_RUMBLE`, creates memless FF, initializes the output report to zero, and sends that zero report.
- `mf_probe()` applies `id->driver_data` quirks, parses HID, starts hardware with generic FF disabled, and calls `mf_init()`.

## Control Flow

The device ID table marks several Mayflash/DragonRise adapters with `HID_QUIRK_MULTI_INPUT` so each controller port can become a separate input device. Probe applies that quirk before parsing. After hardware start, `mf_init()` walks output reports in descriptor order and expects a matching input device for each one. Playback is straightforward: scale, store into the report, and request a set-report transfer.

## State and Persistence Behavior

Each registered FF device owns a small `mf_device` pointing at its output report. The current rumble values live in HID report field storage. No persistent configuration, workqueue, timer, or sysfs state exists.

## Dependencies and Integration Points

The file integrates HID parsing/startup, HID output reports, input FF memless support, DragonRise/Mayflash IDs, and HID quirk flags. It logs with `dbg_hid`, `hid_info`, and `hid_err`.

## Risks and Edge Cases

- The report-to-input pairing depends on descriptor/list ordering. If an adapter exposes reports and inputs in different order, rumble could target the wrong port.
- If FF creation fails after previous ports were initialized, the function returns an error and probe stops, relying on subsystem cleanup for already-created memless devices.
- It assumes report field 0 values 0 and 1 are weak/strong bytes for all matched devices.
- Some listed devices are marked as "probably work" in comments; hardware coverage may be incomplete.

## Test Signals

Tests should cover multi-input descriptor parsing, matching output-report count to input count, invalid output reports, zero-initialization reports on probe, and playback scaling. Hardware tests should verify each adapter port rumbles independently and that the `HID_QUIRK_MULTI_INPUT` choices produce expected input devices.
