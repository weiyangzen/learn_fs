# sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-pidff.c

## Purpose

`hid-pidff.c` implements Linux input force-feedback support for USB HID Physical Interface Device (PID) force-feedback devices. It discovers PID output/feature reports, maps Linux `struct ff_effect` data into PID report fields, handles common non-compliant device layouts through quirks, and registers `input_ff` callbacks for upload, erase, playback, gain, and autocenter.

The file is not a standalone USB driver. It is an exported helper used by HID drivers after a `struct hid_device` has been parsed and has an input device. Its public entry points are `hid_pidff_init_with_quirks()` and the compatibility wrapper `hid_pidff_init()`.

## Important APIs, Types, And Data

- `struct pidff_device` is the central runtime state. It stores the backing `hid_device`, discovered PID reports, arrays of resolved `pidff_usage` field/value pointers for each PID report type, per-Linux-effect PID block IDs and loop state, special HID fields, lookup tables for enumerated usages, an active quirk mask, and discovered effect/axis counts.
- `struct pidff_usage` ties a PID usage to a `struct hid_field *` and the exact `s32 *value` slot to write before calling `hid_hw_request()`.
- `struct pidff_effect` tracks the device-side PID block ID, whether duration is infinite, and the currently requested loop count for a Linux effect slot.
- The PID usage tables encode HID PID usage IDs and define array indexes used throughout the driver.
- Quirk bits come from `hid-pidff.h`: missing delay, missing parameter block offset, permissive device-control logical minimum, fixed conditional direction, periodic-as-sine, and missing negative condition fields.
- The file exports `hid_pidff_init_with_quirks()` with `EXPORT_SYMBOL_GPL`; `hid_pidff_init()` delegates with zero initial quirks.

## Control Flow

Initialization starts in `hid_pidff_init_with_quirks()`. It rejects devices without output reports, allocates `pidff_device`, starts HID I/O, scans output and feature report lists with `pidff_find_reports()`, validates required reports with `pidff_reports_ok()`, resolves report fields with `pidff_init_fields()`, fetches pool information, sets full device gain, probes autocenter support, validates the device-managed pool, then creates the Linux force-feedback device with `input_ff_create()`.

Report discovery is split into `pidff_find_reports()`, `pidff_find_fields()`, `pidff_find_special_fields()`, and `pidff_find_effects()`. These identify required reports, bind usage/value slots, discover selector/array fields, detect optional missing-field quirks, and expose supported FF capabilities in `dev->ffbit`.

Effect upload is handled by `pidff_upload_effect()`. For a new effect it requests a device-side block through `pidff_request_effect_upload()`, increments `effect_count`, and stores the returned PID block ID. For both new and replacement effects it updates `is_infinite`, points `PID_EFFECT_BLOCK_INDEX` at the stored block, emits `SET_EFFECT` if generic parameters changed, then emits the type-specific report: constant, periodic, ramp, or condition. Envelope reports are sent only when non-zero and changed.

Playback flows through `pidff_playback()`, which avoids resending an unchanged infinite-loop playback request, stores the new loop count, and calls `pidff_playback_pid()`. Erase waits for pending HID I/O, sends stop and block-free reports, then decrements the active effect count. Gain and autocenter map to `pidff_set_gain_report()` and `pidff_autocenter()`.

## State And Persistence Behavior

All state is in memory and bound to the input force-feedback device through `dev->ff->private`. The HID device stores report descriptors and field values; this file writes those field values directly before submitting HID SET/GET report requests. No state is persisted across disconnect, module unload, or reboot.

Important mutable state includes the `effect[]` array, `effect_count`, per-report value slots, and active quirk mask. `effect_count` is used to reset/enable actuators when the first effect is uploaded and to reflect erase operations. `pidff->quirks` can be both seeded by callers and extended during field detection.

## Dependencies And Integration Points

- Depends on Linux HID core APIs such as `hid_hw_request()`, `hid_hw_wait()`, `hid_device_io_start()`, `hid_device_io_stop()`, report enums, HID usages, and HID fields.
- Integrates with Linux input force feedback through `input_ff_create()` and callbacks assigned on `struct ff_device`.
- Exposes FF capabilities through `dev->ffbit` and supports `FF_CONSTANT`, `FF_RAMP`, `FF_PERIODIC` waveforms, conditional effects, `FF_GAIN`, and `FF_AUTOCENTER` when available.
- Depends on `hid-pidff.h` for public function declarations and quirk definitions.

## Risks And Edge Cases

- Report discovery is descriptor-sensitive. Non-compliant HID PID descriptors can cause `-ENODEV`, reduced capabilities, or wrong field writes; quirks mitigate only known missing fields and known control/direction problems.
- `pidff_set_effect_direction()` currently enables the single direction value and has unreachable/moribund per-axis logic after an early return.
- `pidff_request_effect_upload()` polls up to 60 GET_REPORT attempts. Devices with slow or malformed block-load status can delay uploads or return `-EIO`, `-ENOSPC`, or `-EREMOTEIO`.
- The autocenter probe temporarily creates and erases an effect and assumes a built-in spring at the minimum effect ID when the allocated ID is minimum plus one.
- Time scaling depends on HID unit exponents and can lose precision by repeated multiply/divide by 10.

## Test Signals

- Probe logs should show successful PID init, active quirk mask, effect memory count, and optional pool information.
- `evtest`, `fftest`, SDL/evdev force-feedback tests, or game force-feedback paths should be able to upload, replay, stop, and erase supported effects.
- Descriptor-coverage tests should exercise devices with missing delay/PBO/negative coefficient/saturation/deadband fields and verify that capabilities are preserved only when report layouts are still usable.
- Fault injection around GET_REPORT/SET_REPORT timeouts should cover upload polling, reset, pool fetch, gain, and autocenter error paths.
