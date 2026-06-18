# sources/distributed-fs/ceph-client/drivers/input/tablet/acecad.c

## Purpose
`acecad.c` is a USB input driver for Acecad Flair and Acecad 302 tablets. It decodes fixed 8-byte interrupt reports into pen proximity, coordinates, pressure, touch, and stylus button events.

## Important APIs, types, and functions
`struct usb_acecad` stores device strings, USB interface, input device, interrupt URB, coherent DMA buffer, and DMA address. Core functions are `usb_acecad_probe()`, `usb_acecad_irq()`, `usb_acecad_open()`, `usb_acecad_close()`, and `usb_acecad_disconnect()`. The USB ID table distinguishes Flair and 302 by `.driver_info`.

## Control flow
Probe requires exactly one interrupt-in endpoint, allocates driver/input objects, an 8-byte coherent buffer, and a URB. It builds the input device name/phys path, sets key and absolute capabilities, applies model-specific X/Y/pressure ranges, fills the interrupt URB, and registers the input device. Opening submits the URB; each successful interrupt decodes report bits, emits input events, syncs, and resubmits. Close kills the URB; disconnect unregisters input and frees USB resources.

## State and persistence
The driver stores only per-device runtime pointers and the DMA report buffer. Input state is maintained by the input core. No tablet settings are persisted or programmed by the driver.

## Dependencies and integration points
It depends on the USB input helper APIs, interrupt endpoints, coherent DMA buffers, input absolute/key events, and USB module matching for vendor `0x0460` device IDs `0x0004` and `0x0008`.

## Risks
Probe uses `usb_maxpacket()` but always allocates 8 bytes; the URB transfer length is clamped to 8, so endpoint descriptors with smaller packets are tolerated but malformed packets may result in stale fields. Name construction can be empty until the model fallback path. Disconnect relies on input unregister closing the device and killing the URB through `close()` when open.

## Test signals
Test both USB IDs, endpoint rejection paths, input capability ranges per model, packet decoding for proximity out and in-range events, URB resubmission after transient errors, open/close behavior, and disconnect while the input node is open.
