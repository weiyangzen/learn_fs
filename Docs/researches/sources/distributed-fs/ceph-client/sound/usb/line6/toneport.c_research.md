# sources/distributed-fs/ceph-client/sound/usb/line6/toneport.c

## Purpose
`toneport.c` supports Line 6 GuitarPort, TonePort, and POD Studio USB audio devices. It initializes fixed 44.1 kHz 16-bit stereo PCM, implements software monitor volume acquisition, optional capture-source selection, device setup commands, and LED class devices for models with red/green LEDs.

## Important APIs, Types, And Functions
The private type is `struct usb_line6_toneport`, embedding `struct usb_line6` and storing `source`, `serial_number`, `firmware_version`, `type`, and two `toneport_led` instances. The USB entry point is `toneport_probe()`. Setup flows through `toneport_init()`, `toneport_setup()`, `toneport_startup()`, and optional PM `toneport_reset_resume()`. User-facing controls are `toneport_control_monitor`, `toneport_control_source`, and LED class callbacks.

## Control Flow And State
Probe delegates to `line6_probe()` with a property row. `toneport_init()` records the model type, installs disconnect/startup hooks, initializes PCM, adds the monitor mixer control, conditionally adds the enumerated `PCM Capture Source` control, reads serial/firmware bytes, registers LEDs when supported, performs setup, and registers the ALSA card.

`toneport_setup()` writes the current host time to device address `0x80c6`, sends an enable command, applies source selection for UX models, updates LEDs for GuitarPort/TonePort GX, and schedules delayed startup. `toneport_startup()` acquires the monitor stream. The monitor mixer stores its value in `line6pcm->volume_monitor`; nonzero values acquire `LINE6_STREAM_MONITOR`, zero releases it. Source selection maps enum values to fixed command words and sends them via a vendor control request. LED brightness changes send a combined red/green command.

## State And Persistence
State is volatile in the driver except any settings the device firmware retains. The source selector, firmware byte, serial number, LED brightness, and monitor volume are cached in memory. LED registration state prevents unregistering unregistered class devices.

## Dependencies And Integration Points
The file integrates ALSA PCM/control APIs, the LED subsystem, USB vendor control messages, Line 6 PCM acquisition/release, common Line 6 probe/disconnect/PM hooks, and device property tables. It depends on `playback.c` for software monitoring because these devices lack hardware monitoring capability bits.

## Risks And Edge Cases
`toneport_send_cmd()` failures are often ignored by callers, so source or LED state can be cached as changed even when the USB command failed. The 32-bit timestamp comment notes overflow in year 2106. LED support is model-gated and must be extended manually for new devices. Monitor acquisition failure rolls the monitor volume back to zero, but source/LED paths do not similarly roll back.

## Test Signals
Coverage should include monitor volume transitions and stream acquisition/release, source enum bounds and command encoding, LED registration/unregistration and brightness commands, reset-resume setup replay, device ID/property consistency, card registration, and PCM constraints for 44.1 kHz signed 16-bit stereo.
