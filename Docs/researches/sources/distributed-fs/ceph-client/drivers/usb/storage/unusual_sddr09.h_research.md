# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_sddr09.h

## Purpose

`unusual_sddr09.h` describes SanDisk/ImageMate SDDR09 and related readers that need the EUSB SDDR09 or DPCM USB protocol paths.

## Important APIs, Types, and Functions

The file contains six `UNUSUAL_DEV()` rows. Some entries select `USB_PR_EUSB_SDDR09` with `usb_stor_sddr09_init`; others select `USB_PR_DPCM_USB` with either no initializer or `usb_stor_sddr09_dpcm_init`. Rows use `USB_SC_SCSI` and no extra flags.

## Control Flow

The rows are expanded into ignore or specialized subdriver tables. Matching hardware is routed to the SDDR09/DPCM transport and optional initializer before SCSI scanning.

## State and Persistence Behavior

There is no state in the header. Probe-time metadata selects protocol and initializer; runtime state belongs to the SDDR09 transport implementation.

## Dependencies and Integration Points

It depends on SDDR09 and DPCM protocol constants plus `usb_stor_sddr09_init` and `usb_stor_sddr09_dpcm_init`. It integrates with usb-storage's protocol handler selection and specialized media-reader transports.

## Risks and Edge Cases

The table mixes exact and broad revision ranges. Incorrect revision coverage can either miss special handling or force it on unrelated firmware. DPCM devices interact with autosense policy in `transport.c`, so protocol selection must be correct.

## Test Signals

Build SDDR09 support, attach represented readers, verify initializer selection by product/revision, test card enumeration and I/O, and exercise reset/error paths for DPCM and EUSB variants.
