# sources/distributed-fs/ceph-client/drivers/hid/hid-letsketch.c

## Purpose

`hid-letsketch.c` supports the LetSketch/VSON WP9620N drawing tablet family by switching the USB device into a vendor raw-report mode and exposing clean Linux input devices for the pen tablet and pad buttons. Without this driver, only part of the active area works and buttons are hardwired to keyboard or mouse shortcuts.

## Important APIs, Types, And Functions

`struct letsketch_data` stores the HID device, two input devices, and an in-range timer. `letsketch_probe()` owns the USB-only raw-mode handshake and device registration. `letsketch_setup_input_tablet()` registers the absolute pen device with `ABS_X`, `ABS_Y`, `ABS_PRESSURE`, `BTN_TOOL_PEN`, `BTN_TOUCH`, and stylus buttons. `letsketch_setup_input_tablet_pad()` registers a pad input device with five `BTN_0`-based buttons and dummy ABS axes for udev/libwacom compatibility. `letsketch_raw_event()` decodes 12-byte report id 8 packets. `letsketch_get_string()` wraps the fragile USB string-descriptor reads needed for mode switching.

## Control Flow

Probe rejects non-USB HID devices and all interfaces except interface 0. It then performs the vendor handshake by slowly reading string descriptors `0xc8..0xca`, descriptors `1..250`, descriptor `0x64`, and `0xc8` again, retrying each read up to five times with `usleep_range()` because the firmware fails when polled too quickly. After a final delay, HID parsing runs, drvdata is allocated, the pen and pad input devices are registered, and HID hardware starts with `HID_CONNECT_HIDRAW` rather than normal hid-input. Input device open/close calls directly open/close HID hardware.

Raw reports with header nibble `0x80` update the pen device: in-range is asserted, touch/stylus bits are decoded from `raw_data[1]`, little-endian X/Y/pressure fields are reported, and a 100 ms timer is armed to synthesize out-of-range because firmware never sends an explicit leave event. Header nibble `0xe0` updates the pad device by treating `raw_data[4]` values 1 through 5 as mutually exclusive button presses. Unknown headers are warned and ignored.

## State And Persistence Behavior

State is minimal and devm-managed. The tablet raw-mode state is a firmware mode established by USB descriptor reads during probe and lasts until reset/unplug. Input state is transient event state plus the timer-maintained `BTN_TOOL_PEN` in-range bit. The driver does not expose sysfs or persistent configuration.

## Dependencies And Integration Points

The driver depends on USB HID, `usb_string()`, input core, timers, `get_unaligned_le16()`, and device ids from `hid-ids.h`. It bypasses ordinary parsed HID input by using only hidraw plus custom input devices, which is necessary because the useful data format is vendor-specific and the other USB interfaces become disabled after raw mode is enabled.

## Risks And Test Signals

Risks include the unusual descriptor-read handshake, long probe latency from 250 string reads, strict fixed 12-byte raw packet expectations, no explicit remove callback for deleting the timer, and unknown behavior on rebranded devices with slightly different report formats. Test with interface filtering, successful raw-mode transition, libinput/libwacom detection, full active-area coordinates, pressure range to 8192, both stylus buttons, five pad buttons, in-range timeout behavior when the pen leaves, and suspend/unplug races around the timer.
