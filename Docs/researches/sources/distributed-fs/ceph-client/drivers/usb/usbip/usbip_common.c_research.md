# sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_common.c

## Purpose

`usbip_common.c` implements USB/IP core helpers shared by VHCI, host stub, and VUDC modules: debugging, reliable socket receive, URB/PDU packing, endian conversion, isochronous descriptor handling, and transfer-buffer receive.

## Important APIs, Types, and Functions

Exports include `usbip_debug_flag`, `dev_attr_usbip_debug`, `usbip_dump_urb()`, `usbip_dump_header()`, `usbip_recv()`, `usbip_pack_pdu()`, `usbip_header_correct_endian()`, `usbip_alloc_iso_desc_pdu()`, `usbip_recv_iso()`, `usbip_pad_iso()`, and `usbip_recv_xbuff()`. Internal flag mapping translates unstable kernel `URB_*` flags to stable UAPI `USBIP_URB_*` bits. `usbip_pack_ret_submit()` clamps response packet counts to the originally allocated URB descriptor count.

## Control Flow

Transmit paths pack URB fields into PDUs, map flags, append payload/iso descriptors, and endian-correct before send. Receive paths read exact socket payload sizes with `MSG_WAITALL`, endian-correct headers/descriptors, unpack URB fields, receive payload into flat buffers or SG entries, validate isochronous packet counts/length sums, and restore padding for isochronous transfers.

## State and Persistence Behavior

Only debug flag state persists at module runtime via module parameter/sysfs. Transfer helpers are stateless, except for mutating URB fields from wire data and raising USB/IP events on TCP/protocol failures.

## Dependencies and Integration Points

It depends on kernel sockets, USB core URBs, scatterlist helpers, byteorder helpers, module parameters, UAPI USB/IP definitions, and `usbip_event.c` for error propagation.

## Risks and Test Signals

Risks include accepting malicious remote lengths, integer overflow in descriptor sizing, partial socket reads, SG copy mismatch, isochronous OOB access, and kernel flag/UAPI drift. Test signals include endian round trips, all four PDU commands, IN/OUT payload receive, SG payload receive, invalid iso packet counts, mismatched iso total length, debug sysfs read/write, and error events by side.
