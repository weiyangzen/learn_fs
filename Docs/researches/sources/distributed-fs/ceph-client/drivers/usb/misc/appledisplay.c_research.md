# sources/distributed-fs/ceph-client/drivers/usb/misc/appledisplay.c

## Purpose
`appledisplay.c` is a USB HID-interface driver for Apple Cinema Displays. It registers a Linux backlight device, sends HID class control reports to get/set brightness, and listens to interrupt reports for display brightness buttons.

## Important APIs, Types, And Functions
`struct appledisplay` stores the USB device, interrupt URB, backlight device, interrupt/control buffers, delayed work, button state, and `sysfslock` mutex. Matching uses `APPLEDISPLAY_DEVICE()` entries for Apple vendor/product IDs with HID class and protocol 0. Key functions are `appledisplay_probe()`, `appledisplay_disconnect()`, `appledisplay_complete()`, `appledisplay_bl_update_status()`, `appledisplay_bl_get_brightness()`, and `appledisplay_work()`.

## Control Flow
Probe finds the first interrupt-in endpoint, allocates state, control buffer, interrupt URB, and coherent interrupt buffer, submits the URB, registers a backlight device named with an atomic display count, reads initial brightness through a HID GET_REPORT control transfer, stores brightness, and attaches interface data. The interrupt completion callback interprets report byte 1 as brightness-up/down/none, schedules delayed work while a button is pressed, and resubmits the interrupt URB. Work reads brightness and updates the backlight property, then reschedules every 125 ms while the button remains pressed. Backlight sysfs updates send HID SET_REPORT control transfers. Disconnect kills the URB, cancels work, unregisters backlight, and frees buffers.

## State And Persistence
State is per display interface and volatile. Brightness is stored in hardware and mirrored in `bd->props.brightness`. `button_pressed` drives polling while a hardware button is held. `count_displays` is a module-global atomic used only to generate unique names.

## Dependencies And Integration Points
The driver depends on USB core, HID request constants, interrupt URBs, coherent DMA buffer allocation, backlight class, delayed work, mutexes, and atomic counters. Userspace integrates through the standard backlight sysfs interface.

## Risks
The error path checks `if (!IS_ERR(pdata->bd))` even when `bd` may be NULL from zeroed allocation, which can call unregister on NULL depending on helper semantics. Probe submits the interrupt URB before backlight registration, and the callback has a comment about a window where no device is registered. Interrupt resubmission failures stop button monitoring. Brightness control serializes control messages with `sysfslock`, but disconnect must kill URB and cancel work before freeing. The driver assumes two-byte HID reports and uses fixed report IDs/values.

## Test Signals
Test probe with missing interrupt endpoint, allocation failures at each step, initial brightness GET_REPORT failure, sysfs brightness set/get, hardware brightness buttons causing delayed polling, disconnect while work is pending, URB shutdown statuses, and multiple displays generating unique backlight names.
