# `sources/distributed-fs/ceph-client/include/linux/usb/irda.h`

## Purpose

`irda.h` defines USB IrDA bridge class constants, class-specific requests, class descriptor layout, capability bitmasks, and inbound/outbound data headers. It is a protocol binding header for USB-to-IrDA bridge drivers.

## Important APIs, Types, and Constants

- Class metadata includes `USB_SUBCLASS_IRDA`, class-specific request IDs, and descriptor type `USB_DT_CS_IRDA`.
- Capability masks describe supported data sizes, window sizes, minimum turnaround times, baud rates, and additional BOF counts.
- `struct usb_irda_cs_descriptor` is the packed class-specific descriptor with spec revision, capability bitmaps, rate sniffing, and max unicast list size.
- Data-format constants define media-busy status, link-speed encodings, and outbound extra-BOF encodings.
- `struct usb_irda_inbound_header` and `struct usb_irda_outbound_header` wrap per-packet IrDA status/change bytes.

## Control Flow and Lifetimes

During probe, a driver parses the class-specific descriptor and negotiates link capabilities with class requests. During data I/O, inbound packets carry `bmStatus`; outbound packets carry `bmChange` to request speed or BOF changes. Lifetimes follow USB interface binding and URB buffers.

## State and Persistence Behavior

The header defines wire-format state, not persistent kernel state. Device capabilities persist for the bound device session after descriptor parsing; negotiated link speed and BOF changes are runtime protocol state.

## Dependencies and Integration Points

It depends on packed USB integer types and integrates USB application-specific class devices with IrDA stack drivers. The little-endian fields must be converted by consumers.

## Risks and Edge Cases

Packed descriptor parsing must validate lengths before dereference. Reserved speed/BOF values must be rejected or ignored. Media-busy and rate-change status can race with queued packets. Bitmaps are capability sets, not scalar values, so choosing an unsupported mode breaks interoperability.

## Test Signals

Test descriptor parsing with valid and malformed descriptors, class request handling, speed change paths, media-busy reporting, all supported baud masks, short packet handling, endian conversion, and disconnect during active IrDA traffic.
