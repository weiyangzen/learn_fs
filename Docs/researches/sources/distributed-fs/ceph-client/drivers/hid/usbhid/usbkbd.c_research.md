# sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbkbd.c

## Purpose

`usbkbd.c` implements a simple USB HID Boot Protocol keyboard driver. It handles keyboards matching HID class, boot subclass, keyboard protocol by consuming fixed 8-byte boot reports and exposing a Linux input keyboard with key, LED, and repeat capabilities.

## Important APIs, Types, And Data

- `usb_kbd_keycode[256]` maps HID boot keyboard usage IDs to Linux input key codes.
- `struct usb_kbd` owns the input device, USB device, old and new 8-byte reports, interrupt IN URB, LED control URB, control request, coherent DMA buffers, device name/path, LED spinlock, and LED URB in-flight flag.
- `usb_kbd_irq()` is the interrupt completion handler for key reports.
- `usb_kbd_event()` handles `EV_LED` changes from input core and submits a class SET_REPORT control URB.
- `usb_kbd_led()` is the LED URB completion handler and resubmits if LED state changed while a prior request was in flight.
- `usb_kbd_open()`, `usb_kbd_close()`, `usb_kbd_probe()`, and `usb_kbd_disconnect()` implement lifecycle.

## Control Flow

Probe validates one interrupt IN endpoint, allocates state and an input device, allocates URBs and coherent DMA buffers, builds the display name and physical path, configures input ID/capabilities/key bits/LED bits, assigns input callbacks, fills the interrupt and LED control URBs, registers the input device, stores interface data, and enables wakeup.

When userspace opens the input device, `usb_kbd_open()` submits the interrupt URB. On each successful completion, `usb_kbd_irq()` reports modifier bits from byte 0, compares old key slots 2..7 against new slots to emit releases, compares new slots against old to emit presses, calls `input_sync()`, copies new to old, and resubmits the URB.

LED changes arrive through `usb_kbd_event()`. It computes the boot keyboard LED byte, serializes with `leds_lock`, skips submission if an identical state is current or if a LED URB is in flight, writes the coherent LED byte, and submits the control URB. The completion handler clears `led_urb_submitted` when current, or writes the newer requested byte and resubmits.

Disconnect clears interface data, kills the interrupt URB, unregisters the input device, kills the LED URB, frees URBs/buffers/control request, and frees driver state.

## State And Persistence Behavior

All state is per attached USB interface and volatile. `old[8]` stores the previous boot report to synthesize key releases; `new` is the DMA buffer for the current interrupt report. LED state is split into `newleds` as desired state and `*leds` as the last submitted payload. `led_urb_submitted` prevents concurrent control URBs and allows coalescing.

## Dependencies And Integration Points

- Depends on USB core APIs for interface matching, endpoint inspection, interrupt/control URBs, coherent DMA, and wakeup.
- Integrates with input core by registering an `input_dev` and reporting `EV_KEY`, `EV_LED`, and `EV_REP`.
- Matches `USB_INTERFACE_INFO(USB_INTERFACE_CLASS_HID, USB_INTERFACE_SUBCLASS_BOOT, USB_INTERFACE_PROTOCOL_KEYBOARD)`.

## Risks And Edge Cases

- Boot protocol supports only six simultaneous non-modifier key slots. Rollover/error codes 1..3 are ignored by the `> 3` checks.
- Interrupt URB error handling comments mention `-EPIPE` should clear halt, but default handling only resubmits.
- `usb_kbd_alloc_mem()` returns `-1` on partial allocation failure and relies on later cleanup to tolerate NULL fields.
- LED updates are coalesced, not queued. Intermediate LED states can be skipped.

## Test Signals

- Attach a boot-protocol keyboard and verify modifier keys, ordinary key press/release, six-key rollover limits, LED changes, and repeat events through evdev.
- Exercise open/close repeatedly and confirm URBs are submitted/killed without leaks.
- Toggle LEDs rapidly to verify `newleds` coalescing and LED URB resubmission.
- Disconnect while the input device is open and while a LED URB is in flight to check teardown ordering.
