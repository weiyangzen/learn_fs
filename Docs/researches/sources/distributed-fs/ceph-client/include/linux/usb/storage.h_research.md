# `sources/distributed-fs/ceph-client/include/linux/usb/storage.h`

## Purpose

`storage.h` defines USB mass-storage subclass/protocol constants and Bulk-Only Transport command/status wrapper layouts. It is shared by USB storage drivers and related transport code.

## Important APIs, Types, and Constants

- Subclass constants cover RBC, 8020 CD-ROM, QIC, UFI, 8070 removable, transparent SCSI, lockable, ISD200, Cypress ATACB, and use-device value.
- Protocol constants cover CBI, CB, bulk-only, UAS, USBAT, SDDR09/55, DPCM, Freecom, Datafab, Jumpshot, Alauda, Karma, and use-device value.
- `struct bulk_cb_wrap` is the packed command block wrapper with signature, tag, transfer length, flags, LUN, CDB length, and command block bytes.
- `struct bulk_cs_wrap` is the packed command status wrapper with signature, tag, residue, and status.
- Constants define wrapper lengths/signatures, direction flags, status values, bulk reset and max-LUN requests, and max-LUN limit.

## Control Flow and Lifetimes

For bulk-only transport, the driver sends a CBW over bulk OUT, transfers data in the indicated direction and length, then reads a CSW over bulk IN and validates signature/tag/status/residue. Reset and get-max-LUN class requests manage error recovery and LUN discovery.

## State and Persistence Behavior

CBW/CSW structs are transient wire buffers. Device subclass/protocol selection persists for the USB interface lifetime. SCSI and transport state live in usb-storage/UAS code.

## Dependencies and Integration Points

It integrates USB interface descriptor parsing with SCSI, usb-storage, UAS, and transport-specific drivers. It depends on packed fixed-width USB types.

## Risks and Edge Cases

CBW/CSW validation must reject bad signatures, wrong tags, invalid statuses, and impossible residue. Max LUN is four bits with upper limit `0x0f`. Some devices misreport subclass/protocol and need unusual-device handling outside this header.

## Test Signals

Run usb-storage BOT enumeration, SCSI read/write, reset recovery, max-LUN queries, malformed CSW injection, short transfers, UAS protocol selection, and devices across listed subclasses/protocols.
