# sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbmouse.c

## Purpose

`usbmouse.c` implements a simple USB HID Boot Protocol mouse driver. It consumes fixed boot mouse interrupt reports and exposes a Linux relative input mouse with left/right/middle/side/extra buttons, X/Y movement, and wheel movement.

## Important APIs, Types, And Data

- `struct usb_mouse` stores device name, physical path, USB device, input device, interrupt URB, coherent report data buffer, and DMA address.
- `usb_mouse_irq()` is the interrupt URB completion handler and translates report bytes to input events.
- `usb_mouse_open()` and `usb_mouse_close()` submit and kill the interrupt URB.
- `usb_mouse_probe()` validates the USB interface, allocates state/input/buffer/URB, configures input capabilities, fills the interrupt URB, and registers the input device.
- `usb_mouse_disconnect()` tears down the input device, URB, coherent buffer, and driver state.

## Control Flow

Probe requires exactly one interrupt IN endpoint. It computes the receive pipe and max packet size, allocates `struct usb_mouse`, an input device, an 8-byte coherent DMA buffer, and an interrupt URB. It builds the input name and physical path, sets input IDs and parent device, advertises mouse buttons and relative axes, assigns open/close callbacks, fills the interrupt URB with up to 8 bytes, registers the input device, and stores interface data.

Opening the input node submits the interrupt URB. On successful completion, `usb_mouse_irq()` interprets byte 0 as button bits, bytes 1 and 2 as signed X/Y deltas, and byte 3 as signed wheel delta, reports them through input core, calls `input_sync()`, and resubmits the URB. Unlink/shutdown statuses stop resubmission; other errors go to the resubmit path.

Disconnect clears interface data, kills the interrupt URB, unregisters the input device, frees the URB and coherent buffer, and frees state.

## State And Persistence Behavior

State is minimal and volatile. The current report is read from the coherent `data` buffer. There is no previous-report cache because relative movement and button states are directly reported every packet. No state persists after disconnect.

## Dependencies And Integration Points

- Depends on USB core for endpoint matching, interrupt URBs, coherent DMA, and interface data.
- Integrates with Linux input core as an `EV_KEY`/`EV_REL` device.
- Uses USB HID boot protocol assumptions rather than descriptor-derived report parsing.
- Matches HID class, boot subclass, mouse protocol.

## Risks And Edge Cases

- Boot mouse packets are assumed to have at least four bytes for wheel support. The URB length is `min(maxp, 8)`, but the IRQ handler always reads `data[3]`.
- Additional buttons/axes beyond the boot protocol are ignored.
- Interrupt `-EPIPE` handling is only commented; the driver resubmits by default and does not clear stalls itself.

## Test Signals

- Boot-protocol mouse attach should produce evdev button, X/Y, and wheel events.
- Repeated open/close and disconnect-while-open should show clean URB cancellation and no use-after-free.
- Tests with short/invalid endpoint max packet sizes would be valuable for the `data[3]` assumption.
- URB error injection should verify terminal statuses stop resubmission and transient errors attempt resubmission with logging.
