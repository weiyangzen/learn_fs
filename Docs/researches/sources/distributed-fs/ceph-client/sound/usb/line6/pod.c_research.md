# sources/distributed-fs/ceph-client/sound/usb/line6/pod.c

## Purpose
`pod.c` is the USB driver for older Line 6 POD-family devices. It registers supported USB IDs, defines device capabilities and endpoints, initializes PCM and control/MIDI support through the common Line 6 core, exposes POD sysfs metadata, parses firmware/system messages, and provides an ALSA mixer control for hardware monitor playback volume.

## Important APIs, Types, And Functions
The main private type is `struct usb_line6_pod`, which embeds `struct usb_line6` and stores `monitor_level`, `startup_progress`, `serial_number`, `firmware_version`, and `device_id`. The USB entry point is `pod_probe()`, which delegates to `line6_probe()`. Initialization is in `pod_init()`. Message handling is in `line6_pod_process_message()`. Startup sequencing is in `pod_startup()`. Mixer callbacks are `snd_pod_control_monitor_info()`, `snd_pod_control_monitor_get()`, and `snd_pod_control_monitor_put()`. Sysfs attributes are `device_id`, `firmware_version`, and `serial_number`.

## Control Flow And State
During probe, `line6_probe()` allocates the device object and calls `pod_init()`. `pod_init()` installs `process_message` and `startup` callbacks, adds the `pod` sysfs attribute group, initializes PCM with fixed 24-bit packed stereo parameters near 39.0625 kHz, and registers the monitor control. For control-capable devices it initializes `monitor_level` to `POD_SYSTEM_INVALID` and schedules delayed startup.

Startup begins with `POD_STARTUP_VERSIONREQ`, sends an async version request, and waits for `line6_pod_process_message()` to parse the identity response. The message parser recognizes the universal version header, fills firmware version and device ID from fixed offsets, advances startup to setup, and schedules startup work immediately. Setup reads the serial number and registers the ALSA card. System sysex messages for `POD_MONITOR_LEVEL` update cached monitor state. Mixer writes call `pod_set_system_param_int()`, which builds a Line 6 sysex system message with a 16-bit nibble-encoded value.

## State And Persistence
All state is volatile. The device itself persists monitor and firmware state; the driver caches monitor level, firmware version, serial number, and device ID. ALSA card registration is deliberately delayed until after version/setup to avoid PODxt Live device errors.

## Dependencies And Integration Points
The driver integrates with `line6_probe()`, `line6_disconnect()`, PM callbacks, Line 6 sysex helpers, `line6_init_pcm()`, ALSA controls, and ALSA card sysfs device attributes. Device capabilities include combinations of `LINE6_CAP_CONTROL`, `LINE6_CAP_CONTROL_MIDI`, `LINE6_CAP_PCM`, and `LINE6_CAP_HWMON`.

## Risks And Edge Cases
Message parsing uses fixed offsets in firmware responses and sysex payloads, so malformed or short messages could be hazardous if the common message layer does not validate length. Mixer put updates local state before confirming USB delivery. Card registration errors are logged but not propagated from startup work. Devices without `LINE6_CAP_CONTROL` do not run the delayed startup path here, so registration behavior relies on the common probe flow.

## Test Signals
Test signals include matching every ID table entry to the correct property entry, delayed startup ordering, firmware/device ID parsing, sysfs formatting, monitor mixer get/put and sysex encoding, PCM constraints for 24-bit packed stereo, control-only Pocket POD behavior, and disconnect/PM callback integration.
