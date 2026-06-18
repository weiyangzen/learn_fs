<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/karma.c -->
# sources/distributed-fs/ceph-client/drivers/usb/storage/karma.c

## Purpose

`karma.c` is the usb-storage subdriver for the Rio Karma music player. It wraps the normal Bulk-Only transport with proprietary Rio commands that switch the device into or out of storage mode around selected SCSI operations.

## Important APIs, Types, and Functions

`struct karma_data` records whether the device is in storage mode and owns a 512-byte receive buffer. `rio_karma_init()` allocates this state and enters storage mode. `rio_karma_send_command()` implements the Rio packet handshake using `RIOP` command frames, a static sequence number, repeated acknowledgments, and a 6-second timeout. `rio_karma_transport()` traps `READ_10` and `START_STOP`; `rio_karma_destructor()` frees the receive buffer.

## Control Flow

Probe installs `rio_karma_transport` and the Bulk reset path. Initialization sends `RIO_ENTER_STORAGE` and marks `in_storage`. During I/O, a READ_10 observed while out of storage mode sends `RIO_ENTER_STORAGE`, flips the state, then delegates to `usb_stor_Bulk_transport()`. START_STOP sends `RIO_LEAVE_STORAGE`, clears the state, and sends `RIO_RESET` instead of passing the command through. All other commands use normal Bulk transport.

## State and Persistence Behavior

The driver maintains only volatile per-device state in `us->extra`. The static command sequence byte is shared across devices, so it is process-global rather than per-device. Device-side storage-mode transitions are persistent in the attached player until changed or reset, but there is no host-side persistence.

## Dependencies and Integration Points

The file depends on usb-storage bulk transfer helpers, the generic SCSI glue module template, `unusual_karma.h`, jiffies timeout helpers, and SCSI opcode constants. It remains a narrow adapter over `usb_stor_Bulk_transport()`.

## Risks and Test Signals

Risks include the global static sequence counter, leaks on init failure after `recv` allocation if the core does not invoke the destructor for failed init, START_STOP always forcing leave/reset semantics, and timeout sensitivity in the custom handshake. Tests should cover repeated enter/leave cycles, READ_10 after START_STOP, concurrent devices if possible, timeout/error responses from bulk endpoints, and normal passthrough commands before and after storage-mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/storage/karma.c -->
