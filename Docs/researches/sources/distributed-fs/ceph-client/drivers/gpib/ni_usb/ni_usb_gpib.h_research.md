# sources/distributed-fs/ceph-client/drivers/gpib/ni_usb/ni_usb_gpib.h

## Purpose
`ni_usb_gpib.h` is the private protocol and state header for the NI USB GPIB driver. It declares USB IDs, endpoint assignments, adapter subdevice IDs, per-board private state, status/register wire-format structures, NI USB bulk command IDs, error codes, vendor control requests, and small helpers for encoding bulk register messages.

## Important APIs, types, and functions
Important types are `struct ni_usb_priv`, `struct ni_usb_urb_ctx`, `struct ni_usb_status_block`, and `struct ni_usb_register`. Enums define supported USB product IDs, USB-B/HS/HS+ endpoint addresses, NI USB subdevice selectors, bulk block IDs such as `NIUSB_REG_WRITE_ID` and `NIUSB_IBRD_DATA_ID`, adapter error codes such as `NIUSB_TIMEOUT_ERROR`, and vendor requests such as `NI_USB_STOP_REQUEST` and `NI_USB_WAIT_REQUEST`. Inline helpers include `nec7210_to_tnt4882_offset()`, `ni_usb_bulk_termination()`, `ni_usb_bulk_register_write_header()`, `ni_usb_bulk_register_write()`, `ni_usb_bulk_register_read_header()`, and `ni_usb_bulk_register_read()`.

## Control flow
The header has no standalone execution, but its helper functions construct the byte streams used by `ni_usb_gpib.c`: bulk operations append command IDs, register triplets, padding, and termination blocks, while control requests use the request constants to stop I/O, wait for status, poll readiness, read serial numbers, and run HS+ extra initialization.

## State and persistence behavior
`struct ni_usb_priv` is the central runtime state object. It tracks endpoint selection, EOS mode/character, monitor bits, URB ownership, transfer locks, timer state, product ID, and REN state. `struct ni_usb_status_block` and `struct ni_usb_register` describe transient wire-format data decoded from or encoded into USB transfers. No persistent storage is represented.

## Dependencies and integration points
The header depends on Linux mutex, semaphore, USB, timer, and Linux-GPIB private definitions. It integrates the USB adapter protocol with NEC7210/TNT4882 register addressing by providing `nec7210_to_tnt4882_offset()` and subdevice IDs consumed by register-write sequences in the C file.

## Risks and edge cases
The structs and enum values are protocol contracts: changing IDs, endpoint numbers, byte ordering, or helper output lengths would break adapter communication. `ni_usb_status_block.count` is parsed from a two's-complement count in the C file, so callers must not treat the raw fields as native device-neutral data. The shared `bulk_urb` and `context` fields imply only one bulk transfer at a time.

## Test signals
Compile coverage catches missing constants, but meaningful validation comes from USB protocol tests that verify register-write/read framing, termination blocks, endpoint selection per product ID, timeout-code handling, and correct status/error parsing in the C driver.
