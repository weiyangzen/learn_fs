# sources/distributed-fs/ceph-client/drivers/media/radio/radio-shark2.c

Purpose: implements USB V4L2 support for the Griffin radioSHARK2, using the local `radio_tea5777` helper for AM/FM tuning and optional LED class devices. Audio is handled by USB audio outside this driver.

Important APIs and functions: USB lifecycle is `usb_shark_probe`, `usb_shark_disconnect`, `usb_shark_release`, and optional PM callbacks. TEA5777 operations are `shark_write_reg` and `shark_read_reg` in `radio_tea5777_ops`. LED handling mirrors the original shark driver through `shark_led_work`, brightness setters, and register/unregister helpers.

Control flow: probe validates interrupt endpoints, allocates device state and a 7-byte buffer, creates a V4L2 device name, registers LEDs, registers the V4L2 device, sets up the embedded `radio_tea5777` with AM support and the `write_before_read` quirk, then calls `radio_tea5777_init` to register the radio video device. Register writes send command `0x81` plus the six TEA5777 bytes; reads send request `0x82`, read three status bytes, and return them to the helper. Resume retunes through `radio_tea5777_set_freq` and reapplies LED state.

State and persistence: `struct shark_device` contains USB/V4L2 objects, the embedded TEA5777 helper state, optional LED work/state/name arrays, and a transfer buffer. All state is volatile and freed via V4L2 device release after disconnect.

Dependencies and integration points: depends on USB interrupt pipes, `radio-tea5777.h`, optional LED class support, workqueues, and the TEA5777 helper's V4L2 controls/ioctls. USB ID matching distinguishes radioSHARK2 with `bcdDevice` 0x0010.

Risks: LED partial-registration cleanup has the same all-slots unregister pattern as `radio-shark.c`. The read path assembles only three bytes and depends on exact firmware report layout. The `write_before_read` quirk means read status can force a pending write, so lock ordering with the helper mutex matters. Debug logging can expose raw register traffic but is module-parameter gated.

Test signals: probe against radioSHARK2 and rejection of radioSHARK, TEA5777 AM/FM tuning, hardware seek through the helper, USB read/write error injection, LED sysfs behavior, suspend/resume retuning, and disconnect during pending LED work or V4L2 access.
