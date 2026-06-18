<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/jumpshot.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/jumpshot.c

## Purpose

`jumpshot.c` supports Lexar Jumpshot CompactFlash readers. These devices are USB-to-ATA readers that do not expose normal SCSI semantics, so the driver implements a private Control/Bulk transport that synthesizes common SCSI responses and translates block reads/writes to ATA-style bridge commands.

## Important APIs, Types, and Functions

`struct jumpshot_info` stores capacity, sector size, and pending sense data. `jumpshot_transport()` is the exported transport hook installed during probe. Low-level helpers include `jumpshot_bulk_read()`, `jumpshot_bulk_write()`, `jumpshot_get_status()`, `jumpshot_id_device()`, `jumpshot_read_data()`, `jumpshot_write_data()`, and `jumpshot_handle_mode_sense()`.

## Control Flow

Probe sets `us->transport_name`, `us->transport`, `us->transport_reset`, and `us->max_lun`. The transport lazily allocates `jumpshot_info`, fakes INQUIRY, identifies the ATA device on READ_CAPACITY, and returns the last LBA plus 512-byte sector size. READ_10, READ_12, WRITE_10, and WRITE_12 extract LBA and transfer count, chunk transfers through a maximum 64 KiB bounce buffer, and use `usb_stor_access_xfer_buf()` to move data to or from the SCSI scatterlist. TEST_UNIT_READY and START_STOP poll or re-identify media; MODE_SENSE returns small static pages; REQUEST_SENSE reports the driver's cached sense triplet.

## State and Persistence Behavior

The only persistent kernel state is `us->extra`, which caches sector size/count and the last sense values. Writes go directly to the CompactFlash media. START_STOP uses the first post-change identify failure as a media-change signal and updates sense state. No filesystem-backed persistence exists.

## Dependencies and Integration Points

The driver uses usb-storage core control and bulk helpers, SCSI opcode constants, `protocol.c` transfer-buffer helpers, `fill_inquiry_response()`, and `unusual_jumpshot.h` for device IDs. It integrates as a separate usb-storage module through `module_usb_stor_driver`.

## Risks and Test Signals

There is an apparent bug in `jumpshot_write_data()`: `waitcount` is initialized but never incremented inside the status polling loop, so failed status polling can spin indefinitely. Other risks include 28-bit LBA rejection, stale sense data, capacity underflow if IDENTIFY returns zero sectors, mode-page incompleteness, and reliance on a fixed 512-byte sector. Tests should exercise media insertion/removal, READ/WRITE chunking across 64 KiB boundaries, status-poll failures, sense after unsupported commands, and READ_CAPACITY after device errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/jumpshot.c -->
