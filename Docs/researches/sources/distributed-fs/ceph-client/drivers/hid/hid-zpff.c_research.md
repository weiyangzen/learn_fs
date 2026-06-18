# sources/distributed-fs/ceph-client/drivers/hid/hid-zpff.c

## Purpose

`hid-zpff.c` adds optional force-feedback support for Zeroplus-based USB controllers. When `CONFIG_ZEROPLUS_FF` is enabled, it installs a memless rumble device and writes scaled motor strengths into a HID output report.

## Important APIs, Types, and Functions

- `struct zpff_device`: stores the output report used for force feedback.
- `zpff_play`: scales strong/weak magnitudes from 16-bit input FF values to 7-bit report fields and sends `HID_REQ_SET_REPORT`.
- `zpff_init`: validates four output report fields, allocates state, creates memless FF, initializes the report, and sends a neutral report.
- `zp_probe`: parses and starts HID with default connection minus generic FF, then calls `zpff_init`.
- `zp_devices[]`: binds two Zeroplus product IDs.

## Control Flow

Probe parses the device and starts HID while suppressing generic force-feedback connection. If the config option is enabled, `zpff_init` finds the first HID input device, validates the output report layout, creates memless FF on that input, initializes constant report fields, and sends it. Later FF effects call `zpff_play`, which updates fields 2 and 3 and requests SET_REPORT.

## State and Persistence Behavior

`zpff_device` persists as the memless FF private data. The HID report object is owned by HID core; the driver mutates its field values on each effect. There is no explicit free path for `zpff_device`; it relies on input FF lifecycle or represents a memory-ownership detail to verify.

## Dependencies and Integration Points

It depends on HID report validation, HID raw request plumbing, Linux input FF memless, and `CONFIG_ZEROPLUS_FF`. User-space sees standard `FF_RUMBLE` on the controller input device.

## Risks and Edge Cases

- `zp_probe` ignores the return value from `zpff_init`, so HID binding succeeds even if FF setup failed.
- Output report field indices are assumed fixed after validation; different report layouts will disable FF.
- The strong/weak motor ordering intentionally follows observed hardware rather than the datasheet.
- State allocation/free ownership should be checked when changing input FF teardown.

## Test Signals

- Build with and without `CONFIG_ZEROPLUS_FF`.
- Run `fftest` and verify both motors scale from 0 to 0x7f.
- Attach unsupported report-layout variants and confirm the driver still binds without FF.
- Check disconnect under active rumble for leaks or stale report access.
