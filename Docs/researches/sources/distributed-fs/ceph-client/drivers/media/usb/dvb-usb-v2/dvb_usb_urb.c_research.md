# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/dvb_usb_urb.c

Purpose: This file provides generic bulk-control read/write helpers for dvb-usb-v2 devices that use bulk endpoints for command transport. It is separate from MPEG TS URB streaming; the helpers send small control commands through driver-specified bulk endpoints.

Important APIs and functions: `dvb_usb_v2_generic_io()` validates buffers and endpoint properties, logs outgoing bytes, sends a bulk message to `generic_bulk_ctrl_endpoint`, checks exact write length, optionally sleeps for `generic_bulk_ctrl_delay`, receives a reply from `generic_bulk_ctrl_endpoint_response`, logs returned bytes, and returns the USB status. Exported wrappers are `dvb_usbv2_generic_rw()`, `dvb_usbv2_generic_write()`, `dvb_usbv2_generic_rw_locked()`, and `dvb_usbv2_generic_write_locked()`.

Control flow: Drivers call the unlocked wrappers when they want this file to take `d->usb_mutex`. Drivers that already hold the mutex call the `_locked` variants, as seen in AF9035, Anysee, and DVBSky transports. The helper always performs the write phase and performs the read phase only when both `rbuf` and `rlen` are nonzero.

State and persistence: No persistent state is used. Runtime behavior depends on endpoint numbers and delay stored in `d->props`, the USB device pointer, and the caller's buffers. The wrappers serialize with `d->usb_mutex` when requested.

Dependencies and integration points: It depends on `dvb_usb_common.h`, Linux USB bulk messaging, and the property fields defined in `dvb_usb.h`. Device-specific protocols provide command formatting and reply validation above this layer.

Risks: Endpoint properties are mandatory even for write-only operations because validation checks both send and response endpoints. The read phase does not check `actual_length` against `rlen`, so a short reply can be treated as success by this helper unless the caller validates content. The helper returns read USB errors but not a short-read error. Calling `_locked` variants without holding `d->usb_mutex` is a driver bug the function cannot detect.

Test signals: Drivers using generic bulk control should show correct debug traces, no write-length mismatch logs, successful read replies after optional delay, and no races when concurrent I2C/RC/streaming control paths share the same mutex. Fault injection with disconnected endpoints should return USB errors to callers.
