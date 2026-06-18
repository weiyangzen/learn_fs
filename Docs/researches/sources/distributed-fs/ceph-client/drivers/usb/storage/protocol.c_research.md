<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.c

## Purpose

`protocol.c` provides generic usb-storage protocol adapters and transfer-buffer utilities. It normalizes SCSI CDBs for devices that require 12-byte commands, delegates protocol handling to the selected transport, and offers scatterlist copy helpers used by many device-specific subdrivers.

## Important APIs, Types, and Functions

The exported protocol entry points are `usb_stor_pad12_command()`, `usb_stor_ufi_command()`, and `usb_stor_transparent_scsi_command()`. The exported buffer helpers are `usb_stor_access_xfer_buf()` and `usb_stor_set_xfer_buf()`. The direction enum comes from `protocol.h`.

## Control Flow

`usb_stor_pad12_command()` extends CDBs shorter than 12 bytes with zeros before calling `usb_stor_invoke_transport()`. `usb_stor_ufi_command()` also forces `cmd_len` to exactly 12 and adjusts INQUIRY, MODE_SENSE_10, and REQUEST_SENSE allocation lengths to values UFI devices tolerate. `usb_stor_transparent_scsi_command()` simply delegates. `usb_stor_access_xfer_buf()` starts a scatterlist mapping iterator, skips to the caller-provided offset, copies bytes to or from mapped segments, and updates the scatterlist pointer and offset for incremental callers. `usb_stor_set_xfer_buf()` copies a local response into the SCSI buffer and sets residual if the copy is short.

## State and Persistence Behavior

There is no persistent state. The functions mutate the active `scsi_cmnd`: CDB padding, command length, selected allocation-length bytes, transfer buffer contents, and residual count.

## Dependencies and Integration Points

The file depends on Linux highmem scatterlist mapping, SCSI command APIs, usb-storage transport invocation, and exported GPL symbols for subdrivers. It is a central integration point for fake INQUIRY, MODE_SENSE, READ_CAPACITY, and media-map drivers that need to copy data between bounce buffers and SCSI scatterlists.

## Risks and Test Signals

Risks include incorrect offset advancement in multi-segment scatterlists, missing `sg_miter_stop()` on early skip failure, assuming `scsi_cmnd.cmnd` has at least 12 bytes, and UFI allocation-length rewrites that may surprise upper layers. Tests should cover single and multi-segment buffers, unaligned offsets, partial copies/residuals, empty scatterlists, UFI command rewriting, and transparent delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/protocol.c -->
