# sources/distributed-fs/ceph-client/drivers/hid/hid-haptic.c

Provides shared HID haptic support for touchpads exposing HID haptic pages. It maps HID haptic reports into Linux `FF_HAPTIC` effects, switches host/device trigger modes, allocates effect buffers, and schedules playback on a workqueue.

Exported helpers include `hid_haptic_feature_mapping()`, `hid_haptic_check_pressure_unit()`, `hid_haptic_input_mapping()`, `hid_haptic_input_configured()`, `hid_haptic_init()`, `hid_haptic_pressure_reset()`, and `hid_haptic_pressure_increase()`. Internal helpers parse waveform/duration lists, fill manual-trigger output report buffers, switch auto-trigger mode, upload/erase/play effects, and destroy FF state.

Device-specific drivers call mapping helpers during HID parsing. After a touchpad input device with auto/manual trigger reports is configured, `hid_haptic_init()` creates the FF device and effect buffers. Userspace uploads `FF_HAPTIC` effects; upload validates waveform/vendor metadata, fills a report buffer, and may switch to host mode. Playback queues work that sends stop then the selected effect.

`struct hid_haptic_device` stores report pointers, mutexes, mode, default trigger, waveform/duration maps, vendor IDs, pressure data, effect buffers, stop effect, and workqueue. Dependencies include HID report helpers, input multitouch, input FF, workqueues, module/device references, and exported GPL symbols.

Risks include shared HID report mutation, complex error unwind through input FF destroy, API asymmetry with declarations in the header, and report layout assumptions. Test signals include feature parsing, pressure units, FF creation/unwind, waveform validation, host-mode switching, playback ordering, erase behavior, and enabled/disabled config builds.
