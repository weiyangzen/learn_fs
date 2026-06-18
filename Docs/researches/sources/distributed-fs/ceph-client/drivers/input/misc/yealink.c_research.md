# sources/distributed-fs/ceph-client/drivers/input/misc/yealink.c

## Purpose
`yealink.c` drives the Yealink USB-P1K VoIP phone. It registers keypad input events, manages the phone LCD/LED/dialtone/ringtone through sysfs, and runs an asynchronous USB control/interrupt polling loop over Yealink control packets.

## Important APIs, Types, and Functions
`struct yld_status` mirrors device-visible LCD/icon/sound/key state. `struct yealink_dev` owns USB/input devices, interrupt and control URBs, coherent packet buffers, LCD map cache, sysfs mutex, shutdown flag, and master/copy status. LCD helpers include `setChar()`, `show_line*()`, `store_line*()`, icon handlers, and ringtone upload. Key helpers include `map_p1k_to_key()` and `report_key()`. USB flow uses `yealink_cmd()`, `yealink_set_ringtone()`, `yealink_do_idle_tasks()`, `urb_irq_callback()`, and `urb_ctl_callback()`. Probe/disconnect are `usb_probe()` and `usb_disconnect()`.

## Control Flow
USB probe validates an interrupt-in endpoint, allocates input and DMA buffers/URBs/control request, configures interrupt and control URBs, registers input keys for all mapped phone scancodes, stores interface data, clears LCD/icons, and writes the driver version to line 3. Input open forces a full status refresh, uploads the default ringtone, sends `CMD_INIT`, and starts the control/interrupt state machine. Control completion either submits the interrupt URB for key responses or asks `yealink_do_idle_tasks()` for the next LCD/icon/sound update. Interrupt completion records key-number changes or maps scancodes to Linux keys, then continues the state machine. Sysfs writes update `master` state under `sysfs_mutex`; idle tasks copy differences to the device.

## State and Persistence Behavior
`master` is the desired state for LCD bytes, LED, dialtone, ringtone, and key request; `copy` is the last sent state. `lcdMap[]` tracks display characters/icons. `key_code` records the currently pressed key so new scancodes release the old key first. USB URBs persist while the input device is open; `shutdown` prevents callbacks from resubmitting during close. Device LCD/ringtone/LED state persists on hardware until updated or disconnected.

## Dependencies and Integration Points
The driver depends on USB HID-interface matching for vendor/product `0x6993:0xb001`, input core, USB coherent DMA/control/interrupt URBs, seven-segment mapping, and the local Yealink packet definitions. Sysfs attributes under the USB interface expose line display, icon control, character map, and ringtone upload.

## Risks and Edge Cases
Sysfs writes update desired state but do not directly start URBs when the input device is closed, so changes may not reach hardware until open. `yealink_set_ringtone()` ignores command errors and sysfs ringtone passes a `const char *` as mutable `u8 *`. The async USB state machine has shared `ctl_data` and `master/copy` state with only sysfs-side mutexing; callbacks are not serialized by that mutex. `get_icons()` starts output at index 1, leaving `buf[0]` uninitialized. Disconnect cleanup unregisters input before clearing interface data and relies on input close killing URBs.

## Test Signals
Test probe with endpoint size validation, input open/close URB sequencing, keypad scancode mapping including shifted `#`, LCD line writes/reads, icon show/hide, ringtone upload, LED/dialtone/ringtone state updates, disconnect while URBs are active, sysfs writes while closed/open, and USB submit/control error injection.
