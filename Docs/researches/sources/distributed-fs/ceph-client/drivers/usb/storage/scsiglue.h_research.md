<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.h -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.h

## Purpose

`scsiglue.h` declares the SCSI glue helpers exported by `scsiglue.c` for usb-storage core and subdrivers.

## Important APIs, Types, and Functions

It declares `usb_stor_report_device_reset()`, `usb_stor_report_bus_reset()`, `usb_stor_host_template_init()`, and the shared fixed sense buffer `usb_stor_sense_invalidCDB`.

## Control Flow

The header has no executable flow. Its functions are called when subdrivers need the default host template or when transport/protocol code must notify the SCSI midlayer about reset events.

## State and Persistence Behavior

It defines no state, but exposes `usb_stor_sense_invalidCDB`, a static invalid-field-in-CDB sense payload used by callers that need to fail unsupported commands predictably.

## Dependencies and Integration Points

The declarations reference `struct us_data` and `struct scsi_host_template`, supplied by the including usb-storage/SCSI headers. It is included by generic protocol code and many device-specific subdrivers.

## Risks and Test Signals

Risk is limited to ABI/prototype drift and misuse of reset-reporting lock preconditions. Build coverage should catch declaration mismatches; runtime tests should ensure reset reports are called with the lock expectations documented in `scsiglue.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/scsiglue.h -->
