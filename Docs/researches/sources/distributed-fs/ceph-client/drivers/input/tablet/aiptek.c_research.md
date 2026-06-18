# sources/distributed-fs/ceph-client/drivers/input/tablet/aiptek.c

## Purpose
`aiptek.c` supports Aiptek HyperPen USB tablets and related Genius/KYE devices. It decodes six proprietary report formats, programs tablet mode and resolution through HID class control reports, exposes extensive sysfs tuning attributes, and reports stylus, mouse, macro-key, tilt, wheel, pressure, and diagnostic events.

## Important APIs, types, and functions
`struct aiptek` holds the input device, USB interface/URB/DMA buffer, discovered feature codes, current and staged settings, packet/jitter state, macro tracking, and USB path. `struct aiptek_settings` contains pointer mode, coordinate mode, tool mode, tilt, wheel, button mappings, and command delays. Important functions include `aiptek_irq()`, `aiptek_open()`, `aiptek_close()`, `aiptek_set_report()`, `aiptek_get_report()`, `aiptek_command()`, `aiptek_query()`, `aiptek_program_tablet()`, the sysfs show/store functions, `aiptek_probe()`, and `aiptek_disconnect()`.

## Control flow
Probe allocates input and USB resources, initializes default settings and capabilities, finds an interrupt-in endpoint, fills the URB, then tries several programming delays until tablet queries return sane X limits. `aiptek_program_tablet()` sends resolution, model, ODM, firmware, X/Y size, pressure, coordinate-mode, macro-key, and autogain commands. Runtime interrupts decode report 1 relative motion, report 2 stylus absolute data, report 3 mouse absolute data, reports 4/5 macro keys from stylus or mouse, and report 6 official macro reports. Sysfs stores update `newSetting`; writing `execute` copies staged settings to `curSetting` and reprograms hardware.

## State and persistence
Settings are per-device in memory. `curSetting` is active, while `newSetting` is staged until `execute`. Hardware is reprogrammed with those settings but the driver does not persist them across unplug or reboot. Runtime state includes event count, diagnostic code, jitter delay window, previous tool, and last macro key pressed.

## Dependencies and integration points
The driver uses USB input APIs, HID `SET_REPORT`/`GET_REPORT` control messages, unaligned little-endian helpers, input ABS/REL/KEY/MSC events, sysfs device groups attached to the USB driver, and module parameters `programmableDelay` and `jitterDelay`.

## Risks
This is a large legacy parser with many mode-dependent paths. Sysfs settings are not protected by a dedicated lock against interrupt handling, so staged/active changes around `execute` can race with event reporting. `store_tabletWheel()` accepts any integer despite defined wheel range constants. `map_str_to_val()` uses prefix matching by write length, so short strings can match unexpectedly. Macro index checks compare signed values with `ARRAY_SIZE()` and report 6 releases neighboring keys in a non-obvious way. Control programming failures during probe are partly inferred from axis size rather than direct error checks.

## Test signals
Use USB ID coverage for Aiptek and KYE IDs, endpoint discovery failure tests, report decoding fixtures for all six report IDs, pointer-mode rejection diagnostics, relative/absolute mismatch diagnostics, jitter delay transitions, macro press/release behavior, sysfs parse/execute semantics, programming-delay fallback, and disconnect/open URB lifetime.
