# sources/distributed-fs/ceph-client/drivers/usb/storage/unusual_sddr55.h

## Purpose

`unusual_sddr55.h` lists SDDR55-style readers that require the `USB_PR_SDDR55` transport.

## Important APIs, Types, and Functions

The file contributes four `UNUSUAL_DEV()` rows for SanDisk and related product IDs. They select `USB_SC_SCSI`, `USB_PR_SDDR55`, no initializer, and usually no extra flags.

## Control Flow

Macro expansion routes matching readers to the SDDR55 subdriver and prevents generic usb-storage from claiming them through the ignore table.

## State and Persistence Behavior

No state is stored. The table controls matching and transport choice; runtime media state belongs to the reader driver.

## Dependencies and Integration Points

It depends on `USB_PR_SDDR55` support and the usual macro inclusion mechanism. It integrates with usb-storage/libusual matching and SCSI block-device enumeration.

## Risks and Edge Cases

The rows are product/revision-specific. Firmware outside those ranges may be mishandled. Since no initializer is supplied, all special behavior must be in the selected transport.

## Test Signals

Compile SDDR55 support, verify the table expansion, attach matching readers, and test card detection, reads/writes, and error recovery.
