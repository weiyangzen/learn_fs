# sources/distributed-fs/ceph-client/drivers/hid/hid-elan.c

## Purpose
`hid-elan.c` is a specialized HID driver for ELAN touchpads in selected USB and I2C devices. It suppresses the generic HID touch reports, queries device geometry, creates a custom multitouch input device, decodes ELAN USB/I2C report formats, enables multitouch mode, and optionally registers a mute LED controlled through HID feature reports.

## Important APIs, Types, And Functions
`struct elan_drvdata` stores the custom input device, a saved first-finger USB report, optional LED class device and state, maximum X/Y, and X/Y resolution. `is_not_elan_touchpad()` filters USB composite devices to interface 1. `elan_input_mapping()` returns `-1` for ELAN touch report IDs so generic hid-input will not map them. `elan_get_device_param()` and `elan_get_device_params()` issue feature report `0x0d` requests to read max X, max Y, and resolution. `elan_input_configured()` creates and registers the custom `Elan Touchpad` input device with five multitouch slots. `elan_report_mt_slot()`, `elan_usb_report_input()`, and `elan_i2c_report_input()` decode packet formats and emit input events. `elan_raw_event()` consumes recognized reports. `elan_start_multitouch()` sends the feature report that enables multitouch and disables mouse emulation. `elan_mute_led_set_brigtness()` and `elan_init_mute_led()` integrate with the LED subsystem.

## Control Flow
Probe allocates driver data, parses the HID descriptor, and starts HID. Non-touchpad USB interfaces are left to generic behavior. For the touchpad interface, `input_configured` must already have created `drvdata->input`; otherwise probe fails with `-ENAVAIL`. Probe then enables multitouch mode and registers the mute LED when the matched ID has `ELAN_HAS_LED`.

For USB reports, single-finger reports update all slots directly from bits in byte 2. Multitouch USB reports arrive as a first-finger report followed by a second-finger report; the first report is saved in `prev_report`, and the second report combines saved and current data before syncing the frame. For I2C report `0x5d`, one 32-byte packet carries up to five finger records; the decoder advances through packed five-byte finger records only for active touch bits. Coordinates are converted from packed 12-bit fields, Y is inverted against `max_y`, pressure is byte 4 of each finger record, and BTN_LEFT comes from the low bit in the report status byte.

## State And Persistence
Runtime state includes max dimensions/resolution queried during input configuration, saved USB first-finger report for two-packet multitouch, current LED state, and the input device. The driver sends feature reports to put hardware into multitouch mode and to set LED brightness, but it does not persist configuration across disconnects.

## Dependencies And Integration Points
The driver depends on HID core, USB interface inspection, HID-over-I2C matching, Linux multitouch input helpers, and the LED class subsystem. It integrates as a custom touchpad input device with `INPUT_PROP_BUTTONPAD`, `BTN_LEFT`, `ABS_MT_POSITION_X/Y`, and `ABS_MT_PRESSURE`, plus an `elan:red:mute` LED with `audio-mute` trigger on selected HP devices.

## Risks
The driver is tightly coupled to specific report IDs and packet lengths. USB two-finger handling depends on receiving first and second reports in order; missing or reordered packets can drop a frame. `elan_get_device_param()` treats any short positive transfer as an error but returns that positive value directly, which callers treat as failure but logs can be less normalized. The LED setter name contains a typo in `brigtness`, harmless for C linkage but worth noting. Non-touchpad USB interface filtering is essential; incorrect interface numbering could suppress or mis-handle unrelated HID functions.

## Test Signals
Test signals include successful custom input registration, correct max/resolution values from feature reports, five-slot MT tracking in `evtest`, BTN_LEFT clickpad behavior, Y-axis orientation, USB single/two-finger ordering, I2C five-finger packet decoding, multitouch-mode feature report success, LED class device registration on HP IDs, LED set behavior including disconnect returning `-ENODEV`, and composite-device interfaces outside interface 1 remaining unaffected.
