# sources/distributed-fs/ceph-client/sound/usb/line6/podhd.c

## Purpose
`podhd.c` supports Line 6 POD HD and POD X3-generation USB devices. It defines device-specific PCM formats, startup handshakes, optional control-interface claiming, sysfs metadata, and an ALSA monitor-volume control for models with hardware-monitor control support.

## Important APIs, Types, And Functions
`struct usb_line6_podhd` embeds `struct usb_line6` and caches `serial_number`, `firmware_version`, and `monitor_level`. Important functions are `podhd_probe()`, `podhd_init()`, `podhd_startup()`, `podhd_dev_start()`, `podhd_disconnect()`, `podhd_set_monitor_level()`, and the `snd_podhd_control_monitor_*()` ALSA control callbacks. The USB ID table maps device products to `podhd_properties_table`.

## Control Flow And State
Probe delegates to `line6_probe()` with a PODHD property entry. `podhd_init()` installs disconnect/startup callbacks. For devices with a separate control interface, it finds and claims `ctrl_if` with `usb_driver_claim_interface()`. Devices with `LINE6_CAP_CONTROL_INFO` get a `podhd` sysfs group for firmware and serial number and delay card registration until startup work completes. PCM devices call `line6_init_pcm()` with either standard 2-in/2-out 48 kHz 24-bit packed properties or POD X3 8-channel capture properties.

`podhd_dev_start()` performs a vendor request sequence, reads three firmware bytes, reads a small range of device memory with `line6_read_data()`, then sends a standard `SET_FEATURE`. `podhd_startup()` calls that handshake, reads the serial number, and registers the ALSA card. Hardware monitor control uses a static 101-entry lookup table of little-endian IEEE float encodings for 0.0 through 1.0. `podhd_set_monitor_level()` clamps user values to 0..100, patches the raw command payload, sends it with `line6_send_raw_message()`, and updates cached state.

## State And Persistence
Driver state is volatile: claimed-interface ownership, cached firmware/serial/monitor values, PCM stream state held in the common Line 6 PCM layer, and ALSA card registration status. Device-side firmware and monitor settings persist according to device behavior, not this code.

## Dependencies And Integration Points
This file depends on the common Line 6 driver and PCM core, ALSA controls/sysfs, USB interface claiming/release, vendor control transfers, and model capabilities such as `LINE6_CAP_PCM`, `LINE6_CAP_CONTROL`, `LINE6_CAP_CONTROL_INFO`, `LINE6_CAP_HWMON`, `LINE6_CAP_HWMON_CTL`, and `LINE6_CAP_IN_NEEDS_OUT`.

## Risks And Edge Cases
Control interface claiming must be paired with release in `podhd_disconnect()`; errors after claiming can leak ownership unless common cleanup calls the disconnect hook. The monitor command is mostly magic constants, so device firmware changes could break it silently. `podhd_dev_start()` logs some failures but startup still attempts registration through `podhd_startup()`. The code assumes MIDI 2.0-style UMP is irrelevant and uses Line 6-specific raw/control paths.

## Test Signals
Tests should cover ID/property alignment, control-interface claim and release, POD X3 8-channel capture constraints, 48 kHz 24-bit PCM setup, sysfs formatting, startup vendor request sequencing, monitor clamping and payload bytes, direct registration path for devices without control-info, and suspend/resume/disconnect behavior.
