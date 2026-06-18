# sources/distributed-fs/ceph-client/drivers/hid/hid-universal-pidff.c

Purpose: generic wrapper for USB PID force-feedback devices, adding broader button mapping and initializing `hid-pidff` with per-device quirks for modern wheels, bases, pedals, and joysticks.

Important APIs, types, and functions: `universal_pidff_input_mapping()` remaps joystick button-page usages beyond the normal joystick range into later key ranges, using `KEY_RESERVED` for overflow so scans are still visible. `universal_pidff_probe()` parses and starts HID without default FF, checks collections for `HID_UP_PID`, then calls `hid_pidff_init_with_quirks()` with `id->driver_data`. `universal_pidff_input_configured()` reduces fuzz/deadzone on axes and special-cases FFBeast joystick ABS_Y.

Control flow: probe exits successfully without FF if no PID usage page exists, allowing multi-interface devices with non-FF sibling interfaces to bind cleanly. If PID exists, pidff initialization errors fail probe. Mapping/configuration hooks run during HID input setup.

State and persistence: no private drvdata. Device-specific behavior is stored in the static ID table through PIDFF quirk bits. Axis settings mutate input device abs parameters.

Dependencies and integration: depends on `usbhid/hid-pidff.h`, HID collection metadata, input mapping/configuration, and a broad device ID table for MOZA, CAMMUS, VRS, FFBeast, PXN/Lite Star, and Asetek devices.

Risks: button remapping spans non-joystick key ranges and may surprise userspace, but preserves events. Probe uses a function pointer assigned to `hid_pidff_init_with_quirks`; the null check is defensive but normally redundant. Collection scanning only detects descriptors that expose the PID usage page.

Test signals: no KUnit tests. Validate with `evtest` for high-number buttons, FF effect upload/playback for each quirk family, and axis fuzz/deadzone behavior.
