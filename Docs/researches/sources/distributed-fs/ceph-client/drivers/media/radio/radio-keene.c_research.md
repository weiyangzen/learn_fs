# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-keene.c

Purpose: USB V4L2 modulator driver for the Keene FM transmitter. It exposes a transmit radio node that sets FM frequency, mute/play state, stereo/mono, power level, preemphasis, and compression gain through HID-style USB control reports.

Important types/APIs: `struct keene_device` stores USB/V4L2/video/control state, mutex, 8-byte report buffer, current frequency, TX/gain/PA settings, stereo, mute, and preemphasis flags. Core functions are `keene_cmd_main`, `keene_cmd_set`, V4L2 modulator/frequency/control ioctls, USB probe/disconnect, suspend/resume, and release.

Control flow: probe filters a shared Logitech VID/PID by product string, allocates state/buffer, creates four controls, registers V4L2/video, stores the V4L2 device in USB interface data, waits for hardware settle, sends an initial idle command at 95.16 MHz, registers the radio node, and sets controls. Frequency and mute call `keene_cmd_main`; stereo/preemphasis/compression call `keene_cmd_set`; resume replays mode and frequency after delay.

State and persistence: runtime state mirrors desired transmitter settings and current frequency. Hardware may preserve settings while powered but the driver replays them on resume. No disk persistence.

Dependencies and integration: USB HID-class interface matching, V4L2 modulator API (`VFL_DIR_TX`), controls for tune power/preemphasis/compression, and control events.

Risks: shared USB ID makes product-string filtering critical. Power-level conversion writes a computed register value and leaves `db2tx` index dependent on control step/min. Suspend/resume do not take the mutex, unlike normal file ops. Test signals include real-device product filtering, modulator ioctls, control range tests, suspend/resume replay, mute/play behavior, and disconnect while open.
