<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.h

## Purpose

`protocol.h` declares usb-storage protocol handlers and scatterlist transfer-buffer utilities implemented by `protocol.c`.

## Important APIs, Types, and Functions

It declares `usb_stor_pad12_command()`, `usb_stor_ufi_command()`, `usb_stor_transparent_scsi_command()`, `enum xfer_buf_dir` with `TO_XFER_BUF` and `FROM_XFER_BUF`, `usb_stor_access_xfer_buf()`, and `usb_stor_set_xfer_buf()`.

## Control Flow

The header has no runtime control flow. Its declarations let usb-storage core and subdrivers select protocol handlers or copy synthetic response data to and from `struct scsi_cmnd` buffers.

## State and Persistence Behavior

It declares no storage. Runtime mutations occur in `protocol.c` through the passed `scsi_cmnd`, scatterlist pointer, and offset.

## Dependencies and Integration Points

Callers need visible definitions for `struct scsi_cmnd`, `struct us_data`, and `struct scatterlist`. The header is used by generic usb-storage code and device-specific transports such as ISD200, Jumpshot, SDDR09, SDDR55, Shuttle USBAT, Realtek, and Sierra mode-switch paths.

## Risks and Test Signals

Risks are prototype drift, enum misuse that reverses copy direction, and include-order errors. Build coverage plus focused tests of `usb_stor_access_xfer_buf()` users are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.h -->
