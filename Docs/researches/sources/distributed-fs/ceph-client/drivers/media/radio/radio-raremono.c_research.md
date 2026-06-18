# sources/distributed-fs/ceph-client/drivers/media/radio/radio-raremono.c

Purpose: provides V4L2 support for Thanko's Raremono, a USB AM/FM/SW receiver using a si4734 behind firmware that presents the same USB IDs as the Si470x reference design.

Important APIs and functions: USB lifecycle is `usb_raremono_probe` and `usb_raremono_disconnect`. `raremono_cmd_main` sends the firmware frequency/band command over HID control messages. V4L2 ioctls include querycap, tuner get/set, frequency get/set, and frequency-band enumeration.

Control flow: probe allocates device state and a 64-byte buffer, performs a distinguishing GET_REPORT against the shared Si470x USB ID, rejects real Si470x devices, registers V4L2 state, initializes a video device, tunes FM 95.160 MHz, and registers the radio node. Frequency setting chooses FM, AM, or shortwave based on requested V4L2 frequency gaps, clamps to the selected band, converts to kHz or 10 kHz units for FM, and sends a 3-byte HID report. Tuner status reads a signal report and scales signal from returned bytes.

State and persistence: `struct raremono_device` stores USB/V4L2 objects, mutex, shared HID buffer, current band, and current frequency in kHz. No state is persistent beyond the device session.

Dependencies and integration points: uses USB control transfers with HID report requests, V4L2 frequency-band APIs, unaligned big-endian helpers for the device-ID probe, and a V4L2 video device with the radio/tuner capabilities. It intentionally shares ID space with `radio-si470x-usb.c` and cooperates via runtime device identification.

Risks: the firmware hides many si4734 features, so the driver exposes only basic tuning and signal strength. The band selection heuristic depends on gaps between AM/SW/FM ranges. There is no explicit mute, seek, RDS, or power management. Signal reporting uses an opaque vendor report with long timeout. If both Raremono and Si470x matching logic drift, one driver can bind the wrong product.

Test signals: binding tests against both Raremono and Si470x reference devices, `VIDIOC_ENUM_FREQ_BANDS` for all three bands, AM/SW/FM frequency clamp behavior, signal read failures, disconnect during ioctl, and `v4l2-compliance` for basic tuner ioctls.
