# sources/distributed-fs/ceph-client/drivers/media/radio/radio-shark.c

Purpose: implements USB V4L2 tuning support for the Griffin radioSHARK, using the common `snd_tea575x` tuner helper and optional LED class devices. Audio is provided separately by USB audio.

Important APIs and functions: USB lifecycle is `usb_shark_probe`, `usb_shark_disconnect`, `usb_shark_release`, and optional suspend/resume. TEA575x operations are `shark_write_val` and `shark_read_val`. LED helpers include `shark_led_work`, brightness setters, `shark_register_leds`, `shark_unregister_leds`, and `shark_resume_leds`.

Control flow: probe validates expected interrupt endpoints, allocates device state and a 6-byte transfer buffer, assigns a unique V4L2 name, registers LED devices, registers the V4L2 device, populates the embedded `snd_tea575x`, and calls `snd_tea575x_init`. Tuning writes a 32-bit TEA shift-register value over USB interrupt OUT and caches it to avoid redundant transfers. Reads request status with command `0x80`, read interrupt IN status, update cached value, and infer stereo because the hardware does not expose the stereo pin. Disconnect exits the TEA helper under its mutex, unregisters LEDs, and drops the V4L2 reference.

State and persistence: `struct shark_device` stores USB/V4L2 objects, embedded TEA575x state, optional LED work/state/name arrays, a transfer buffer, and the last TEA value. State is volatile and released via the V4L2 device release hook.

Dependencies and integration points: depends on USB interrupt endpoints, `media/drv-intf/tea575x.h`, optional `LEDS_CLASS`, workqueues, and V4L2 device registration performed by the TEA helper. It matches radioSHARK by USB IDs plus `bcdDevice` 0x0001.

Risks: LED registration happens before `v4l2_device_register`, so LED names use the preassigned V4L2 name and need careful cleanup if partial registration fails. `shark_unregister_leds` unregisters all templates even if registration failed partway. Read fallback returns `last_val` after USB errors, which may hide stale hardware state. Stereo is inferred, not measured. `cannot_mute` is set because hardware tuning path lacks mute support.

Test signals: endpoint validation, TEA575x initialization, tuning and status reads over USB, radioSHARK versus radioSHARK2 matching by `bcdDevice`, LED brightness/pulse sysfs behavior, suspend/resume retuning and LED restoration, and disconnect while LED work or tuner ioctls are active.
