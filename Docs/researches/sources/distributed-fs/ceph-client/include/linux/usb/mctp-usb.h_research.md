# `sources/distributed-fs/ceph-client/include/linux/usb/mctp-usb.h`

## Purpose

`mctp-usb.h` defines common protocol constants for the DMTF MCTP-over-USB transport binding. It can be shared by host and gadget implementations.

## Important APIs, Types, and Constants

- `struct mctp_usb_hdr` is the packed transport header with big-endian DMTF ID, reserved byte, and payload length.
- `MCTP_USB_XFER_SIZE` fixes USB transfer size at 512 bytes.
- `MCTP_USB_BTU`, `MCTP_USB_MTU_MIN`, and `MCTP_USB_MTU_MAX` define transport payload limits.
- `MCTP_USB_DMTF_ID` identifies the DMTF binding.

## Control Flow and Lifetimes

Transmitters prepend `mctp_usb_hdr`, set the DMTF ID and length, and send within the transfer/MTU limits. Receivers validate ID, reserved fields, and length before handing payload to the MCTP core. This header does not implement flow control.

## State and Persistence Behavior

Only wire-format state is defined. Runtime packet queues, endpoint state, and MCTP network state live in host/gadget drivers.

## Dependencies and Integration Points

It depends on kernel fixed-width types and endian annotations. It integrates USB transport drivers with the MCTP stack and DMTF DSP0283 framing.

## Risks and Edge Cases

The `len` field is one byte, so maximum MTU must account for header size and cannot exceed `U8_MAX - sizeof(header)`. Consumers must validate big-endian ID and avoid trusting malformed lengths. Reserved-byte handling should follow the binding specification.

## Test Signals

Test host/gadget loopback, minimum and maximum MTU packets, malformed IDs, oversized lengths, short transfers, endian conversion, and MCTP stack registration over USB endpoints.
